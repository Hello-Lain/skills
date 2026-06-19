#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from scope_contract import normalize_contract_path, path_in_scope, scope_entries

BLOCKED_RE = re.compile(r"(?mi)^\s*(Blocked|Cannot complete|Unable to write|could not write)\b")
SKILL_MONITOR_RE = re.compile(r"(?mi)^Skill Monitor:")
VERDICT_RE = re.compile(r"^\s*(?:-\s*)?(?:#{1,6}\s*)?Verdict\s*:?\s*`?(PASS|FAIL)?`?\.?\s*$", re.I)
SALVAGED_RE = re.compile(r"(?mi)^Salvaged-From-Worker:\s+\S+")


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"ERROR: cannot read {path}: {exc}") from exc


def _worker_status(status_root: Path, name: str) -> dict:
    path = status_root / "workers" / name / "status.json"
    if not path.exists():
        return {"state": "missing", "path": str(path)}
    return _load_json(path)


def _worker_result(status_root: Path, name: str) -> str:
    path = status_root / "workers" / name / "result.md"
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _terminal_result(text: str) -> str:
    turns = list(re.finditer(r"(?m)^##\s+Turn\s+\d+\b.*$", text))
    if not turns:
        return text
    return text[turns[-1].end() :].strip()


def _artifact_path(repo_root: Path, output: str) -> Path:
    artifact = Path(output)
    if not artifact.is_absolute():
        artifact = (repo_root / artifact).resolve()
    return artifact


def _artifact_salvaged(repo_root: Path, output: str) -> bool:
    artifact = _artifact_path(repo_root, output)
    if not artifact.exists():
        return False
    try:
        return bool(SALVAGED_RE.search(artifact.read_text(encoding="utf-8")))
    except OSError:
        return False


def _repo_relative_path(repo_root: Path, path_text: str) -> str:
    try:
        return normalize_contract_path(path_text, repo_root)
    except ValueError:
        return path_text


def _validate_implementation_evidence(repo_root: Path, worker: dict, status: dict) -> list[str]:
    scope = scope_entries(repo_root, [path for path in worker.get("files", []) if path])
    if not scope:
        return []
    changed = [path for path in status.get("files_changed") or [] if path]
    if any(path_in_scope(changed_path, scope, repo_root) for changed_path in changed):
        return []
    return [f"missing expected implementation evidence: no scoped files_changed for {[path for path, _ in scope]}"]


def _validate_output_artifact(repo_root: Path, output: str) -> list[str]:
    if not output:
        return []
    artifact = _artifact_path(repo_root, output)
    if not artifact.exists():
        return [f"missing output artifact: {artifact}"]
    try:
        text = artifact.read_text(encoding="utf-8")
        if not text.strip():
            return [f"empty output artifact: {artifact}"]
    except OSError as exc:
        return [f"cannot read output artifact: {artifact}: {exc}"]
    if BLOCKED_RE.search(text):
        return [f"output artifact reports blocked: {artifact}"]
    return []


def _validate_review_artifact(validator: Path, artifact: Path) -> list[str]:
    if not artifact.exists():
        return [f"missing review artifact: {artifact}"]
    proc = subprocess.run(
        [sys.executable, str(validator), "--require-review", str(artifact)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        return [f"invalid review artifact: {artifact}: {detail}"]
    text = artifact.read_text(encoding="utf-8")
    verdict = _review_verdict(text)
    if verdict == "FAIL":
        return [f"review verdict FAIL: {artifact}"]
    return []


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
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a completed codex2codex wave against manifest artifacts.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--meight-home", required=True, type=Path)
    parser.add_argument(
        "--validator",
        type=Path,
        default=Path(__file__).with_name("validate_result_contract.py"),
    )
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    spec_dir = Path(manifest["spec_dir"])
    repo_root = spec_dir.parents[2] if len(spec_dir.parents) >= 3 and spec_dir.parent.name == "specs" else Path.cwd()
    errors: list[str] = []
    warnings: list[str] = []

    for worker in manifest.get("workers", []):
        name = worker["name"]
        status = _worker_status(args.meight_home, name)
        state = status.get("state")
        artifact_salvaged = bool(worker.get("output") and _artifact_salvaged(repo_root, worker["output"]))
        if state != "completed" and not (state == "needs_input" and artifact_salvaged):
            errors.append(f"{name}: state is {state}, expected completed")

        result = _worker_result(args.meight_home, name)
        if not result.strip():
            errors.append(f"{name}: missing result.md")
        terminal_result = _terminal_result(result)
        if BLOCKED_RE.search(terminal_result) and not artifact_salvaged:
            errors.append(f"{name}: result reports blocked despite terminal state")
        if SKILL_MONITOR_RE.search(result):
            warnings.append(f"{name}: result contains Skill Monitor section; consider filtering worker output")

        if worker.get("mode") == "review":
            output = worker.get("output") or ""
            artifact = _artifact_path(repo_root, output)
            errors.extend(_validate_review_artifact(args.validator, artifact))
        else:
            errors.extend(_validate_output_artifact(repo_root, worker.get("output") or ""))
            errors.extend(f"{name}: {error}" for error in _validate_implementation_evidence(repo_root, worker, status))

    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
