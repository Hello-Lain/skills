#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REQUIRED_HEADINGS = (
    "Goal",
    "Non-Goals",
    "Evidence Inspected",
    "Spec Summary",
    "Domain Language Check",
    "Current Context",
    "Assumptions",
    "User Inputs Needed",
    "Proposed Approach",
    "Scenario Probes",
    "Dependency Graph",
    "Task Breakdown",
    "Step-by-Step Plan",
    "Parallelization",
    "Files / Components Likely Affected",
    "Owners / Responsibilities",
    "Validation Plan",
    "Rollout Plan",
    "Monitoring / Observability",
    "Documentation / ADR Updates",
    "Rollback / Recovery Plan",
    "Abort Criteria",
    "Risks",
    "Open Questions",
    "Execution Decision",
)

HANDOFF_LABELS = (
    "Goal",
    "Current state",
    "Authoritative artifacts",
    "Decisions",
    "Verification",
    "Remaining risks",
    "Next action",
    "Suggested skills",
    "Redactions / omitted raw data",
)

SUBAGENT_PHASES = ("planner", "reviewer", "synthesizer")
ARTIFACT_START = "SPEC2PLAN_ARTIFACT_V1"
ARTIFACT_END = "SPEC2PLAN_ARTIFACT_END"

MODE_RE = re.compile(r"(?mi)^.*Mode:\s*(light|heavy)\b")
RISK_RE = re.compile(r"(?mi)^.*Risk level:\s*(Low|Medium|High|Critical)\b")
CONFIDENCE_RE = re.compile(r"(?mi)^.*Confidence:\s*(Low|Medium|High)\b")
ADR_RE = re.compile(r"(?mi)\bADR\s*:\s*(Needed|Not needed|Existing)\b")
TASK_RE = re.compile(r"(?mi)^\s*#{3,}\s*Task\s+\d+\s*:")
TASK_BLOCK_RE = re.compile(r"(?ms)^\s*#{3,}\s*Task\s+\d+\s*:.+?(?=^\s*#{3,}\s*Task\s+\d+\s*:|\Z)")
FIELD_RE = re.compile(r"(?ms)^\s*-\s*([^:\n]+?)\s*:\s*(.*?)(?=^\s*-\s*[^:\n]+?\s*:|\Z)")
XL_RE = re.compile(r"(?mi)Estimated scope:\s*XL\b")
CODE_RE = re.compile(r"`([^`]+)`")
VALID_ROLES = {"coding", "devops", "review", "consult", "sa"}
TASK_REQUIRED_FIELDS = (
    "Worker role",
    "Wave",
    "Acceptance criteria",
    "Verification",
    "Dependencies",
    "Files likely touched",
    "Writable scope",
    "Output artifact",
    "Estimated scope",
)
EXEC_REQUIRED_FIELDS = ("Worker role", "Wave", "Verification", "Writable scope", "Output artifact")


def has_heading(text: str, heading: str) -> bool:
    return bool(re.search(rf"(?m)^##\s+{re.escape(heading)}\s*$", text))


