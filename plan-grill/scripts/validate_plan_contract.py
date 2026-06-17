#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = (
    "Goal",
    "Non-Goals",
    "Evidence Inspected",
    "Current Context",
    "Assumptions",
    "User Inputs Needed",
    "Proposed Approach",
    "Step-by-Step Plan",
    "Files / Components Likely Affected",
    "Owners / Responsibilities",
    "Validation Plan",
    "Rollout Plan",
    "Monitoring / Observability",
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

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a plan-grill plan contract.")
    parser.add_argument("plan_path", type=Path)
    parser.add_argument("--allow-missing-handoff", action="store_true", help="Compatibility mode for old plans.")
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

    if not args.allow_missing_handoff:
        errors.extend(handoff_errors(text))

    if errors:
        print("INVALID: " + "; ".join(errors), file=sys.stderr)
        return 1

    print("VALID")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
