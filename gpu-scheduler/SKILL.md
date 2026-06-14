---
name: gpu-scheduler
description: "Schedule local GPU experiments by selecting CUDA devices from live nvidia-smi state. Use before running real GPU work such as CUDA training, inference, benchmarks, model evaluation, multi-GPU jobs, or any experiment that needs GPU allocation, especially on a shared two-GPU workstation."
---

# GPU Experiment Scheduler

## Overview

Use this skill before launching GPU experiments. Select GPUs first, activate the project virtual environment, then launch the command with the recommended `CUDA_VISIBLE_DEVICES` value.

Never kill, pause, or reconfigure another user's process. This skill only decides which visible devices to use.

Coordinate with `uv-mirror-env` for Python environment handling. Before running GPU experiment code, prefer:

```bash
source .venv/bin/activate
```

If `.venv` is missing or broken, use `uv-mirror-env` to create or repair it before running the experiment.

## Workflow

1. Check current local time in `Asia/Shanghai`.
2. Inspect GPU state with `nvidia-smi` or the helper script.
3. Choose devices using the policy below.
4. Run `source .venv/bin/activate` from the project root.
5. Prefix the experiment command with `CUDA_VISIBLE_DEVICES=<ids>`.
6. Re-check GPU state immediately before long or expensive runs.

Helper:

```bash
python ./scripts/select_gpu.py --tasks 1
python ./scripts/select_gpu.py --tasks 2 --min-free-mb 24000 --json
```

## Scheduling Policy

Assume the normal target machine has GPUs `0` and `1`.

Daytime policy, outside `22:00-08:30`:

- If no other user is using either GPU, use both GPUs when the experiment can benefit from both; otherwise use the least loaded single GPU.
- If another user occupies one GPU, use only the unoccupied GPU.
- If another user occupies both GPUs, use exactly one GPU: choose the lower-load GPU.
- Always allocate at least one GPU for a GPU-required experiment unless the user explicitly cancels.

Night policy, from `22:00` through `08:30`:

- If free VRAM is sufficient, use both GPUs.
- For one task, run one dual-GPU program with `CUDA_VISIBLE_DEVICES=0,1`.
- For two tasks, run one task on GPU `0` and the other on GPU `1`; schedule them in order instead of oversubscribing a GPU.
- If VRAM is not sufficient on both GPUs, fall back to the daytime lower-load single-GPU selection.

Load ranking:

- Prefer GPUs without other-user processes.
- Rank lower used VRAM before lower GPU utilization.
- Treat unavailable or unparsable utilization as high utilization.

## Command Patterns

Single-GPU run:

```bash
source .venv/bin/activate
CUDA_VISIBLE_DEVICES=<id> python train.py
```

Dual-GPU run:

```bash
source .venv/bin/activate
CUDA_VISIBLE_DEVICES=0,1 torchrun --nproc_per_node=2 train.py
```

Two independent night tasks:

```bash
source .venv/bin/activate
CUDA_VISIBLE_DEVICES=0 python task_a.py
CUDA_VISIBLE_DEVICES=1 python task_b.py
```

## Fallbacks

- If `nvidia-smi` is unavailable, stop and report that GPU state cannot be verified.
- If the machine has one GPU, select that GPU when it has enough free memory.
- If the machine has more than two GPUs, apply the same policy to the two lowest-index GPUs unless the user asks otherwise.
- If required VRAM is unknown, choose by current free VRAM and state that the selection is best-effort.
