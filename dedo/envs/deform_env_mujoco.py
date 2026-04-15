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

        # Stiffness mapping (PyBullet -> MuJoCo): rough heuristic, will need
        # empirical tuning per task. Treat elastic as Young's modulus proxy.
        young = max(50.0, info.get('deform_elastic_stiffness', 50.0) * 1e3)
        damping = max(0.1, info.get('deform_damping_stiffness', 0.01) * 100.0)

        gravity = self.args.sim_gravity

        anchor_init_pos = self.args.anchor_init_pos
        other_init_pos = self.args.other_anchor_init_pos

        flexcomp_xml = (
            f'<flexcomp type="mesh" dim="2" name="cloth" file="{mesh_rel}" '
            f'pos="{init_pos[0]} {init_pos[1]} {init_pos[2]}" '
            f'quat="{quat[0]} {quat[1]} {quat[2]} {quat[3]}" '
            f'scale="{scale} {scale} {scale}" mass="0.5" radius="0.02">'
            f'<edge equality="true" damping="{damping}"/>'
            f'<contact solref="0.01 1" friction="1.0"/>'
            f'<elasticity young="{young}" poisson="0.0" thickness="5e-3"/>'
            f'</flexcomp>'
        )

        xml = f"""
<mujoco model="dedo_mujoco">
  <option timestep="{self.dt}" integrator="implicitfast" gravity="0 0 {gravity}">
    <flag multiccd="enable"/>
  </option>
  <compiler meshdir="{meshdir}" angle="radian"/>
  <equality>
    <connect name="mocap_connect_0" body1="mocap_0" body2="cloth_{self.anchor_vertex_ids[0]}"
             anchor="0 0 0" solref="0.01 1" solimp=".95 .99 0.001" active="true"/>
    <connect name="mocap_connect_1" body1="mocap_1" body2="cloth_{self.anchor_vertex_ids[1]}"
             anchor="0 0 0" solref="0.01 1" solimp=".95 .99 0.001" active="true"/>
  </equality>
  <worldbody>
    <light pos="0 0 20" dir="0 0 -1" directional="true"/>
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
        # Reset mocap positions to args defaults.
        self.data.mocap_pos[self._mocap_idx[0]] = np.array(self.args.anchor_init_pos)
        self.data.mocap_pos[self._mocap_idx[1]] = np.array(self.args.other_anchor_init_pos)
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
