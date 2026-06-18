#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

TASK_RE = re.compile(
    r"^\s*-\s*\[(?P<mark>[ xX])\]\s*\[(?P<role>[^\]]+)\]\s*"
    r"(?P<title>.*?)\s*\|\s*(?P<files>.*?)\s*\|\s*(?P<rest>.*)$"
)
WAVE_RE = re.compile(r"^##\s+(?P<name>.+?)\s*$")
VERIFY_RE = re.compile(r"Verify:\s*(?P<verify>.*?)(?:\s+Output:\s*(?P<output>.*))?$", re.I)
OUTPUT_RE = re.compile(r"Output:\s*(?P<output>.*)$", re.I)
PATH_RE = re.compile(r"`([^`]+)`")

ROLE_MODE = {
    "coding": ("implement", "ws", "medium"),
    "devops": ("implement", "ws", "medium"),
    "review": ("review", "ws", "medium"),
    "sa": ("consult", "ro", "high"),
    "consult": ("consult", "ro", "medium"),
}


@dataclass
class Task:
    completed: bool
    role: str
    title: str
    files: list[str]
    verify: str
    output: str
    raw: str


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "wave"


def _extract_paths(text: str) -> list[str]:
    paths = PATH_RE.findall(text)
    if paths:
        return paths
    return [part.strip() for part in text.split(",") if part.strip()]


def _first_code_span(text: str) -> str:
    paths = PATH_RE.findall(text)
    stripped = text.strip()
    if len(paths) == 1 and stripped == f"`{paths[0]}`":
        return paths[0].strip()
    return stripped


def _split_verify(rest: str) -> tuple[str, str]:
    match = VERIFY_RE.search(rest)
    if match:
        verify = _first_code_span(match.group("verify") or "")
        output = _first_code_span(match.group("output") or "")
        return verify, output
    output_match = OUTPUT_RE.search(rest)
    if output_match:
        return "", _first_code_span(output_match.group("output"))
    return rest.strip(), ""


def parse_tasks(tasks_path: Path, wave_name: str, include_completed: bool = False) -> list[Task]:
    current_wave = None
    tasks: list[Task] = []
    for line in tasks_path.read_text(encoding="utf-8").splitlines():
        wave_match = WAVE_RE.match(line)
        if wave_match:
            current_wave = wave_match.group("name")
            continue
        if current_wave != wave_name:
            continue
        task_match = TASK_RE.match(line)
        if not task_match:
            continue
        completed = task_match.group("mark").lower() == "x"
        if completed and not include_completed:
            continue
        verify, output = _split_verify(task_match.group("rest"))
        tasks.append(
            Task(
                completed=completed,
                role=task_match.group("role").strip(),
                title=task_match.group("title").strip(),
                files=_extract_paths(task_match.group("files")),
                verify=verify,
                output=output,
                raw=line.strip(),
            )
        )
    return tasks


def _review_output(spec_dir: Path, index: int, task: Task) -> str:
    if task.output:
        return _first_code_span(task.output)
    if len([file for file in task.files if file.startswith("review")]) == 1:
        return task.files[0]
    suffix = _slug(task.title) or f"review-{index}"
    return str(spec_dir / f"review-{suffix}.md")


def _check_overlap(tasks: list[Task]) -> list[str]:
    owners: dict[str, str] = {}
    errors: list[str] = []
    for index, task in enumerate(tasks, 1):
        role_key = task.role.lower().strip()
        mode = ROLE_MODE.get(role_key, ("implement", "ws", "medium"))[0]
        if mode in {"review", "consult"}:
            continue
        owner = f"{role_key}-{index}"
        for file_path in task.files:
            prior = owners.get(file_path)
            if prior:
                errors.append(f"write-scope overlap: {file_path} owned by {prior} and {owner}")
            owners[file_path] = owner
    return errors


def _profile_text(profile: str) -> str:
    if profile == "full":
        return "Use normal project context if needed, but avoid raw logs/transcripts."
    return (
        "Use minimal context: read only Spec, Task, listed File scope, and directly related tests. "
        "Do not load unrelated skills, MCP tool inventories, histories, large logs, or generated caches."
    )


def _brief(spec_dir: Path, wave: str, task: Task, index: int, output: str, mode: str, profile: str) -> str:
    instance = f"{task.role.lower().strip()}-{index}"
    restrictions = "no commit, no push, no user communication, no /codex2codex recursion"
    if mode == "review":
        restrictions += "; do not modify product files; write only the requested review artifact"
    return "\n".join(
        [
            f"Use role: {task.role}-agent",
            f"Instance: {instance}",
            f"Spec: {spec_dir / 'spec.md'}",
            f"Wave: {wave}",
            f"File scope: {', '.join(task.files)}",
            f"Task: {task.title}",
            f"Verify: {task.verify or 'Not specified'}",
            f"Output: {output}",
            f"Context profile: {_profile_text(profile)}",
            "Concurrency: peer workers may edit nearby files; stay inside scope.",
            f"Restrictions: {restrictions}.",
            "Do not include Skill Monitor sections unless a real skill incident affects this output.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate codex2codex worker briefs from codex-agent-team tasks.md.")
    parser.add_argument("--spec-dir", required=True, type=Path)
    parser.add_argument("--wave", required=True)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--profile", choices=("minimal", "full"), default="minimal")
    parser.add_argument("--include-completed", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    spec_dir = args.spec_dir
    tasks_path = spec_dir / "tasks.md"
    if not tasks_path.exists():
        print(f"ERROR: missing {tasks_path}", file=sys.stderr)
        return 1

    tasks = parse_tasks(tasks_path, args.wave, args.include_completed)
    if not tasks:
        print(f"ERROR: no tasks found for wave: {args.wave}", file=sys.stderr)
        return 1

    overlap_errors = _check_overlap(tasks)
    if overlap_errors:
        for error in overlap_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    out_dir = args.out_dir or (spec_dir / "generated" / _slug(args.wave))
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {"spec_dir": str(spec_dir), "wave": args.wave, "profile": args.profile, "workers": []}
    role_counts: dict[str, int] = {}
    for index, task in enumerate(tasks, 1):
        role_key = task.role.lower().strip()
        role_counts[role_key] = role_counts.get(role_key, 0) + 1
        role_index = role_counts[role_key]
        mode, sandbox, effort = ROLE_MODE.get(role_key, ("implement", "ws", "medium"))
        output = _review_output(spec_dir, role_index, task) if mode == "review" else task.output
        name = f"{role_key}-{role_index}"
        brief_path = out_dir / f"{name}.txt"
        brief_path.write_text(_brief(spec_dir, args.wave, task, role_index, output, mode, args.profile), encoding="utf-8")
        manifest["workers"].append(
            {
                "name": name,
                "role": task.role,
                "mode": mode,
                "sandbox": sandbox,
                "effort": effort,
                "files": task.files,
                "verify": task.verify,
                "output": output,
                "brief": str(brief_path),
                "raw_task": task.raw,
            }
        )

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
    else:
        print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
