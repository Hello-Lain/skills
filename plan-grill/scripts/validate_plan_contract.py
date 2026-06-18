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
    "Domain Language Check",
    "Current Context",
    "Assumptions",
    "User Inputs Needed",
    "Proposed Approach",
    "Scenario Probes",
    "Step-by-Step Plan",
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

RISK_RE = re.compile(r"(?mi)^.*Risk level:\s*(Low|Medium|High|Critical)\b")
CONFIDENCE_RE = re.compile(r"(?mi)^.*Confidence:\s*(Low|Medium|High)\b")
ADR_RE = re.compile(r"(?mi)\bADR\s*:\s*(Needed|Not needed|Existing)\b")
SUBAGENT_PHASES = ("planner", "grill", "synthesizer")
ARTIFACT_START = "PLAN_GRILL_ARTIFACT_V1"
ARTIFACT_END = "PLAN_GRILL_ARTIFACT_END"

def has_heading(text: str, heading: str) -> bool:
    return bool(re.search(rf"(?m)^##\s+{re.escape(heading)}\s*$", text))

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
    parser = argparse.ArgumentParser(description="Validate a plan-grill plan contract.")
    parser.add_argument("plan_path", type=Path)
    parser.add_argument("--allow-missing-handoff", action="store_true", help="Compatibility mode for old plans.")
    parser.add_argument("--allow-missing-subagents", action="store_true", help="Compatibility mode for legacy plans only.")
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

    if not RISK_RE.search(text):
        errors.append("missing Risk level: Low|Medium|High|Critical")
    if not CONFIDENCE_RE.search(text):
        errors.append("missing Confidence: Low|Medium|High")
    if not ADR_RE.search(text):
        errors.append("missing ADR: Needed|Not needed|Existing")

    if not args.allow_missing_handoff:
        errors.extend(handoff_errors(text))
    if not args.allow_missing_subagents:
        errors.extend(subagent_errors(args.plan_path))
        errors.extend(synthesizer_match_errors(args.plan_path, text))

    if errors:
        print("INVALID: " + "; ".join(errors), file=sys.stderr)
        return 1

    print("VALID")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
