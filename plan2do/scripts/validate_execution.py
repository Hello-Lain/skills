#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


VERDICT_RE = re.compile(r"^\s*(?:[-*]\s*)?(?:#{1,6}\s*)?Verdict\s*:\s*`?(PASS|FAIL)`?\s*$", re.IGNORECASE)
COMPLETE_RE = re.compile(r"^\s*(?:[-*]\s*)?Status\s*:\s*`?COMPLETE`?\s*$", re.IGNORECASE | re.MULTILINE)
INCOMPLETE_RE = re.compile(r"^\s*(?:[-*]\s*)?Status\s*:\s*`?INCOMPLETE`?\s*$", re.IGNORECASE | re.MULTILINE)
EXEMPT_RE = re.compile(r"^\s*(?:[-*]\s*)?Review exemption\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON {path}: {exc}") from exc


def _nonempty(path: Path) -> bool:
    try:
        return path.exists() and path.is_file() and bool(path.read_text(encoding="utf-8").strip())
    except OSError:
        return False


def _task_path(task: dict, workspace: Path) -> Path:
    raw = task.get("output_artifact_path") or task.get("output_artifact") or ""
    path = Path(raw)
    return path if path.is_absolute() else workspace / path


def _review_verdict(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return "MISSING"
    for line in text.splitlines():
        match = VERDICT_RE.match(line)
        if match:
            return match.group(1).upper()
    return "UNKNOWN"


def _review_exempt(final_report: str) -> bool:
    match = EXEMPT_RE.search(final_report)
    if not match:
        return False
    value = match.group(1).strip().lower()
    return value not in {"", "none", "no", "not applicable", "n/a", "na"}


def _verification_evidence(workspace: Path, final_report: str) -> bool:
    artifacts = workspace / "artifacts"
    if artifacts.exists():
        for path in artifacts.glob("*verification*.md"):
            if _nonempty(path):
                return True
    return bool(re.search(r"^\s*(?:[-*]\s*)?Verification\b", final_report, re.IGNORECASE | re.MULTILINE))


def validate_workspace(workspace: Path, *, require_review: bool = True) -> list[str]:
    workspace = workspace.resolve()
    errors: list[str] = []
    state_path = workspace / "execution" / "tasks.json"
    final_report_path = workspace / "artifacts" / "final-report.md"

    if not state_path.exists():
        return [f"missing execution task state: {state_path}"]

    try:
        state = _load_json(state_path)
    except ValueError as exc:
        return [str(exc)]

    tasks = state.get("tasks")
    if state.get("schema_version") != 1:
        errors.append(f"unsupported execution schema_version: {state.get('schema_version')}")
    if state.get("status") != "compiled":
        errors.append(f"execution state status is not compiled: {state.get('status')}")
    if not isinstance(tasks, list) or not tasks:
        errors.append("execution state has no tasks")
        tasks = []

    review_paths: list[Path] = [workspace / "review.md", workspace / "artifacts" / "review.md"]
    for task in tasks:
        number = task.get("number", "<unknown>")
        artifact = _task_path(task, workspace)
        if not _nonempty(artifact):
            errors.append(f"missing or empty output artifact for task {number}: {artifact}")
        if task.get("role") == "review":
            review_paths.append(artifact)

    final_report = ""
    final_complete = False
    final_incomplete = False
    if not _nonempty(final_report_path):
        errors.append(f"missing or empty final report: {final_report_path}")
    else:
        final_report = final_report_path.read_text(encoding="utf-8")
        final_complete = bool(COMPLETE_RE.search(final_report))
        final_incomplete = bool(INCOMPLETE_RE.search(final_report))
        if not final_complete:
            errors.append(f"final report lacks 'Status: COMPLETE': {final_report_path}")
        if not _verification_evidence(workspace, final_report):
            errors.append("missing verification evidence: add a *verification*.md artifact or a Verification section in final report")

    for task in tasks:
        number = task.get("number", "<unknown>")
        status = str(task.get("status") or "").lower()
        if status == "complete":
            continue
        if status == "blocked" and final_incomplete and not final_complete:
            errors.append(f"task {number} is blocked; final success is not allowed")
            continue
        errors.append(f"task {number} status is not complete: {status or 'missing'}")

    if require_review and not _review_exempt(final_report):
        saw_pass = False
        existing_review = False
        for path in dict.fromkeys(review_paths):
            if not path.exists():
                continue
            existing_review = True
            verdict = _review_verdict(path)
            if verdict == "PASS":
                saw_pass = True
            elif verdict == "FAIL":
                errors.append(f"review verdict FAIL: {path}")
            elif verdict != "MISSING":
                errors.append(f"review artifact lacks Verdict: PASS or Verdict: FAIL: {path}")
        if not existing_review:
            errors.append(f"missing review artifact: expected one of {', '.join(str(path) for path in review_paths)}")
        elif not saw_pass:
            errors.append("missing required review Verdict: PASS")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate plan2do execution artifacts before final success.")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--allow-missing-review", action="store_true")
    args = parser.parse_args()

    errors = validate_workspace(args.workspace, require_review=not args.allow_missing_review)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
