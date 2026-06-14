#!/usr/bin/env python3
"""Select CUDA devices for shared two-GPU experiment scheduling."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import getpass
import json
import os
import pwd
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Iterable
from zoneinfo import ZoneInfo


SCRIPT_TZ = ZoneInfo("Asia/Shanghai")
NIGHT_START = dt.time(22, 0)
NIGHT_END = dt.time(8, 30)


@dataclass
class ProcessInfo:
    pid: int
    used_mb: int
    owner: str


@dataclass
class GpuInfo:
    index: int
    uuid: str
    total_mb: int
    used_mb: int
    free_mb: int
    util_pct: int
    processes: list[ProcessInfo] = field(default_factory=list)

    @property
    def other_processes(self) -> list[ProcessInfo]:
        current_user = getpass.getuser()
        return [process for process in self.processes if process.owner != current_user]

    @property
    def other_used_mb(self) -> int:
        return sum(process.used_mb for process in self.other_processes)

    @property
    def has_other_user(self) -> bool:
        return bool(self.other_processes)


def parse_int(value: str, default: int = 0) -> int:
    match = re.search(r"-?\d+", value or "")
    if not match:
        return default
    return int(match.group(0))


def run_nvidia_smi(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["nvidia-smi", *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("nvidia-smi not found; cannot verify GPU state") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise RuntimeError(f"nvidia-smi failed: {detail}") from exc
    return result.stdout


def parse_csv_rows(text: str) -> Iterable[list[str]]:
    for row in csv.reader(text.splitlines()):
        fields = [field.strip() for field in row]
        if not fields or not fields[0] or fields[0].lower().startswith("no running"):
            continue
        yield fields


def pid_owner(pid: int) -> str:
    try:
        uid = os.stat(f"/proc/{pid}").st_uid
        return pwd.getpwuid(uid).pw_name
    except (FileNotFoundError, KeyError, PermissionError):
        return "unknown"


def query_gpus() -> list[GpuInfo]:
    gpu_text = run_nvidia_smi(
        [
            "--query-gpu=index,uuid,memory.total,memory.used,memory.free,utilization.gpu",
            "--format=csv,noheader,nounits",
        ]
    )
    gpus: list[GpuInfo] = []
    uuid_to_gpu: dict[str, GpuInfo] = {}
    for fields in parse_csv_rows(gpu_text):
        if len(fields) < 6:
            continue
        util = parse_int(fields[5], default=100)
        gpu = GpuInfo(
            index=parse_int(fields[0]),
            uuid=fields[1],
            total_mb=parse_int(fields[2]),
            used_mb=parse_int(fields[3]),
            free_mb=parse_int(fields[4]),
            util_pct=util,
        )
        gpus.append(gpu)
        uuid_to_gpu[gpu.uuid] = gpu

    if not gpus:
        raise RuntimeError("No GPUs found in nvidia-smi output")

    try:
        app_text = run_nvidia_smi(
            [
                "--query-compute-apps=gpu_uuid,pid,used_memory",
                "--format=csv,noheader,nounits",
            ]
        )
    except RuntimeError:
        app_text = ""

    for fields in parse_csv_rows(app_text):
        if len(fields) < 3:
            continue
        gpu = uuid_to_gpu.get(fields[0])
        if gpu is None:
            continue
        pid = parse_int(fields[1], default=-1)
        if pid < 0:
            continue
        gpu.processes.append(
            ProcessInfo(pid=pid, used_mb=parse_int(fields[2]), owner=pid_owner(pid))
        )

    return sorted(gpus, key=lambda item: item.index)


def is_night(now: dt.datetime) -> bool:
    current = now.timetz().replace(tzinfo=None)
    return current >= NIGHT_START or current <= NIGHT_END


def load_key(gpu: GpuInfo) -> tuple[int, int, int, int]:
    other_flag = 1 if gpu.has_other_user else 0
    return (other_flag, gpu.other_used_mb or gpu.used_mb, gpu.util_pct, gpu.index)


def enough_memory(gpu: GpuInfo, min_free_mb: int) -> bool:
    return min_free_mb <= 0 or gpu.free_mb >= min_free_mb


def choose_gpus(gpus: list[GpuInfo], tasks: int, min_free_mb: int, now: dt.datetime) -> tuple[list[int], str]:
    candidates = [gpu for gpu in gpus if enough_memory(gpu, min_free_mb)]
    if not candidates:
        candidates = gpus[:]

    primary = sorted(candidates, key=load_key)
    two_gpu_pool = [gpu for gpu in gpus if enough_memory(gpu, min_free_mb)]
    low_two = sorted(two_gpu_pool, key=lambda item: item.index)[:2]
    night = is_night(now)

    if night and len(low_two) >= 2:
        return [gpu.index for gpu in low_two], "night-window: use both GPUs when memory is sufficient"

    if not primary:
        raise RuntimeError("No selectable GPUs")

    usable_low_two = sorted(candidates, key=lambda item: item.index)[:2]
    others_using = [gpu for gpu in usable_low_two if gpu.has_other_user]
    free_from_others = [gpu for gpu in usable_low_two if not gpu.has_other_user]

    if len(usable_low_two) >= 2 and not others_using:
        return [gpu.index for gpu in usable_low_two], "daytime: both GPUs are free from other users"

    if len(usable_low_two) >= 2 and len(others_using) == 1 and free_from_others:
        chosen = sorted(free_from_others, key=load_key)[0]
        return [chosen.index], "daytime: one GPU has another user; use the free GPU"

    chosen = primary[0]
    if len(others_using) >= 2:
        reason = "daytime: both GPUs have other users; choose lower-load GPU"
    else:
        reason = "daytime: choose lower-load single GPU"
    return [chosen.index], reason


def parse_now(raw: str | None) -> dt.datetime:
    if not raw:
        return dt.datetime.now(SCRIPT_TZ)
    parsed = dt.datetime.fromisoformat(raw)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=SCRIPT_TZ)
    return parsed.astimezone(SCRIPT_TZ)


def gpu_to_dict(gpu: GpuInfo) -> dict[str, object]:
    return {
        "index": gpu.index,
        "total_mb": gpu.total_mb,
        "used_mb": gpu.used_mb,
        "free_mb": gpu.free_mb,
        "util_pct": gpu.util_pct,
        "has_other_user": gpu.has_other_user,
        "processes": [
            {"pid": proc.pid, "owner": proc.owner, "used_mb": proc.used_mb}
            for proc in gpu.processes
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Select GPUs for local experiments.")
    parser.add_argument("--tasks", type=int, default=1, help="Number of GPU tasks to schedule.")
    parser.add_argument("--min-free-mb", type=int, default=0, help="Minimum free VRAM per selected GPU.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--now", help="Override current Asia/Shanghai time for tests, ISO format.")
    args = parser.parse_args()

    if args.tasks < 1:
        parser.error("--tasks must be >= 1")

    try:
        now = parse_now(args.now)
        gpus = query_gpus()
        selected, reason = choose_gpus(gpus, args.tasks, args.min_free_mb, now)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = {
        "selected": selected,
        "cuda_visible_devices": ",".join(str(index) for index in selected),
        "reason": reason,
        "night_window": is_night(now),
        "tasks": args.tasks,
        "min_free_mb": args.min_free_mb,
        "gpus": [gpu_to_dict(gpu) for gpu in gpus],
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"CUDA_VISIBLE_DEVICES={result['cuda_visible_devices']}")
        print(f"reason: {reason}")
        for gpu in gpus:
            owners = ",".join(proc.owner for proc in gpu.processes) or "none"
            print(
                f"gpu {gpu.index}: free={gpu.free_mb}MB used={gpu.used_mb}MB "
                f"util={gpu.util_pct}% other_user={gpu.has_other_user} owners={owners}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
