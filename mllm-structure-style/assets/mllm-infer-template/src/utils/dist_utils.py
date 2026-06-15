from __future__ import annotations

import os
from datetime import timedelta
from typing import Any

import torch
import torch.distributed as dist


def _local_world_size() -> int:
    return int(os.environ.get("LOCAL_WORLD_SIZE", os.environ.get("WORLD_SIZE", "1")))


def _can_use_cuda_for_all_local_ranks() -> bool:
    return torch.cuda.is_available() and torch.cuda.device_count() >= _local_world_size()


def init_distributed(env_cfg: Any) -> None:
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    if world_size <= 1 or not dist.is_available() or dist.is_initialized():
        return

    backend = str(getattr(env_cfg, "distributed_backend", "nccl"))
    if not _can_use_cuda_for_all_local_ranks():
        backend = str(getattr(env_cfg, "cpu_backend", "gloo"))
    timeout_seconds = int(getattr(env_cfg, "timeout_seconds", 1800))
    dist.init_process_group(backend=backend, timeout=timedelta(seconds=timeout_seconds))


def cleanup_distributed() -> None:
    if dist.is_available() and dist.is_initialized():
        dist.destroy_process_group()


def get_rank() -> int:
    if dist.is_available() and dist.is_initialized():
        return dist.get_rank()
    return int(os.environ.get("RANK", "0"))


def get_world_size() -> int:
    if dist.is_available() and dist.is_initialized():
        return dist.get_world_size()
    return int(os.environ.get("WORLD_SIZE", "1"))


def get_local_rank() -> int:
    return int(os.environ.get("LOCAL_RANK", "0"))


def is_main_process() -> bool:
    return get_rank() == 0


def get_device() -> torch.device:
    if _can_use_cuda_for_all_local_ranks():
        device = torch.device(f"cuda:{get_local_rank()}")
        torch.cuda.set_device(device)
        return device
    return torch.device("cpu")


def all_gather_list(local_values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not (dist.is_available() and dist.is_initialized()):
        return local_values
    gathered: list[list[dict[str, Any]] | None] = [None for _ in range(dist.get_world_size())]
    dist.all_gather_object(gathered, local_values)
    merged: list[dict[str, Any]] = []
    for shard in gathered:
        if shard:
            merged.extend(shard)
    return merged
