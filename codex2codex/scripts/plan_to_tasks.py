#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from roles import IMPLEMENT_ROLES, RoleError, normalize_role

TASK_HEADING_RE = re.compile(r"(?m)^###\s+Task\s+(\d+)\s*:\s*(.+?)\s*$")
FIELD_RE = re.compile(r"(?ms)^\s*-\s*([^:\n]+?)\s*:\s*(.*?)(?=^\s*-\s*[^:\n]+?\s*:|\Z)")
CODE_RE = re.compile(r"`([^`]+)`")
TASK_NUM_RE = re.compile(r"\bTask\s*(\d+)\b|\b#?(\d+)\b", re.I)

@dataclass
class PlanTask:
    number: int
    title: str
    role: str
    files: list[str]
    verify: str
    output: str
    dependencies: list[int]
    wave: int | None


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "plan"


def _field(block: str, name: str) -> str:
    wanted = re.sub(r"\s+", " ", name.strip().lower())
    for match in FIELD_RE.finditer(block):
        label = re.sub(r"\s+", " ", match.group(1).strip().lower())
        if label == wanted:
            return match.group(2).strip()
    return ""


def _clean_inline(value: str) -> str:
    code_spans = [item.strip() for item in CODE_RE.findall(value) if item.strip()]
    if len(code_spans) == 1 and value.strip() == f"`{code_spans[0]}`":
        return code_spans[0]
    lines = [line.strip().lstrip("-").strip() for line in value.splitlines()]
    lines = [line for line in lines if line]
    text = "; ".join(lines).strip()
    if text.startswith("`") and text.endswith("`") and text.count("`") == 2:
        return text.strip("`")
    return text


def _paths(value: str) -> list[str]:
    found = [path.strip() for path in CODE_RE.findall(value) if path.strip()]
    if not found:
        for line in value.splitlines():
            item = line.strip().lstrip("-").strip()
            if item and item.lower() not in {"none", "not applicable", "n/a", "na"}:
                found.append(item)
    unique: list[str] = []
    for path in found:
        if path not in unique:
            unique.append(path)
    return unique


def _role(value: str, title: str) -> str:
    try:
        return normalize_role(value, title)
    except RoleError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc


def _deps(value: str) -> list[int]:
    lowered = value.lower()
    if not value.strip() or any(word in lowered for word in ("none", "not applicable", "n/a", "na")):
        return []
    deps: list[int] = []
    for match in TASK_NUM_RE.finditer(value):
        number = int(match.group(1) or match.group(2))
        if number not in deps:
            deps.append(number)
    return deps


def _wave(value: str) -> int | None:
    match = re.search(r"\b(?:wave\s*)?(\d+)\b", value, re.I)
    return int(match.group(1)) if match else None


def parse_plan(plan_path: Path, spec_dir: Path) -> list[PlanTask]:
    text = plan_path.read_text(encoding="utf-8")
    matches = list(TASK_HEADING_RE.finditer(text))
    tasks: list[PlanTask] = []
    for index, match in enumerate(matches):
        number = int(match.group(1))
        title = match.group(2).strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.end() : end]
        role = _role(_field(block, "Worker role"), title)
        files = _paths(_field(block, "Writable scope")) or _paths(_field(block, "Files likely touched"))
        verify = _clean_inline(_field(block, "Verification")) or "Not specified"
        output = _paths(_field(block, "Output artifact"))
        output_path = output[0] if output else str(spec_dir / "artifacts" / f"task-{number}-{_slug(title)}.md")
        tasks.append(
            PlanTask(
                number=number,
                title=title,
                role=role,
                files=files,
                verify=verify,
                output=output_path,
                dependencies=_deps(_field(block, "Dependencies")),
                wave=_wave(_field(block, "Wave")),
            )
        )
    return tasks


def assign_waves(tasks: list[PlanTask]) -> dict[int, list[PlanTask]]:
    by_number = {task.number: task for task in tasks}
    assigned: dict[int, int] = {}
    waves: dict[int, list[PlanTask]] = {}

    for task in sorted(tasks, key=lambda item: item.number):
        min_wave = 1
        for dep in task.dependencies:
            min_wave = max(min_wave, assigned.get(dep, 1) + 1)
        wave = max(task.wave or min_wave, min_wave)
        while task.role in IMPLEMENT_ROLES and _overlaps_existing(task, waves.get(wave, [])):
            wave += 1
        assigned[task.number] = wave
        waves.setdefault(wave, []).append(task)

    missing = sorted({dep for task in tasks for dep in task.dependencies if dep not in by_number})
    if missing:
        raise SystemExit(f"ERROR: dependencies refer to missing tasks: {', '.join(map(str, missing))}")
    return dict(sorted(waves.items()))


