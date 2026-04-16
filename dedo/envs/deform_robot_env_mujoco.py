"""MuJoCo backend for DeformRobotEnv.

Replaces the dual mocap bodies of DeformEnvMuJoCo with a dual-arm Franka
driven by mink differential IK. The cloth's anchor vertices are connected
to each arm's `panda_link7_{r,l}` body via MuJoCo <connect> equality, so
the arms carry the cloth. Per step: action → target EE positions written
to mocap bodies → mink solves IK → position actuators track the solution.
"""

import os
import re
import xml.etree.ElementTree as ET

import gymnasium as gym
import mink
import mujoco
import numpy as np

from ..utils.task_info import ROBOT_INFO
from .deform_env_mujoco import DeformEnvMuJoCo

# Scale factor for dedo's ~10x world vs native Franka dimensions. Positions
# inside the arm MJCF and mesh scales are multiplied by this.
_ARM_SCALE = 10.0


def _scale_pos_attr(s: str) -> str:
    parts = s.split()
    return ' '.join(f'{float(p) * _ARM_SCALE:.6f}' for p in parts)


def _build_scaled_franka_mjcf(urdf_path: str, out_path: str) -> None:
    """Compile franka_dual.urdf to MJCF, scale 10x, add actuators + EE sites.

    MuJoCo has no "scale a body tree" op, so we post-process the MJCF text:
    scale every body/inertial/joint/geom `pos=` by _ARM_SCALE, multiply each
    `<mesh scale=...>` by _ARM_SCALE, add position actuators for every arm
    joint, and insert sentinel `ee_site_{r,l}` sites at `panda_link7_{r,l}`
    so mink has targetable frames.
    """
    # 1. Compile URDF → tmp MJCF via mujoco.
    tmp_model = mujoco.MjModel.from_xml_path(urdf_path)
    tmp_xml = '/tmp/_franka_dual_raw.xml'
    mujoco.mj_saveLastXML(tmp_xml, tmp_model)

    tree = ET.parse(tmp_xml)
    root = tree.getroot()

    # 2. Scale <mesh scale=...> (default 1 1 1 → 10 10 10).
    for mesh in root.iter('mesh'):
        existing = mesh.get('scale')
        if existing:
            vals = [float(v) * _ARM_SCALE for v in existing.split()]
        else:
            vals = [_ARM_SCALE] * 3
        mesh.set('scale', ' '.join(f'{v}' for v in vals))
        # Resolve mesh file to absolute path so compiler doesn't depend on meshdir.
        fname = mesh.get('file')
        if fname and not os.path.isabs(fname):
            mesh.set('file', os.path.join(
                os.path.dirname(urdf_path), fname))

    # 3. Scale `pos=` attrs everywhere.
    for elem in root.iter():
        if elem.tag in ('body', 'inertial', 'joint', 'geom', 'site'):
            if 'pos' in elem.attrib:
                elem.set('pos', _scale_pos_attr(elem.get('pos')))

    # 3b. Make all arm geoms non-collidable. Flex cloth dropping on arm
    # geometry would otherwise impulsively push the arm off the mocap.
    for geom in root.iter('geom'):
        geom.set('contype', '0')
        geom.set('conaffinity', '0')

    # 3a. Scale inertia proportional to s² (mass unchanged). Gravity-
    # compensate every arm body so the un-actuated arm doesn't sag — the
    # weld only fixes link7's pose, so without gravcomp, link1-6 would
    # swing as a gravity-loaded pendulum.
    s2 = _ARM_SCALE ** 2
    for inertial in root.iter('inertial'):
        di = inertial.get('diaginertia')
        if di:
            vals = [float(v) * s2 for v in di.split()]
            inertial.set('diaginertia', ' '.join(f'{v}' for v in vals))
    for body in root.iter('body'):
        body.set('gravcomp', '1')
    for joint in root.iter('joint'):
        jname = joint.get('name') or ''
        if 'finger' in jname:
            continue
        d = joint.get('damping')
        d = float(d) if d else 0.0
        joint.set('damping', f'{max(d * 10.0, 50.0)}')
        # Armature adds rotor-side inertia; damps high-freq oscillations when
        # the weld drives the arm on a short control horizon.
        joint.set('armature', '5.0')

    # 4. Remove <compiler>'s angle attr clobber potential; ensure no meshdir.
    comp = root.find('compiler')
    if comp is not None:
        comp.attrib.pop('meshdir', None)

    # 5. Insert ee_site at each link7 body origin. Cloth connect, mink
    # target, and weld-to-mocap all resolve at the body origin — keeping the
    # site there avoids inconsistencies that would show up as a constraint
    # tug when the sim starts.
    for side in ('r', 'l'):
        link7 = root.find(f".//body[@name='panda_link7_{side}']")
        if link7 is None:
            raise RuntimeError(f'panda_link7_{side} not found in compiled MJCF')
        ET.SubElement(link7, 'site', {
            'name': f'ee_site_{side}',
            'pos': '0 0 0',
            'size': '0.05',
            'rgba': '1 1 0 1',
        })

    # No actuators — the arm is driven kinematically by a weld equality
    # from the scene's mocap bodies to panda_link7_{r,l}. MuJoCo's constraint
    # solver handles the IK internally, and cloth sees a kinematic arm,
    # which is essential for stability of the flex mesh.

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tree.write(out_path)


