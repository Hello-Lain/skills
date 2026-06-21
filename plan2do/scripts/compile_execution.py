#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


TASK_HEADING_RE = re.compile(r"^###\s+Task\s+(\d+):\s*(.+?)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^\s*-\s+([^:\n]+):\s*(.*)$")
CODE_RE = re.compile(r"`([^`]+)`")

REQUIRED_FIELDS = [
    "Description",
    "Worker role",
    "Wave",
    "Acceptance criteria",
    "Verification",
    "Concrete edits",
    "Interfaces / contracts changed",
    "Test cases",
    "Pre-check commands",
    "Post-check commands",
    "Dependencies",
    "Files likely touched",
    "Writable scope",
    "Output artifact",
    "Estimated scope",
]

VALID_ROLES = {"coding", "devops", "review", "consult", "sa"}
VALID_SIZES = {"XS", "S", "M", "L"}
VALID_STATUSES = {"pending", "complete", "blocked"}


def _label(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _clean(text: str) -> str:
    value = text.strip()
    if value.startswith("`") and value.endswith("`") and value.count("`") == 2:
        return value.strip("`").strip()
    return value


def _task_blocks(text: str) -> list[tuple[int, str, str]]:
    matches = list(TASK_HEADING_RE.finditer(text))
    blocks: list[tuple[int, str, str]] = []
    for index, match in enumerate(matches):
        next_task = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        next_section = re.search(r"^##\s+", text[match.end() :], re.MULTILINE)
        section_end = match.end() + next_section.start() if next_section else len(text)
        end = min(next_task, section_end)
        blocks.append((int(match.group(1)), match.group(2).strip(), text[match.end() : end]))
    return blocks


def _parse_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal current, buffer
        if current is not None:
            fields[current] = "\n".join(buffer).strip()
        current = None
        buffer = []

    for line in block.splitlines():
        if line.startswith("## ") or line.startswith("### "):
            break
        match = FIELD_RE.match(line)
        if match:
            flush()
            current = _label(match.group(1))
            buffer = [match.group(2).rstrip()]
            continue
        if current is not None:
            buffer.append(line.rstrip())
    flush()
    return fields


def _paths(value: str) -> list[str]:
    code_paths = [item.strip() for item in CODE_RE.findall(value) if item.strip()]
    if code_paths:
        return code_paths
    paths: list[str] = []
    for chunk in re.split(r"[;\n]", value):
        item = chunk.strip().lstrip("-").strip()
        if item and item.lower() not in {"none", "not applicable", "n/a", "na"}:
            paths.append(item)
    return paths


def _dependencies(value: str) -> list[int]:
    lowered = value.lower()
    if not value.strip() or any(token in lowered for token in ("none", "not applicable", "n/a", "na")):
        return []
    deps: list[int] = []
    for match in re.finditer(r"\bTask\s*(\d+)\b|\b#(\d+)\b", value, re.IGNORECASE):
        number = int(match.group(1) or match.group(2))
        if number not in deps:
            deps.append(number)
    return deps


def _wave(value: str) -> int | None:
    match = re.search(r"\b(?:wave\s*)?(\d+)\b", value, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _repo_root_from_workspace(workspace: Path) -> Path:
    parts = workspace.resolve().parts
    for index, part in enumerate(parts):
        if part == ".codex" and index + 1 < len(parts) and parts[index + 1] == "work":
            return Path(*parts[:index]) if index else Path("/")
    return workspace


def _resolve_path(path_text: str, workspace: Path, repo_root: Path) -> str:
    path = Path(path_text)
    if path.is_absolute():
        return str(path)
    if path_text.startswith(".codex/"):
        return str((repo_root / path_text).resolve())
    return str((workspace / path).resolve())


def _review_output_artifact_errors(
    number: int,
    role: str,
    output_paths: list[str],
    fields: dict[str, str],
) -> list[str]:
    if role != "review":
        return []

    errors: list[str] = []
    task_text = "\n".join(fields.values())
    for path_text in output_paths:
        if _is_review_artifact_path(path_text) or _requires_standalone_verdict(task_text):
            continue
        errors.append(
            f"Task {number} review Output artifact must be .codex/work/<topic>/review*.md "
            f"or task text must explicitly require a standalone Verdict: PASS or Verdict: FAIL in that artifact: {path_text}"
        )
    return errors


def _is_review_artifact_path(path_text: str) -> bool:
    path = Path(path_text)
    return (
        not path.is_absolute()
        and len(path.parts) >= 3
        and path.parts[0] == ".codex"
        and path.parts[1] == "work"
        and path.name.startswith("review")
        and path.suffix == ".md"
    )


def _requires_standalone_verdict(text: str) -> bool:
    return bool(
        re.search(r"(?is)\bstandalone\b.*\bVerdict\s*:\s*PASS\b.*\bVerdict\s*:\s*FAIL\b", text)
        or re.search(r"(?is)\bVerdict\s*:\s*PASS\b.*\bVerdict\s*:\s*FAIL\b.*\bstandalone\b", text)
    )


def compile_plan(plan_path: Path) -> dict:
    if not plan_path.exists():
        raise ValueError(f"plan not found: {plan_path}")

    workspace = plan_path.resolve().parent
    repo_root = _repo_root_from_workspace(workspace)
    text = plan_path.read_text(encoding="utf-8")
    blocks = _task_blocks(text)
    if not blocks:
        raise ValueError("no task blocks found; expected headings like '### Task 1: ...'")

    tasks: list[dict] = []
    all_numbers: set[int] = set()
    errors: list[str] = []

    for number, title, block in blocks:
        all_numbers.add(number)
        fields = _parse_fields(block)
        missing = [name for name in REQUIRED_FIELDS if not fields.get(_label(name), "").strip()]
        if missing:
            errors.append(f"Task {number} missing required fields: {', '.join(missing)}")
            continue

        role = _clean(fields[_label("Worker role")]).lower()
        if role not in VALID_ROLES:
            errors.append(f"Task {number} invalid Worker role: {role}")

        wave = _wave(fields[_label("Wave")])
        if wave is None:
            errors.append(f"Task {number} invalid Wave: {fields[_label('Wave')]}")

        estimated_scope = _clean(fields[_label("Estimated scope")]).upper()
        if estimated_scope not in VALID_SIZES:
            errors.append(f"Task {number} invalid Estimated scope: {estimated_scope}")

        output_paths = _paths(fields[_label("Output artifact")])
        if not output_paths:
            errors.append(f"Task {number} has no parseable Output artifact")
            continue
        errors.extend(_review_output_artifact_errors(number, role, output_paths, fields))

        writable_scope = _paths(fields[_label("Writable scope")])
        if not writable_scope:
            errors.append(f"Task {number} has no parseable Writable scope")

        tasks.append(
            {
                "number": number,
                "title": title,
                "role": role,
                "wave": wave,
                "dependencies": _dependencies(fields[_label("Dependencies")]),
                "status": "pending",
                "acceptance_criteria": _clean(fields[_label("Acceptance criteria")]),
                "verification": _clean(fields[_label("Verification")]),
                "pre_check_commands": _clean(fields[_label("Pre-check commands")]),
                "post_check_commands": _clean(fields[_label("Post-check commands")]),
                "files_likely_touched": _paths(fields[_label("Files likely touched")]),
                "writable_scope": writable_scope,
                "output_artifact": output_paths[0],
                "output_artifact_path": _resolve_path(output_paths[0], workspace, repo_root),
                "estimated_scope": estimated_scope,
            }
        )

    for task in tasks:
        missing_deps = [dep for dep in task["dependencies"] if dep not in all_numbers]
        if missing_deps:
            errors.append(f"Task {task['number']} depends on missing task(s): {missing_deps}")

    if errors:
        raise ValueError("\n".join(errors))

    return {
        "schema_version": 1,
        "status": "compiled",
        "plan_path": str(plan_path.resolve()),
        "workspace": str(workspace),
        "task_count": len(tasks),
        "tasks": sorted(tasks, key=lambda item: item["number"]),
    }


def _preserve_statuses(state: dict, output: Path) -> None:
    if not output.exists():
        return
    try:
        existing = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    statuses = {
        item.get("number"): item.get("status")
        for item in existing.get("tasks", [])
        if item.get("status") in VALID_STATUSES
    }
    for task in state["tasks"]:
        status = statuses.get(task["number"])
        if status:
            task["status"] = status


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile a spec2plan plan.md into a plan2do execution task state.")
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output", type=Path, help="Override output path; defaults to <plan-workspace>/execution/tasks.json")
    parser.add_argument("--reset-status", action="store_true", help="Reset task statuses to pending instead of preserving an existing tasks.json")
    args = parser.parse_args()

    try:
        state = compile_plan(args.plan)
    except ValueError as exc:
        for line in str(exc).splitlines():
            print(f"ERROR: {line}", file=sys.stderr)
        return 1

    output = args.output or (Path(state["workspace"]) / "execution" / "tasks.json")
    if not args.reset_status:
        _preserve_statuses(state, output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