def _overlaps_existing(task: PlanTask, peers: list[PlanTask]) -> bool:
    if task.role not in IMPLEMENT_ROLES:
        return False
    files = set(task.files)
    for peer in peers:
        if peer.role in IMPLEMENT_ROLES and files.intersection(peer.files):
            return True
    return False


def _task_line(task: PlanTask) -> str:
    files = ", ".join(f"`{path}`" for path in task.files) if task.files else "`NO_WRITABLE_SCOPE_DECLARED`"
    return (
        f"- [ ] [{task.role}] Task {task.number}: {task.title} | {files} | "
        f"Verify: `{task.verify}` Output: `{task.output}`"
    )


def _add_review(waves: dict[int, list[PlanTask]], spec_dir: Path) -> None:
    if any(task.role == "review" for tasks in waves.values() for task in tasks):
        return
    touched: list[str] = []
    for task in [task for tasks in waves.values() for task in tasks if task.role in IMPLEMENT_ROLES]:
        for path in task.files:
            if path not in touched:
                touched.append(path)
    if not touched:
        return
    next_task = max(task.number for tasks in waves.values() for task in tasks) + 1
    next_wave = max(waves) + 1 if waves else 1
    waves.setdefault(next_wave, []).append(
        PlanTask(
            number=next_task,
            title="Review implementation outputs",
            role="review",
            files=touched,
            verify="inspect changed files and rerun relevant verification commands",
            output=str(spec_dir / "review.md"),
            dependencies=[],
            wave=next_wave,
        )
    )


def write_tasks(plan_path: Path, spec_dir: Path, tasks: list[PlanTask], add_review: bool, force: bool) -> dict:
    if not tasks:
        raise SystemExit("ERROR: plan contains no ### Task N: sections")
    for task in tasks:
        if task.role in IMPLEMENT_ROLES and not task.files:
            raise SystemExit(f"ERROR: Task {task.number} has no Writable scope or Files likely touched")
        if task.verify.lower().strip() == "not specified":
            raise SystemExit(f"ERROR: Task {task.number} has no Verification")
    spec_dir.mkdir(parents=True, exist_ok=True)
    tasks_path = spec_dir / "tasks.md"
    if tasks_path.exists() and not force:
        raise SystemExit(f"ERROR: {tasks_path} exists; pass --force to overwrite")

    waves = assign_waves(tasks)
    if add_review:
        _add_review(waves, spec_dir)

    spec_path = spec_dir / "spec.md"
    if not spec_path.exists() or force:
        spec_path.write_text(
            f"# Spec Source\n\nAuthoritative plan: `{plan_path}`\n\n"
            "Generated for codex2codex plan orchestration.\n",
            encoding="utf-8",
        )

    lines = [
        f"# Codex2Codex Tasks: {plan_path.stem}",
        "",
        f"Source plan: `{plan_path}`",
        "",
    ]
    wave_names: list[str] = []
    for wave_num, wave_tasks in waves.items():
        wave_name = f"Wave {wave_num}"
        wave_names.append(wave_name)
        lines.extend([f"## {wave_name}", ""])
        lines.extend(_task_line(task) for task in wave_tasks)
        lines.append("")
    tasks_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"spec_dir": str(spec_dir), "tasks_path": str(tasks_path), "waves": wave_names, "task_count": sum(len(v) for v in waves.values())}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile spec2plan plan.md into codex2codex tasks.md waves.")
    parser.add_argument("plan_path", type=Path)
    parser.add_argument("--spec-dir", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--add-review", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    plan_path = args.plan_path.resolve()
    spec_dir = args.spec_dir or (plan_path.parent / ".codex" / "specs" / _slug(plan_path.stem))
    tasks = parse_plan(plan_path, spec_dir)
    result = write_tasks(plan_path, spec_dir, tasks, args.add_review, args.force)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result["tasks_path"])
        for wave in result["waves"]:
            print(wave)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
