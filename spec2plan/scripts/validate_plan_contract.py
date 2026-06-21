#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
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
    "Implementation Map",
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
    "Plan Self-Review",
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
PATHISH_RE = re.compile(r"(?:^|[\s`])(?:\.?/?[\w.-]+/[\w./*{}-]+|[\w.-]+\.(?:py|ts|tsx|js|jsx|rs|go|java|md|yaml|yml|json|toml|sql|sh|txt))(?:[\s`]|$)")
COMMANDISH_RE = re.compile(r"(?i)\b(?:python|pytest|npm|pnpm|yarn|uv|cargo|go test|make|just|ruff|mypy|tsc|eslint|docker|kubectl|terraform|git|bash|sh)\b")
PLACEHOLDER_RE = re.compile(
    r"(?i)\b(?:tbd|todo|later|as needed|relevant files?|appropriate tests?|etc\.?)\b|相关|必要时|适当"
)
VALID_ROLES = {"coding", "devops", "review", "consult", "sa"}
TASK_REQUIRED_FIELDS = (
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
)
EXEC_REQUIRED_FIELDS = ("Worker role", "Wave", "Verification", "Writable scope", "Output artifact")
COMMAND_FIELDS = ("verification", "pre-check commands", "post-check commands")
IMPLEMENTATION_MAP_LABELS = ("Files", "Symbols / APIs", "Tests", "Commands", "Data / migration impact")
SELF_REVIEW_PHRASES = ("writable scope", "coverage", "unknown", "rollback", "Task 1")


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
        for field in COMMAND_FIELDS:
            value = fields.get(field, "")
            if value and not _has_command_or_exception(value):
                errors.append(f"{label} {field} must include an exact command or a concrete not-runnable/manual-check reason")
        for field_name, value in fields.items():
            if _has_placeholder(value):
                errors.append(f"{label} has placeholder language in {field_name}: {_first_placeholder(value)}")
        errors.extend(_output_artifact_errors(fields.get("output artifact", ""), label))
        role = fields.get("worker role", "").strip().lower()
        if role and role not in VALID_ROLES:
            errors.append(f"{label} has unknown Worker role: {role}")
        errors.extend(_review_output_artifact_errors(fields, label))
    if XL_RE.search(task_section):
        errors.append("XL tasks are not allowed")
    errors.extend(_wave_overlap_errors(task_blocks))
    return errors

def _task_fields(block: str) -> dict[str, str]:
    return {match.group(1).strip().lower(): match.group(2).strip() for match in FIELD_RE.finditer(block)}

def _empty_or_placeholder(value: str) -> bool:
    stripped = re.sub(r"\s+", " ", value.strip()).strip("` ").lower()
    return not stripped or stripped in {"tbd", "todo", "unknown", "not specified", "n/a", "na"}

def _has_placeholder(value: str) -> bool:
    return bool(PLACEHOLDER_RE.search(value))

def _first_placeholder(value: str) -> str:
    match = PLACEHOLDER_RE.search(value)
    return match.group(0) if match else ""

def _has_command_or_exception(value: str) -> bool:
    lower = value.lower()
    if any(phrase in lower for phrase in ("not runnable", "not applicable", "manual check", "manual verification", "no command")):
        return True
    return bool(CODE_RE.search(value) or COMMANDISH_RE.search(value))

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
            errors.append(f"{task_label} Output artifact must be repo-relative under .codex/work/: {path_text}")
            continue
        first = path.parts[0] if path.parts else ""
        second = path.parts[1] if len(path.parts) > 1 else ""
        if (first, second) != (".codex", "work"):
            errors.append(f"{task_label} Output artifact should live under .codex/work/: {path_text}")
    return errors

def _review_output_artifact_errors(fields: dict[str, str], task_label: str) -> list[str]:
    role = fields.get("worker role", "").strip().lower()
    if role != "review":
        return []

    errors: list[str] = []
    task_text = "\n".join(fields.values())
    for path_text in _scope_paths(fields.get("output artifact", "")):
        if _is_review_artifact_path(path_text) or _requires_standalone_verdict(task_text):
            continue
        errors.append(
            f"{task_label} review Output artifact must be .codex/work/<topic>/review*.md "
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

def implementation_map_errors(text: str) -> list[str]:
    errors: list[str] = []
    body = section_text(text, "Implementation Map")
    for label in IMPLEMENTATION_MAP_LABELS:
        if not re.search(rf"(?mi)^\s*-\s*{re.escape(label)}\s*:", body):
            errors.append(f"Implementation Map missing label: {label}")
    if _has_placeholder(body):
        errors.append(f"Implementation Map has placeholder language: {_first_placeholder(body)}")
    return errors

def micro_step_errors(text: str) -> list[str]:
    errors: list[str] = []
    body = section_text(text, "Step-by-Step Plan")
    step_lines = [
        line.strip()
        for line in body.splitlines()
        if re.match(r"^\s*(?:[-*]|\d+[.)])\s+\S+", line)
    ]
    if not step_lines:
        return ["Step-by-Step Plan must include bullet or numbered micro-steps"]
    for index, line in enumerate(step_lines, 1):
        if _has_placeholder(line):
            errors.append(f"Step {index} has placeholder language: {_first_placeholder(line)}")
        if not (CODE_RE.search(line) or PATHISH_RE.search(line) or COMMANDISH_RE.search(line)):
            errors.append(f"Step {index} lacks exact path, symbol/API, command, or artifact anchor")
    return errors

def self_review_errors(text: str) -> list[str]:
    errors: list[str] = []
    body = section_text(text, "Plan Self-Review")
    for phrase in SELF_REVIEW_PHRASES:
        if phrase.lower() not in body.lower():
            errors.append(f"Plan Self-Review missing check topic: {phrase}")
    if _has_placeholder(body):
        errors.append(f"Plan Self-Review has placeholder language: {_first_placeholder(body)}")
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

def execution_compile_errors(plan_path: Path) -> list[str]:
    compiler = Path(__file__).resolve().parents[2] / "plan2do" / "scripts" / "compile_execution.py"
    if not compiler.is_file():
        return [f"missing plan2do compiler for execution compatibility check: {compiler}"]

    try:
        spec = importlib.util.spec_from_file_location("_plan2do_compile_execution", compiler)
        if spec is None or spec.loader is None:
            return [f"cannot load plan2do compiler: {compiler}"]
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.compile_plan(plan_path)
    except Exception as exc:
        return [f"plan2do compile compatibility failed: {exc}"]
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
    errors.extend(implementation_map_errors(text))
    errors.extend(micro_step_errors(text))
    errors.extend(self_review_errors(text))
    errors.extend(handoff_errors(text))
    errors.extend(execution_compile_errors(args.plan_path))

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