def _fragment_xml(model_path: str) -> tuple[str, str, str]:
    """Split scaled Franka MJCF into (assets, worldbody_inner, actuators) for splicing."""
    with open(model_path) as f:
        txt = f.read()
    # Crude but works: extract inner content of each top-level section.
    def _extract(tag: str) -> str:
        m = re.search(fr'<{tag}[^>]*>(.*)</{tag}>', txt, re.DOTALL)
        return m.group(1) if m else ''
    return _extract('asset'), _extract('worldbody'), _extract('actuator')


class DeformRobotEnvMuJoCo(DeformEnvMuJoCo):
    ORI_SIZE = 6  # unused for first-cut (position-only control)
    FING_DIST = 0.01

    def __init__(self, args):
        self._arm_frags = None  # populated by _extra_xml_fragments during super.__init__
        self._robot_info = ROBOT_INFO.get(f'franka{2 if not args.env.startswith("FoodPacking") else 1}')
        assert self._robot_info is not None
        # The weld+flex combo is only stable with a shorter sim step. Bump
        # sim_freq unless the user already set something higher.
        if args.sim_freq < 2000:
            args.sim_freq = 2000
        self._prepare_arm_mjcf(args)
        super().__init__(args)

        # mink setup — uses a standalone arm-only model so IK solves over 18
        # DOFs instead of the ~900 DOFs of the full scene (incl. cloth flex).
        self._ik_model = mujoco.MjModel.from_xml_string(self._arm_only_xml)
        self._ik_data = mujoco.MjData(self._ik_model)
        self._init_ik_qpos()
        self.configuration = mink.Configuration(self._ik_model)
        self.configuration.update(self._ik_data.qpos.copy())
        self._ee_tasks = [
            mink.FrameTask(
                frame_name=f'ee_site_{side}', frame_type='site',
                position_cost=1.0, orientation_cost=0.0, lm_damping=1.0,
            )
            for side in ('r', 'l')
        ]
        self._posture_task = mink.PostureTask(model=self._ik_model, cost=1e-3)
        self._posture_task.set_target_from_configuration(self.configuration)
        self._mink_tasks = [*self._ee_tasks, self._posture_task]
        self._mink_solver = 'daqp'
        self._mink_dt = self.dt
        # Velocity limit per joint — prevents the solver from returning huge
        # velocities when targets are far, which would destabilize the sim.
        vel_limits = {
            jname: 2.0 for jname in self._arm_joint_names()
        }
        self._mink_limits = [
            mink.VelocityLimit(self._ik_model, vel_limits),
            mink.ConfigurationLimit(self._ik_model),
        ]
        # Map joint name -> qposadr for transferring IK solution back to main.
        self._joint_qadr_main = self._build_joint_qadr_map(self.model)
        self._joint_qadr_ik = self._build_joint_qadr_map(self._ik_model)

        # Solve IK once so each arm's EE starts at the cloth anchor vertex.
        # Without this, the <connect> equality yanks the cloth violently on
        # the first step.
        self._init_qpos_cache = self._solve_init_qpos()
        self._apply_cached_qpos()

        # Action space: absolute EE positions (3 per arm) in [-1, 1].
        self.action_space = gym.spaces.Box(
            -np.ones(self.num_anchors * 3, dtype=np.float32),
            np.ones(self.num_anchors * 3, dtype=np.float32),
        )

    # ---- MJCF prep -----------------------------------------------------
    def _prepare_arm_mjcf(self, args):
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data')
        cache_dir = os.path.join(data_path, '_mujoco_cache')
        out_path = os.path.join(cache_dir, 'franka_dual_scaled.xml')
        urdf_path = os.path.join(
            data_path, 'robots', self._robot_info['file_name'])
        if not os.path.exists(out_path):
            _build_scaled_franka_mjcf(urdf_path, out_path)
        self._arm_mjcf_path = out_path
        self._arm_frags = _fragment_xml(out_path)
        # Build standalone arm-only model (wrapped in the same robot_base body
        # used in the full scene) for fast IK over the 18-DOF arm only.
        base_pos = self._robot_info['base_pos']
        self._arm_only_xml = f"""
<mujoco model="arm_only">
  <compiler angle="radian"/>
  <asset>{self._arm_frags[0]}</asset>
  <worldbody>
    <body name="robot_base" pos="{base_pos[0]} {base_pos[1]} {base_pos[2]}" quat="0 0 0 1">
      {self._arm_frags[1]}
    </body>
  </worldbody>
  <actuator>{self._arm_frags[2]}</actuator>
</mujoco>
"""

    # ---- DeformEnvMuJoCo hooks -----------------------------------------
    def _extra_xml_fragments(self):
        assets, world_inner, actuators = self._arm_frags
        # Wrap the scaled arm in a parent body at robot_info['base_pos']
        # with yaw=π. All child body `pos`s are relative to this parent.
        base_pos = self._robot_info['base_pos']
        base_quat = '0 0 0 1'  # yaw=π
        world_xml = (
            f'<body name="robot_base" pos="{base_pos[0]} {base_pos[1]} '
            f'{base_pos[2]}" quat="{base_quat}">\n{world_inner}\n</body>'
        )
        # Weld each mocap body to the corresponding arm link7 so the arm
        # follows the mocap kinematically via the constraint solver — no
        # actuators or IK needed at runtime. relpose="0 0 0 1 0 0 0"
        # disables MuJoCo's default compile-time offset baking so mocap
        # and link7 are rigidly identified.
        equality_xml = (
            '<weld name="weld_r" body1="mocap_0" body2="panda_link7_r" '
            '  relpose="0 0 0 1 0 0 0" solref="0.01 1" '
            '  solimp="0.95 0.99 0.001"/>\n'
            '<weld name="weld_l" body1="mocap_1" body2="panda_link7_l" '
            '  relpose="0 0 0 1 0 0 0" solref="0.01 1" '
            '  solimp="0.95 0.99 0.001"/>'
        )
        return assets, world_xml, actuators, equality_xml

    # Keep cloth attached to mocap (parent default). The arm follows mocap
    # via weld, so visually the cloth is at the gripper, but the dynamic
    # grasp is physically carried by the kinematic mocap — not the arm —
    # which avoids destabilizing the flex cloth with articulated-arm
    # feedback forces.

    # ---- qpos init -----------------------------------------------------
    def _build_joint_qadr_map(self, model):
        m = {}
        for jid in range(model.njnt):
            name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, jid)
            if name is not None:
                m[name] = int(model.jnt_qposadr[jid])
        return m

    def _arm_joint_names(self):
        return [f'panda_joint{i + 1}_{s}'
                for s in ('r', 'l') for i in range(7)]

    def _init_ik_qpos(self):
        """Seed the arm-only IK model with ROBOT_INFO rest_arm_qpos."""
        qadr = self._build_joint_qadr_map(self._ik_model)
        rest = self._robot_info['rest_arm_qpos']
        left_rest = self._robot_info.get('left_rest_arm_qpos', rest)
        for side, q in (('r', rest), ('l', left_rest)):
            for i in range(7):
                jname = f'panda_joint{i + 1}_{side}'
                if jname in qadr:
                    self._ik_data.qpos[qadr[jname]] = q[i]
        mujoco.mj_forward(self._ik_model, self._ik_data)

    # ---- IK init -------------------------------------------------------
    def _solve_init_qpos(self) -> np.ndarray:
        """Run mink IK on the arm-only model to place each EE at the cloth anchor.

        Returns the solved arm-model qpos vector.
        """
        for i, task in enumerate(self._ee_tasks):
            tgt_T = mink.SE3.from_rotation_and_translation(
                mink.SO3.identity(),
                np.asarray(self._anchor_init_world[i]),
            )
            task.set_target(tgt_T)
        ik_dt = 0.05
        for _ in range(400):
            vel = mink.solve_ik(
                self.configuration, self._ee_tasks,
                ik_dt, self._mink_solver, damping=1e-3,
            )
            if np.linalg.norm(vel) < 1e-5:
                break
            self.configuration.integrate_inplace(vel, ik_dt)
        self._posture_task.set_target_from_configuration(self.configuration)
        return self.configuration.q.copy()

    def _transfer_arm_qpos_to_main(self, arm_qpos):
        """Copy arm-model joint qpos into the main model's qpos."""
        for jname in self._arm_joint_names():
            if jname not in self._joint_qadr_main or jname not in self._joint_qadr_ik:
                continue
            self.data.qpos[self._joint_qadr_main[jname]] = \
                arm_qpos[self._joint_qadr_ik[jname]]

    def _apply_cached_qpos(self):
        self.data.qvel[:] = 0.0
        self._transfer_arm_qpos_to_main(self._init_qpos_cache)
        mujoco.mj_forward(self.model, self.data)
        # Set each mocap_pos to the ACTUAL world position of its welded link7
        # body after forward-kinematics — not the IK target — so the weld
        # equality has zero residual at step 0.
        for i, side in enumerate(('r', 'l')):
            bid = mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_BODY, f'panda_link7_{side}')
            self.data.mocap_pos[self._mocap_idx[i]] = self.data.xpos[bid]
        mujoco.mj_forward(self.model, self.data)
        # Sync IK state.
        self._ik_data.qpos[:] = self._init_qpos_cache
        mujoco.mj_forward(self._ik_model, self._ik_data)
        self.configuration.update(self._ik_data.qpos.copy())

    # ---- gym API overrides --------------------------------------------
    def reset(self, *, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)
        self._apply_cached_qpos()
        mujoco.mj_forward(self.model, self.data)
        # Rebuild obs to reflect the repositioned arm.
        obs, _ = self._get_obs()
        if not self.cam_on:
            obs = obs.astype(np.float32)
        return obs, info

    def step(self, action, unscaled=False):
        action = np.asarray(action, dtype=np.float64).reshape(self.num_anchors, 3)
        # Action is absolute EE target in [-1,1] × WORKSPACE_BOX_SIZE.
        if unscaled:
            targets = action
        else:
            assert (np.abs(action) <= 1.0 + 1e-6).all()
            targets = action * self.WORKSPACE_BOX_SIZE

        # Slew the mocap targets toward `targets` over the sim substeps so the
        # weld equality has a reachable short-horizon goal each sim step. This
        # avoids the constraint solver facing a 10m jump in one tick.
        cur = np.array([self.data.mocap_pos[self._mocap_idx[i]].copy()
                        for i in range(self.num_anchors)])
        n = self.args.sim_steps_per_action
        for k in range(n):
            alpha = (k + 1) / n
            for i in range(self.num_anchors):
                self.data.mocap_pos[self._mocap_idx[i]] = (
                    (1 - alpha) * cur[i] + alpha * targets[i])
            mujoco.mj_step(self.model, self.data)
            if self.viewer is not None:
                self.viewer.sync()

        obs, terminated = self._get_obs()
        reward = self._get_reward()
        if terminated:
            reward *= max(1, self.max_episode_len - self.stepnum)
        truncated = self.stepnum >= self.max_episode_len
        info = {}
        if terminated or truncated:
            self._make_final_steps_robot(targets)
            last_rwd = self._get_reward() * self.FINAL_REWARD_MULT
            info['is_success'] = abs(last_rwd) < self.SUCESS_REWARD_TRESHOLD
            reward += last_rwd
            info['final_reward'] = reward
        self.episode_reward += reward
        self.stepnum += 1
        if not self.cam_on:
            obs = obs.astype(np.float32)
        return obs, float(reward), bool(terminated), bool(truncated), info

    def _ik_step(self, targets):
        # Set EE task targets (position-only; orientation cost is 0).
        for i, task in enumerate(self._ee_tasks):
            tgt_T = mink.SE3.from_rotation_and_translation(
                mink.SO3.identity(), np.asarray(targets[i]))
            task.set_target(tgt_T)
        try:
            vel = mink.solve_ik(
                self.configuration, self._mink_tasks,
                self._mink_dt, self._mink_solver, damping=1e-3,
                limits=self._mink_limits,
            )
            self.configuration.integrate_inplace(vel, self._mink_dt)
        except Exception:
            return
        # Write the IK arm qpos as position-actuator targets on the main model.
        for i in range(self.model.nu):
            jnt_id = self.model.actuator_trnid[i, 0]
            jname = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, jnt_id)
            if jname in self._joint_qadr_ik:
                self.data.ctrl[i] = self.configuration.q[self._joint_qadr_ik[jname]]

    def _make_final_steps_robot(self, last_targets):
        for i in range(self.num_anchors):
            self.data.mocap_pos[self._mocap_idx[i]] = last_targets[i]
        for _ in range(self.STEPS_AFTER_DONE):
            mujoco.mj_step(self.model, self.data)
            if self.viewer is not None:
                self.viewer.sync()

    def _grip_obs(self):
        # EE pos + finite-difference velocity (normalized) per arm. We avoid
        # data.cvel because it is center-of-mass velocity — on an articulated
        # arm that can spike to large values even when the EE itself barely
        # moves, which would trip the parent env's velocity termination.
        obs = []
        cur_pos = []
        for side in ('r', 'l'):
            sid = mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_SITE, f'ee_site_{side}')
            cur_pos.append(np.array(self.data.site_xpos[sid], dtype=float))
        prev = getattr(self, '_prev_ee_pos', None)
        dt_obs = max(self.dt * self.args.sim_steps_per_action, 1e-6)
        for i, side in enumerate(('r', 'l')):
            obs.extend(cur_pos[i].tolist())
            if prev is None:
                vel = np.zeros(3)
            else:
                vel = (cur_pos[i] - prev[i]) / dt_obs
            obs.extend((vel / self.MAX_OBS_VEL).tolist())
        self._prev_ee_pos = cur_pos
        return np.nan_to_num(np.array(obs))
