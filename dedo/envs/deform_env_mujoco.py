"""MuJoCo backend for DeformEnv (HangGarment slice).

First-cut port: low-dim observations, dual mocap-driven anchors via flexcomp
mesh + `connect` equality constraints. Reuses DEFORM_INFO/TASK_INFO from the
PyBullet implementation for task parameters and reward.

Scope limitations vs DeformEnv:
- Image observations / point clouds not implemented (low-dim only).
- Rigid scene entities (hangers, racks) not loaded; goal_pos from SCENE_INFO
  is still used for reward, but no visible obstacle is present.
- Procedural / robot / FoodPacking tasks not supported yet.
"""

import os
import time

import gymnasium as gym
import mujoco
import numpy as np

from ..utils.args import preset_override_util
from ..utils.task_info import DEFORM_INFO, SCENE_INFO, TASK_INFO

def _read_obj_vertices(path: str) -> np.ndarray:
    vs = []
    with open(path) as f:
        for line in f:
            if line.startswith('v '):
                vs.append([float(x) for x in line.split()[1:4]])
    return np.array(vs, dtype=np.float64)


def _clean_obj_for_flexcomp(src_path: str, dst_path: str) -> None:
    """Emit a geometry-only .obj that flexcomp can ingest cleanly.

    Two issues with the dedo .obj files:
      1. UV seams produce multiple verts at identical positions; MuJoCo's
         mesh importer merges them, which then makes faces referencing the
         seam verts degenerate ("repeated vertex in element").
      2. .mtl/vt/vn tokens are not needed by flexcomp.

    We keep the original vertex count and ordering so dedo's preset
    `deform_anchor_vertices` indices remain valid, and slightly perturb
    duplicate vert positions (epsilon along z) so MuJoCo does not merge
    them. Faces are triangulated and emitted with vertex-only indices.
    """
    verts = []
    faces = []
    with open(src_path) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == 'v':
                verts.append([float(x) for x in parts[1:4]])
            elif parts[0] == 'f':
                idxs = [int(tok.split('/')[0]) - 1 for tok in parts[1:]]
                faces.append(idxs)
    verts = np.array(verts, dtype=np.float64)

    # Group duplicates by rounded position; perturb all but the first in each
    # group so MuJoCo's mesh importer treats them as distinct.
    keys = [tuple(np.round(v, 6)) for v in verts]
    seen: dict[tuple, int] = {}
    eps = 1e-5
    for i, k in enumerate(keys):
        if k in seen:
            verts[i, 2] += eps * (i - seen[k])  # monotone offset per dup
        else:
            seen[k] = i

    tris = []
    for face in faces:
        for k in range(1, len(face) - 1):
            tri = (face[0], face[k], face[k + 1])
            if len(set(tri)) == 3:
                tris.append(tri)

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, 'w') as f:
        for v in verts:
            f.write(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
        for tri in tris:
            f.write(f'f {tri[0] + 1} {tri[1] + 1} {tri[2] + 1}\n')


def _rpy_to_mat(rpy):
    r, p, y = rpy
    cr, sr = np.cos(r), np.sin(r)
    cp, sp = np.cos(p), np.sin(p)
    cy, sy = np.cos(y), np.sin(y)
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def _mat_to_quat(R):
    # Returns (w, x, y, z)
    tr = R[0, 0] + R[1, 1] + R[2, 2]
    if tr > 0:
        s = 2.0 * np.sqrt(tr + 1.0)
        w = 0.25 * s
        x = (R[2, 1] - R[1, 2]) / s
        y = (R[0, 2] - R[2, 0]) / s
        z = (R[1, 0] - R[0, 1]) / s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
        w = (R[2, 1] - R[1, 2]) / s
        x = 0.25 * s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
        w = (R[0, 2] - R[2, 0]) / s
        x = (R[0, 1] + R[1, 0]) / s
        y = 0.25 * s
        z = (R[1, 2] + R[2, 1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
        w = (R[1, 0] - R[0, 1]) / s
        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s
        z = 0.25 * s
    return np.array([w, x, y, z])


def _urdf_to_mjcf_geoms(urdf_path: str, base_pos, base_ori_rpy, scale: float,
                       rgba=None) -> str:
    """Convert a static URDF (fixed joints, primitive geoms) into MJCF geom XML.

    Only covers what the dedo rigid scene URDFs actually use: fixed joints,
    visual geometries of type cylinder/box/sphere. Collision geoms are merged
    with visual (we emit one geom per visual). All geoms are static (attached
    to worldbody) with fixed poses derived from the URDF joint chain.
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(urdf_path)
    root = tree.getroot()

    # Build link and joint maps.
    links = {link.get('name'): link for link in root.findall('link')}
    # joints: child_link -> (parent_link, origin_xyz, origin_rpy)
    child_to_joint = {}
    for j in root.findall('joint'):
        parent = j.find('parent').get('link')
        child = j.find('child').get('link')
        origin = j.find('origin')
        xyz = [0, 0, 0]
        rpy = [0, 0, 0]
        if origin is not None:
            xyz = [float(v) for v in origin.get('xyz', '0 0 0').split()]
            rpy = [float(v) for v in origin.get('rpy', '0 0 0').split()]
        child_to_joint[child] = (parent, xyz, rpy)

    # Find root link (no incoming joint).
    root_links = [n for n in links if n not in child_to_joint]
    assert len(root_links) == 1, f'Expected single root link in {urdf_path}'

    # Resolve world pose of each link by walking up the chain.
    base_R = _rpy_to_mat(base_ori_rpy)
    base_t = np.array(base_pos, dtype=float)

    def link_world_pose(name):
        if name in child_to_joint:
            parent, xyz, rpy = child_to_joint[name]
            pR, pt = link_world_pose(parent)
            R = pR @ _rpy_to_mat(rpy)
            t = pt + pR @ (np.array(xyz) * scale)
            return R, t
        return base_R, base_t

    frags = []
    for name, link in links.items():
        link_R, link_t = link_world_pose(name)
        for vi, visual in enumerate(link.findall('visual')):
            origin = visual.find('origin')
            vxyz = [0, 0, 0]
            vrpy = [0, 0, 0]
            if origin is not None:
                vxyz = [float(v) for v in origin.get('xyz', '0 0 0').split()]
                vrpy = [float(v) for v in origin.get('rpy', '0 0 0').split()]
            vR = _rpy_to_mat(vrpy)
            R = link_R @ vR
            t = link_t + link_R @ (np.array(vxyz) * scale)
            quat = _mat_to_quat(R)

            geom = visual.find('geometry')
            if geom is None:
                continue
            cyl = geom.find('cylinder')
            box = geom.find('box')
            sph = geom.find('sphere')
            rgba_str = ''
            if rgba is not None:
                rgba_str = f'rgba="{rgba[0]} {rgba[1]} {rgba[2]} {rgba[3]}"'
            else:
                mat = visual.find('material/color')
                if mat is not None:
                    rgba_str = f'rgba="{mat.get("rgba")}"'
            pose = (f'pos="{t[0]} {t[1]} {t[2]}" '
                    f'quat="{quat[0]} {quat[1]} {quat[2]} {quat[3]}"')
            if cyl is not None:
                length = float(cyl.get('length')) * scale
                radius = float(cyl.get('radius')) * scale
                frags.append(
                    f'<geom type="cylinder" size="{radius} {length / 2}" '
                    f'{pose} {rgba_str}/>'
                )
            elif box is not None:
                sz = [float(v) * scale / 2 for v in box.get('size').split()]
                frags.append(
                    f'<geom type="box" size="{sz[0]} {sz[1]} {sz[2]}" '
                    f'{pose} {rgba_str}/>'
                )
            elif sph is not None:
                radius = float(sph.get('radius')) * scale
                frags.append(
                    f'<geom type="sphere" size="{radius}" {pose} {rgba_str}/>'
                )
    return '\n      '.join(frags)


SCENE_NAME_MAP = {
    'hanggarment': 'hangcloth',
    'bgarments': 'hangcloth',
    'sewing': 'hangcloth',
    'hangproccloth': 'hangcloth',
}


def _resolve_scene_name(task: str) -> str:
    t = task.lower()
    if t in SCENE_NAME_MAP:
        return SCENE_NAME_MAP[t]
    if t.startswith('button'):
        return 'button'
    if t.startswith('dress'):
        return 'dress'
    return t


def _euler_to_quat(rpy):
    r, p, y = rpy
    cr, sr = np.cos(r * 0.5), np.sin(r * 0.5)
    cp, sp = np.cos(p * 0.5), np.sin(p * 0.5)
    cy, sy = np.cos(y * 0.5), np.sin(y * 0.5)
    # MuJoCo quat order: (w, x, y, z)
    return np.array([
        cr * cp * cy + sr * sp * sy,
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
    ])


class DeformEnvMuJoCo(gym.Env):
    MAX_OBS_VEL = 20.0
    MAX_ACT_VEL = 10.0
    WORKSPACE_BOX_SIZE = 20.0
    STEPS_AFTER_DONE = 200
    FINAL_REWARD_MULT = 400
    SUCESS_REWARD_TRESHOLD = 2.5

    def __init__(self, args):
        self.args = args
        self.num_anchors = 2  # HangGarment slice
        self.scene_name = _resolve_scene_name(args.task)

        self.data_path = os.path.join(os.path.dirname(__file__), '..', 'data')
        args.data_path = self.data_path
        self._select_deform_obj()
        self.goal_pos = np.array(SCENE_INFO[self.scene_name]['goal_pos'])

        self.max_episode_len = args.max_episode_len
        self.dt = 1.0 / args.sim_freq

        self.gripper_lims = np.tile(
            np.concatenate([self.WORKSPACE_BOX_SIZE * np.ones(3), np.ones(3)]),
            self.num_anchors,
        )
        self.observation_space = gym.spaces.Box(
            -1.0 * self.gripper_lims, self.gripper_lims, dtype=np.float32
        )
        self.action_space = gym.spaces.Box(
            -np.ones(self.num_anchors * 3, dtype=np.float32),
            np.ones(self.num_anchors * 3, dtype=np.float32),
        )

        self.viewer = None
        self._build_model()

    # ---- setup helpers -------------------------------------------------
    def _select_deform_obj(self):
        args = self.args
        if args.override_deform_obj is not None:
            self.deform_obj = args.override_deform_obj
        else:
            assert args.task in TASK_INFO, f'Unknown task {args.task}'
            versions = TASK_INFO[args.task]
            if args.version == 0:
                self.deform_obj = np.random.choice(versions)
            else:
                self.deform_obj = versions[args.version - 1]
        if self.deform_obj in DEFORM_INFO:
            preset_override_util(args, DEFORM_INFO[self.deform_obj])
        info = DEFORM_INFO[self.deform_obj]
        self.anchor_vertex_ids = [vs[0] for vs in info['deform_anchor_vertices']]
        self.true_loop_vertices = info.get('deform_true_loop_vertices', None)
        self.fixed_pin_vertex_ids = info.get('deform_fixed_anchor_vertex_ids', [])

    def _build_model(self):
        info = DEFORM_INFO[self.deform_obj]
        scale = info.get('deform_scale', self.args.deform_scale)
        init_pos = info.get('deform_init_pos', self.args.deform_init_pos)
        init_ori = info.get('deform_init_ori', self.args.deform_init_ori)
        quat = _euler_to_quat(init_ori)

        # Generate cleaned mesh under a sibling cache dir so flexcomp ingests it.
        cache_root = os.path.join(self.data_path, '_mujoco_cache')
        cleaned_abs = os.path.join(cache_root, self.deform_obj)
        if not os.path.exists(cleaned_abs):
            _clean_obj_for_flexcomp(
                os.path.join(self.data_path, self.deform_obj), cleaned_abs
            )
        mesh_rel = os.path.relpath(cleaned_abs, cache_root)
        meshdir = cache_root

        # Compute anchor-vertex world positions at XML-build time. MuJoCo's
        # <connect> equality bakes anchor2 into eq_data at compile time from
        # the initial relative pose, so mocap bodies MUST start colocated
        # with their target cloth vertices; otherwise the constraint pulls
        # the cloth by the initial offset forever.
        mesh_verts = _read_obj_vertices(cleaned_abs)
        R_init = _rpy_to_mat(init_ori)
        anchor_world = []
        for vid in self.anchor_vertex_ids:
            v_local = mesh_verts[vid] * scale
            v_world = np.array(init_pos) + R_init @ v_local
            anchor_world.append(v_world)
        self._anchor_init_world = np.array(anchor_world)

        # PyBullet → MuJoCo parameter mapping. The engines are too different
        # for a 1:1 conversion, so these are heuristics with CLI overrides
        # (--mj_young / --mj_thickness / --mj_mass / --mj_radius /
        # --mj_edge_damping) used during tuning.
        young = self.args.mj_young if self.args.mj_young is not None else max(
            1e4, info.get('deform_elastic_stiffness', 50.0) * 1e3
        )
        damping = (self.args.mj_edge_damping
                   if self.args.mj_edge_damping is not None
                   else max(0.1, info.get('deform_damping_stiffness', 0.01) * 100.0))
        thickness = self.args.mj_thickness if self.args.mj_thickness is not None else 0.02
        cloth_mass = self.args.mj_mass if self.args.mj_mass is not None else 2.0
        cloth_radius = self.args.mj_radius if self.args.mj_radius is not None else 0.02

        gravity = self.args.sim_gravity

        anchor_init_pos = self._anchor_init_world[0]
        other_init_pos = self._anchor_init_world[1]

        pin_xml = ''
        if self.fixed_pin_vertex_ids:
            pin_ids = ' '.join(str(i) for i in self.fixed_pin_vertex_ids)
            pin_xml = f'<pin id="{pin_ids}"/>'
        flexcomp_xml = (
            f'<flexcomp type="mesh" dim="2" name="cloth" file="{mesh_rel}" '
            f'pos="{init_pos[0]} {init_pos[1]} {init_pos[2]}" '
            f'quat="{quat[0]} {quat[1]} {quat[2]} {quat[3]}" '
            f'scale="{scale} {scale} {scale}" mass="{cloth_mass}" '
            f'radius="{cloth_radius}" rgba="0.2 0.55 0.9 1">'
            f'<edge damping="{damping}"/>'
            f'<contact solref="0.01 1" friction="1.0"/>'
            f'<elasticity young="{young}" poisson="0.0" thickness="{thickness}"/>'
            f'{pin_xml}'
            f'</flexcomp>'
        )

        # Rigid scene entities (hangers, rods, bags, etc.) from SCENE_INFO.
        rigid_frags = []
        mesh_assets = []  # list of (asset_name, abs_path)
        scene = SCENE_INFO.get(self.scene_name, {'entities': {}})
        for rel_path, kw in scene['entities'].items():
            full = os.path.join(self.data_path, rel_path)
            if not os.path.exists(full):
                continue
            if rel_path.endswith('.urdf'):
                frag = _urdf_to_mjcf_geoms(
                    full,
                    base_pos=kw['basePosition'],
                    base_ori_rpy=kw.get('baseOrientation', [0, 0, 0]),
                    scale=kw.get('globalScaling', 1.0),
                    rgba=kw.get('rgbaColor'),
                )
                if frag:
                    rigid_frags.append(frag)
            elif rel_path.endswith('.obj'):
                asset_name = 'rigid_' + os.path.splitext(
                    os.path.basename(rel_path))[0]
                mesh_assets.append((asset_name, full,
                                    kw.get('globalScaling', 1.0)))
                quat = _euler_to_quat(kw.get('baseOrientation', [0, 0, 0]))
                bp = kw['basePosition']
                rgba = kw.get('rgbaColor')
                rgba_str = (f'rgba="{rgba[0]} {rgba[1]} {rgba[2]} {rgba[3]}"'
                            if rgba is not None else '')
                rigid_frags.append(
                    f'<geom type="mesh" mesh="{asset_name}" '
                    f'pos="{bp[0]} {bp[1]} {bp[2]}" '
                    f'quat="{quat[0]} {quat[1]} {quat[2]} {quat[3]}" '
                    f'{rgba_str}/>'
                )
        rigid_xml = '\n    '.join(rigid_frags)
        mesh_asset_xml = '\n    '.join(
            f'<mesh name="{n}" file="{p}" scale="{s} {s} {s}"/>'
            for n, p, s in mesh_assets
        )

        xml = f"""
<mujoco model="dedo_mujoco">
  <option timestep="{self.dt}" integrator="implicitfast" gravity="0 0 {gravity}">
    <flag multiccd="enable"/>
  </option>
  <compiler meshdir="{meshdir}" angle="radian"/>
  <asset>
    <material name="cloth_mat" rgba="0.2 0.5 0.9 1.0"/>
    {mesh_asset_xml}
  </asset>
  <equality>
    <connect name="mocap_connect_0" body1="mocap_0" body2="cloth_{self.anchor_vertex_ids[0]}"
             anchor="0 0 0" solref="0.05 1" solimp="0.9 0.95 0.01" active="true"/>
    <connect name="mocap_connect_1" body1="mocap_1" body2="cloth_{self.anchor_vertex_ids[1]}"
             anchor="0 0 0" solref="0.05 1" solimp="0.9 0.95 0.01" active="true"/>
  </equality>
  <worldbody>
    <light pos="0 0 20" dir="0 0 -1" directional="true"/>
    <light pos="0 -10 10" dir="0 1 -0.5" directional="true" diffuse=".6 .6 .6"/>
    <geom name="floor" type="plane" pos="0 0 0" size="50 50 0.1" rgba="0.7 0.7 0.7 1"/>
    <body name="mocap_0" mocap="true" pos="{anchor_init_pos[0]} {anchor_init_pos[1]} {anchor_init_pos[2]}">
      <geom type="sphere" size="0.1" rgba="1 0 1 1" contype="0" conaffinity="0"/>
    </body>
    <body name="mocap_1" mocap="true" pos="{other_init_pos[0]} {other_init_pos[1]} {other_init_pos[2]}">
      <geom type="sphere" size="0.1" rgba="1 0 1 1" contype="0" conaffinity="0"/>
    </body>
    <body name="cloth">
      {flexcomp_xml}
    </body>
    {rigid_xml}
  </worldbody>
</mujoco>
"""
        self.model = mujoco.MjModel.from_xml_string(xml)
        self.data = mujoco.MjData(self.model)
        self._mocap_body_ids = [
            mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, f'mocap_{i}')
            for i in range(self.num_anchors)
        ]
        self._mocap_idx = [
            int(self.model.body_mocapid[bid]) for bid in self._mocap_body_ids
        ]
        # Cache vertex body ids for reward (true_loop_vertices -> body ids).
        self._vertex_body_ids = None
        if self.true_loop_vertices is not None:
            self._vertex_body_ids = [
                np.array([
                    mujoco.mj_name2id(
                        self.model, mujoco.mjtObj.mjOBJ_BODY, f'cloth_{v}'
                    )
                    for v in loop
                ])
                for loop in self.true_loop_vertices
            ]
        self._mocap_vel = np.zeros((self.num_anchors, 3))

    # ---- gym API -------------------------------------------------------
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            np.random.seed(seed)
        self.stepnum = 0
        self.episode_reward = 0.0
        mujoco.mj_resetData(self.model, self.data)
        mujoco.mj_forward(self.model, self.data)
        if self.args.viz and self.viewer is None:
            from mujoco import viewer as _mj_viewer
            self.viewer = _mj_viewer.launch_passive(self.model, self.data)
        obs, _ = self._get_obs()
        return obs.astype(np.float32), {}

    def step(self, action, unscaled=False):
        action = np.asarray(action, dtype=np.float64).reshape(self.num_anchors, 3)
        if not unscaled:
            assert (np.abs(action) <= 1.0 + 1e-6).all()
            vel = action * self.MAX_ACT_VEL
        else:
            vel = action
        self._mocap_vel = vel

        for _ in range(self.args.sim_steps_per_action):
            for i in range(self.num_anchors):
                self.data.mocap_pos[self._mocap_idx[i]] += vel[i] * self.dt
            mujoco.mj_step(self.model, self.data)
            if self.viewer is not None:
                self.viewer.sync()
                if self.args.debug:
                    time.sleep(self.dt)

        obs, terminated = self._get_obs()
        reward = self._get_reward()
        if terminated:
            reward *= max(1, self.max_episode_len - self.stepnum)
        truncated = self.stepnum >= self.max_episode_len
        info = {}
        if terminated or truncated:
            self._make_final_steps()
            last_rwd = self._get_reward() * self.FINAL_REWARD_MULT
            info['is_success'] = abs(last_rwd) < self.SUCESS_REWARD_TRESHOLD
            reward += last_rwd
            info['final_reward'] = reward
        self.episode_reward += reward
        self.stepnum += 1
        return obs.astype(np.float32), float(reward), bool(terminated), bool(truncated), info

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

    # ---- internals -----------------------------------------------------
    def _get_obs(self):
        anc = []
        for i in range(self.num_anchors):
            pos = self.data.mocap_pos[self._mocap_idx[i]]
            anc.extend(pos.tolist())
            anc.extend((self._mocap_vel[i] / self.MAX_OBS_VEL).tolist())
        obs = np.nan_to_num(np.array(anc))
        terminated = bool((np.abs(obs) > self.gripper_lims).any())
        if terminated:
            obs = np.clip(obs, -self.gripper_lims, self.gripper_lims)
        return obs, terminated

    def _vertex_positions(self):
        # flexcomp vertex bodies have a free joint; xpos gives world position.
        return self.data.xpos

    def _get_reward(self):
        if self._vertex_body_ids is None:
            return 0.0
        xpos = self._vertex_positions()
        dists = []
        n = min(len(self._vertex_body_ids), len(self.goal_pos))
        for i in range(n):
            pts = xpos[self._vertex_body_ids[i]]
            pts = pts[~np.isnan(pts).any(axis=1)]
            if len(pts) == 0:
                return -float(self.WORKSPACE_BOX_SIZE)
            dists.append(np.linalg.norm(pts.mean(axis=0) - self.goal_pos[i]))
        dist = float(np.mean(dists))
        return -dist / self.WORKSPACE_BOX_SIZE

    def _make_final_steps(self):
        for _ in range(self.STEPS_AFTER_DONE):
            mujoco.mj_step(self.model, self.data)
            if self.viewer is not None:
                self.viewer.sync()

    @property
    def sim(self):
        return self  # crude shim for callers expecting env.sim
