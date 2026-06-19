#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STATE_FILE = "execution-state.json"
VERDICT_RE = re.compile(r"^\s*(?:-\s*)?(?:#{1,6}\s*)?Verdict\s*:?\s*`?(PASS|FAIL)?`?\.?\s*$", re.I)


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"ERROR: cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON {path}: {exc}") from exc


def _review_verdict(text: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = VERDICT_RE.match(line)
        if not match:
            continue
        if match.group(1):
            return match.group(1).upper()
        for next_line in lines[index + 1 :]:
            value = next_line.strip().strip("`").rstrip(".").upper()
            if value in {"PASS", "FAIL"}:
                return value
            if value:
                break
    return "UNKNOWN"


def _artifact_exists(path_text: str) -> bool:
    return bool(path_text and Path(path_text).exists() and Path(path_text).read_text(encoding="utf-8").strip())


def validate(spec_dir: Path, *, require_review: bool = True) -> list[str]:
    state_path = spec_dir / STATE_FILE
    if not state_path.exists():
        return [f"missing execution state: {state_path}"]
    state = _load_json(state_path)
    errors: list[str] = []
    plan = state.get("plan") or {}
    waves = state.get("waves") or {}
    expected_waves = plan.get("waves") or []

    if plan.get("dry_run"):
        errors.append("dry-run compile state is not an execution quality gate")
    if plan.get("status") not in {"compiled", "success"}:
        errors.append(f"plan status is not executable complete: {plan.get('status') or 'missing'}")
    if not expected_waves:
        errors.append("plan has no recorded waves")

    saw_implementation = False
    saw_review_pass = False
    for wave in expected_waves:
        receipt = waves.get(wave)
        if not receipt:
            errors.append(f"missing execution receipt for wave: {wave}")
            continue
        if receipt.get("status") != "success" or receipt.get("exit_code") != 0:
            errors.append(f"wave did not succeed: {wave}")
        cleanup = receipt.get("cleanup") or {}
        if not cleanup.get("shutdown_attempted"):
            errors.append(f"wave cleanup not recorded: {wave}")
        if not cleanup.get("shutdown_ok"):
            errors.append(f"wave shutdown did not succeed: {wave}")
        for worker in receipt.get("workers") or []:
            mode = worker.get("mode")
            output = worker.get("output") or ""
            summary_path = worker.get("summary_path") or ""
            if mode != "review":
                saw_implementation = True
            if output and not _artifact_exists(output):
                errors.append(f"missing worker output artifact: {output}")
            if not summary_path or not Path(summary_path).exists():
                errors.append(f"missing worker provenance summary: {worker.get('name') or '<unknown>'}")
            if mode == "review":
                if not output or not Path(output).exists():
                    errors.append(f"missing review artifact: {output or worker.get('name') or '<unknown>'}")
                    continue
                verdict = _review_verdict(Path(output).read_text(encoding="utf-8"))
                if verdict == "PASS":
                    saw_review_pass = True
                elif verdict == "FAIL":
                    errors.append(f"review verdict FAIL: {output}")
                else:
                    errors.append(f"missing review PASS verdict: {output}")

    if require_review and saw_implementation and not saw_review_pass:
        errors.append("missing required review PASS")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate that codex2codex execution, review, and cleanup actually completed.")
    parser.add_argument("spec_dir", type=Path)
    parser.add_argument("--allow-missing-review", action="store_true")
    args = parser.parse_args()

    errors = validate(args.spec_dir, require_review=not args.allow_missing_review)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
