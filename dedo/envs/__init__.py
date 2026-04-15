from dedo.envs.deform_env import DeformEnv
from dedo.envs.deform_robot_env import DeformRobotEnv

try:
    from dedo.envs.deform_env_mujoco import DeformEnvMuJoCo
except ImportError:
    DeformEnvMuJoCo = None
