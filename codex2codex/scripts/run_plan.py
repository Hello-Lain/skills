#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from execution_state import record_plan_compile, record_plan_result
from roles import ALLOWED_CONTEXT_PROFILES


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def _bounded_nonnegative_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 0 or parsed > 3:
        raise argparse.ArgumentTypeError("must be between 0 and 3")
    return parsed


def _compile_plan(plan_path: Path, spec_dir: Path | None, force: bool, add_review: bool) -> dict:
    script = Path(__file__).with_name("plan_to_tasks.py")
    cmd = [sys.executable, str(script), str(plan_path), "--json"]
    if spec_dir:
        cmd.extend(["--spec-dir", str(spec_dir)])
    if force:
        cmd.append("--force")
    if add_review:
        cmd.append("--add-review")
    proc = _run(cmd)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout)
        raise SystemExit(proc.returncode)
    return json.loads(proc.stdout)


def _run_wave(spec_dir: Path, wave: str, args: argparse.Namespace) -> int:
    script = Path(__file__).with_name("run_wave.py")
    cmd = [
        sys.executable,
        str(script),
        "--spec-dir",
        str(spec_dir),
        "--wave",
        wave,
        "--profile",
        args.profile,
        "--timeout",
        str(args.timeout),
        "--meight",
        args.meight,
    ]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.keep_home:
        cmd.append("--keep-home")
    if args.skip_validate:
        cmd.append("--skip-validate")
    if args.no_update_tasks:
        cmd.append("--no-update-tasks")
    if args.no_fix_wave:
        cmd.append("--no-fix-wave")
    if args.auto_run_fix:
        cmd.append("--auto-run-fix")
        cmd.extend(["--max-fix-cycles", str(args.max_fix_cycles)])
    cmd.extend(["--same-worker-restarts", str(args.same_worker_restarts)])
    cmd.extend(["--fresh-worker-restarts", str(args.fresh_worker_restarts)])
    cmd.extend(["--same-thread-continues", str(args.same_thread_continues)])
    if args.no_preflight:
        cmd.append("--no-preflight")
    cmd.extend(["--preflight-timeout", str(args.preflight_timeout)])
    proc = subprocess.run(cmd, text=True, check=False)
    return proc.returncode


def main_with_args(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile plan.md into codex2codex waves, then dry-run or execute them.")
    parser.add_argument("plan_path", type=Path)
    parser.add_argument("--spec-dir", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--add-review", action="store_true", default=True)
    parser.add_argument("--no-add-review", dest="add_review", action="store_false")
    parser.add_argument("--profile", choices=ALLOWED_CONTEXT_PROFILES, default="role")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--meight", default="meight")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-home", action="store_true")
    parser.add_argument("--skip-validate", action="store_true")
    parser.add_argument("--no-update-tasks", action="store_true")
    parser.add_argument("--no-fix-wave", action="store_true")
    parser.add_argument("--auto-run-fix", action="store_true")
    parser.add_argument("--max-fix-cycles", type=int, default=1)
    parser.add_argument("--same-worker-restarts", type=_bounded_nonnegative_int, default=1)
    parser.add_argument("--fresh-worker-restarts", type=_bounded_nonnegative_int, default=1)
    parser.add_argument("--same-thread-continues", type=_bounded_nonnegative_int, default=3)
    parser.add_argument("--no-preflight", action="store_true")
    parser.add_argument("--preflight-timeout", type=int, default=30)
    args = parser.parse_args(argv)

    dry_run_dir: Path | None = None
    spec_dir_arg = args.spec_dir
    if args.dry_run:
        dry_run_dir = Path(tempfile.mkdtemp(prefix=f"run-plan-dry-{args.plan_path.stem}-"))
        spec_dir_arg = dry_run_dir / "spec"

    try:
        compiled = _compile_plan(args.plan_path, spec_dir_arg, args.force, args.add_review)
        spec_dir = Path(compiled["spec_dir"])
        record_plan_compile(
            spec_dir,
            plan_path=args.plan_path,
            tasks_path=compiled["tasks_path"],
            waves=compiled["waves"],
            dry_run=args.dry_run,
        )
        if args.dry_run:
            print("COMPILE ONLY - NOT A QUALITY GATE")
        print(f"compiled tasks: {compiled['tasks_path']}")
        exit_code = 0
        for wave in compiled["waves"]:
            print(f"== {wave} ==")
            code = _run_wave(spec_dir, wave, args)
            if code != 0:
                exit_code = code
                break
        record_plan_result(spec_dir, exit_code=exit_code, dry_run=args.dry_run)
        return exit_code
    finally:
        if dry_run_dir:
            shutil.rmtree(dry_run_dir, ignore_errors=True)


def main() -> int:
    return main_with_args()


if __name__ == "__main__":
    raise SystemExit(main())