def section_text(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def handoff_errors(text: str) -> list[str]:
    errors: list[str] = []
    if not has_heading(text, "Execution Handoff"):
        return ["missing ## Execution Handoff"]
    for label in HANDOFF_LABELS:
        if not re.search(rf"(?mi)^\s*-\s*{re.escape(label)}\s*:", text):
            errors.append(f"handoff missing label: {label}")
    headings = re.findall(r"(?m)^##\s+(.+?)\s*$", text)
    if headings and headings[-1] != "Execution Handoff":
        errors.append("Execution Handoff must be the final heading")
    return errors


def task_errors(text: str) -> list[str]:
    errors: list[str] = []
    task_section = section_text(text, "Task Breakdown")
    if not TASK_RE.search(task_section):
        errors.append("Task Breakdown must include at least one ### Task N:")
    task_blocks = [match.group(0) for match in TASK_BLOCK_RE.finditer(task_section)]
    if TASK_RE.search(task_section) and not task_blocks:
        errors.append("Task Breakdown task blocks could not be parsed")
    for block in task_blocks:
        task_number = re.search(r"(?m)Task\s+(\d+)\s*:", block)
        label = f"Task {task_number.group(1)}" if task_number else "Task"
        fields = _task_fields(block)
        for field in TASK_REQUIRED_FIELDS:
            if field.lower() not in fields:
                errors.append(f"{label} missing task field: {field}")
        for field in EXEC_REQUIRED_FIELDS:
            value = fields.get(field.lower(), "")
            if _empty_or_placeholder(value):
                errors.append(f"{label} has non-executable {field}")
        errors.extend(_output_artifact_errors(fields.get("output artifact", ""), label))
        role = fields.get("worker role", "").strip().lower()
        if role and role not in VALID_ROLES:
            errors.append(f"{label} has unknown Worker role: {role}")
    if XL_RE.search(task_section):
        errors.append("XL tasks are not allowed")
    errors.extend(_wave_overlap_errors(task_blocks))
    return errors

def _task_fields(block: str) -> dict[str, str]:
    return {match.group(1).strip().lower(): match.group(2).strip() for match in FIELD_RE.finditer(block)}

def _empty_or_placeholder(value: str) -> bool:
    stripped = re.sub(r"\s+", " ", value.strip()).strip("` ").lower()
    return not stripped or stripped in {"tbd", "todo", "unknown", "not specified", "n/a", "na"}

def _scope_paths(value: str) -> list[str]:
    paths = [path.strip() for path in CODE_RE.findall(value) if path.strip()]
    if paths:
        return paths
    paths = []
    for line in value.splitlines():
        item = line.strip().lstrip("-").strip()
        if item and not _empty_or_placeholder(item):
            paths.append(item)
    return paths


def _output_artifact_errors(value: str, task_label: str) -> list[str]:
    errors: list[str] = []
    for path_text in _scope_paths(value):
        path = Path(path_text)
        if path_text.endswith("/") or path.name in {"", ".", ".."}:
            errors.append(f"{task_label} has invalid Output artifact path: {path_text}")
            continue
        parent = path.parent
        if str(parent) in {"", "."}:
            errors.append(f"{task_label} Output artifact must include a parent directory: {path_text}")
            continue
        if path.is_absolute():
            continue
        first = path.parts[0] if path.parts else ""
        if first not in {".codex", ".spec2plan"}:
            errors.append(f"{task_label} Output artifact should live under .codex/ or .spec2plan/: {path_text}")
    return errors


def _wave_overlap_errors(task_blocks: list[str]) -> list[str]:
    errors: list[str] = []
    owners: dict[tuple[str, str], str] = {}
    for block in task_blocks:
        task_number = re.search(r"(?m)Task\s+(\d+)\s*:", block)
        task_label = f"Task {task_number.group(1)}" if task_number else "Task"
        fields = _task_fields(block)
        role = fields.get("worker role", "").strip().lower()
        if role in {"review", "consult", "sa"}:
            continue
        wave = fields.get("wave", "").strip()
        for path in _scope_paths(fields.get("writable scope", "")):
            key = (wave, path)
            prior = owners.get(key)
            if prior:
                errors.append(f"same-wave Writable scope overlap: {path} in {prior} and {task_label}")
            owners[key] = task_label
    return errors


def subagent_errors(plan_path: Path) -> list[str]:
    errors: list[str] = []
    subagent_dir = plan_path.parent / "subagents"
    validator = Path(__file__).with_name("validate_subagent_artifact.py")

    for phase in SUBAGENT_PHASES:
        artifact = subagent_dir / f"{phase}.md"
        if not artifact.is_file():
            errors.append(f"missing subagent artifact: {artifact}")
            continue
        result = subprocess.run(
            [sys.executable, str(validator), phase, str(artifact)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            errors.append(f"invalid {phase} artifact: {detail}")
    return errors


def synthesizer_match_errors(plan_path: Path, plan_text: str) -> list[str]:
    artifact = plan_path.parent / "subagents" / "synthesizer.md"
    if not artifact.is_file():
        return []

    try:
        text = artifact.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read synthesizer artifact for comparison: {exc}"]

    stripped = text.strip()
    if not stripped.startswith(ARTIFACT_START) or not stripped.endswith(ARTIFACT_END):
        return []

    body = stripped.removeprefix(ARTIFACT_START).removesuffix(ARTIFACT_END).strip()
    match = re.search(r"(?ms)^artifact:\s*\n(.*)\Z", body)
    if not match:
        return []

    final_artifact = match.group(1).replace("\r\n", "\n").strip()
    final_plan = plan_text.replace("\r\n", "\n").strip()
    if final_plan != final_artifact:
        return ["plan.md must match subagents/synthesizer.md artifact body exactly"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a spec2plan plan contract.")
    parser.add_argument("plan_path", type=Path)
    parser.add_argument("--mode", choices=("light", "heavy"), default="light")
    args = parser.parse_args()

    try:
        text = args.plan_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"INVALID: cannot read plan: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    if not re.search(r"(?m)^#\s+\S+", text):
        errors.append("missing top-level title")

    for heading in REQUIRED_HEADINGS:
        if not has_heading(text, heading):
            errors.append(f"missing ## {heading}")

    for name, regex in (
        ("Mode: light|heavy", MODE_RE),
        ("Risk level: Low|Medium|High|Critical", RISK_RE),
        ("Confidence: Low|Medium|High", CONFIDENCE_RE),
        ("ADR: Needed|Not needed|Existing", ADR_RE),
    ):
        if not regex.search(text):
            errors.append(f"missing {name}")

    errors.extend(task_errors(text))
    errors.extend(handoff_errors(text))

    if args.mode == "heavy":
        errors.extend(subagent_errors(args.plan_path))
        errors.extend(synthesizer_match_errors(args.plan_path, text))

    if errors:
        print("INVALID: " + "; ".join(errors), file=sys.stderr)
        return 1

    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
