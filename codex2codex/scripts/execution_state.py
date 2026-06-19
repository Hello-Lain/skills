#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

STATE_FILE = "execution-state.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def state_path(spec_dir: Path) -> Path:
    return spec_dir / STATE_FILE


def load_state(spec_dir: Path) -> dict:
    path = state_path(spec_dir)
    if not path.exists():
        return {"version": 1, "spec_dir": str(spec_dir), "plan": {}, "waves": {}, "history": []}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state = {"version": 1, "spec_dir": str(spec_dir), "plan": {}, "waves": {}, "history": []}
    state.setdefault("version", 1)
    state.setdefault("spec_dir", str(spec_dir))
    state.setdefault("plan", {})
    state.setdefault("waves", {})
    state.setdefault("history", [])
    return state


def save_state(spec_dir: Path, state: dict) -> Path:
    path = state_path(spec_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now_iso()
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def record_plan_compile(spec_dir: Path, *, plan_path: Path, tasks_path: str, waves: list[str], dry_run: bool) -> Path:
    state = load_state(spec_dir)
    state["plan"] = {
        "status": "compiled",
        "dry_run": dry_run,
        "plan_path": str(plan_path),
        "tasks_path": tasks_path,
        "waves": waves,
        "compiled_at": now_iso(),
    }
    state["history"].append({"event": "plan_compiled", "dry_run": dry_run, "at": now_iso()})
    return save_state(spec_dir, state)


def record_plan_result(spec_dir: Path, *, exit_code: int, dry_run: bool) -> Path:
    state = load_state(spec_dir)
    plan = state.setdefault("plan", {})
    plan["final_exit_code"] = exit_code
    plan["dry_run"] = dry_run
    plan["status"] = "dry-run" if dry_run else ("success" if exit_code == 0 else "failed")
    plan["completed_at"] = now_iso()
    state["history"].append({"event": "plan_result", "dry_run": dry_run, "exit_code": exit_code, "at": now_iso()})
    return save_state(spec_dir, state)


def record_wave_result(
    spec_dir: Path,
    *,
    wave: str,
    exit_code: int,
    validate_code: int,
    wait_code: int,
    run_dir: Path,
    workers: list[dict],
    cleanup: dict,
    fix_waves: list[str] | None = None,
) -> Path:
    state = load_state(spec_dir)
    state.setdefault("waves", {})[wave] = {
        "status": "success" if exit_code == 0 else "failed",
        "exit_code": exit_code,
        "validate_code": validate_code,
        "wait_code": wait_code,
        "run_dir": str(run_dir),
        "workers": workers,
        "cleanup": cleanup,
        "fix_waves": fix_waves or [],
        "completed_at": now_iso(),
    }
    state["history"].append({"event": "wave_result", "wave": wave, "exit_code": exit_code, "at": now_iso()})
    return save_state(spec_dir, state)
