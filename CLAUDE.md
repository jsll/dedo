# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

Managed with **uv**. Python 3.10 is pinned via `.python-version`; supported range is `>=3.8,<3.11` (upper bound from `stable_baselines3==1.2.0`).

```
uv sync --all-extras   # creates .venv, installs locked deps + dev tools
```

Run any command inside the env with `uv run <cmd>` (e.g. `uv run uv run python -m dedo.demo ...`).

**Pinned deps of note** (`pyproject.toml`): `gym==0.25.2`, `pybullet>=3.2.5`, `stable_baselines3==1.2.0`. The original repo pinned `gym==0.21.0` / `pybullet==3.1.7`; both were un-installable on modern toolchains (gym 0.21 has malformed wheel metadata, pybullet 3.1.7 won't compile under modern GCC) so they were bumped as part of tooling modernization. The code still uses the legacy gym 0.21 API (`env.seed`, 4-tuple `step`) which gym 0.25 accepts with deprecation warnings — a full gymnasium/sb3 2.x migration is deferred to phase 2.

## Lint & format

Ruff (config in `pyproject.toml`) plus pre-commit hooks:

```
uv run ruff check .              # lint
uv run ruff check --fix .        # autofix
uv run ruff format .             # format
uv run pre-commit install        # one-time: enable git hooks
```

There is no test suite or CI in this repo.

## Common commands

Visualize a task with a hard-coded policy:
```
uv run python -m dedo.demo --env=HangGarment-v1 --viz --debug
```

Run a preset trajectory demo:
```
uv run python -m dedo.demo_preset --env=HangBag-v1 --viz
```

Point-cloud observations: add `--pcd --logdir rendered` to either demo.

Train RL (Stable-Baselines3 or RLlib):
```
uv run python -m dedo.run_rl_sb3 --env=HangGarment-v0 --logdir=/tmp/dedo --num_play_runs=3 --viz --debug
uv run python -m dedo.run_rllib --env=HangGarment-v0 --logdir=/tmp/dedo --num_play_runs=3 --viz --debug
```

Train VAE variants: `uv run python -m dedo.run_svae ...`. View training with `tensorboard --logdir=/tmp/dedo`.

CLI flags are centralized in `dedo/utils/args.py` — add/modify args there rather than in individual scripts.

## Architecture

**Single Gym env, many tasks via registration.** `dedo/__init__.py` is the heart of the package: on import it walks `TASK_INFO` (from `dedo/utils/task_info.py`) and registers one Gym id per (task, mesh-variant) pair — e.g. `HangGarment-v0` (randomized) through `HangGarment-v10`. All tasks share a single env class: `DeformEnv` (`dedo/envs/deform_env.py`), except `FoodPacking*` and `HangGarmentRobot-v1` which use `DeformRobotEnv` (`dedo/envs/deform_robot_env.py`). Task behavior is driven by data (entries in `TASK_INFO` / `DEFORM_INFO`), not by subclassing.

**Per-deformable physics config.** `DEFORM_INFO` in `task_info.py` maps each `.obj` path (relative to `dedo/data/`) to initial pose, scale, stiffness, and `deform_true_loop_vertices` used for success/reward computation. Adding a custom mesh = new entry in `DEFORM_INFO` + `--override_deform_obj path/to.obj`.

**Utility layering.** Scripts (`demo.py`, `demo_preset.py`, `run_rl_sb3.py`, `run_rllib.py`, `run_svae.py`) are thin drivers over `dedo/utils/`:
- `init_utils.py` — PyBullet world / anchor / deformable loading
- `anchor_utils.py` — the two "hand" anchors that drive deformables
- `bullet_manipulator.py` — Franka arm wrapper used by robot envs
- `camera_utils.py`, `process_camera.py`, `pcd_utils.py` — rendering and point-cloud segmentation
- `procedural_utils.py` — procedural cloth generation for `ButtonProc` / `HangProcCloth`
- `preset_info.py` — hard-coded trajectories used by `demo_preset.py`
- `rl_sb3_utils.py`, `rllib_utils.py`, `train_utils.py` — RL training glue
- `vaes/` — VAE model variants for `run_svae.py`

**Point-cloud caveat.** PyBullet only segments the deformable if it has ID 0, so the deformable is loaded first. Side effect: the floor can disappear in rendered output.

**Data.** Meshes and textures live under `dedo/data/` (bags, garments, berkeley_garments, sewing, etc.). `HangBag` totes and `sewing`/`BGarments` mesh lists are discovered at import time by scanning those directories.

## Docs

Most usage documentation lives in the GitHub wiki (see README links), not in-repo.
