#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

START = "PLAN_GRILL_ARTIFACT_V1"
END = "PLAN_GRILL_ARTIFACT_END"
PHASES = {"planner", "grill", "synthesizer"}
STATUSES = {"complete", "needs_revision", "unsafe"}
PROGRESS_ONLY = (
    "i will",
    "i'll",
    "working on",
    "still investigating",
    "need to inspect",
    "let me",
    "starting",
)


def invalid(msg: str) -> int:
    print(f"INVALID: {msg}", file=sys.stderr)
    return 1


def parse(text: str) -> tuple[str, str, str] | str:
    stripped = text.strip()
    if not stripped.startswith(START):
        return "missing start marker"
    if not stripped.endswith(END):
        return "missing final end marker or trailing text after marker"

    body = stripped.removeprefix(START).removesuffix(END).strip()
    phase_match = re.search(r"(?mi)^phase:\s*(\w+)\s*$", body)
    status_match = re.search(r"(?mi)^status:\s*(\w+)\s*$", body)
    artifact_match = re.search(r"(?ms)^artifact:\s*\n(.*)\Z", body)

    if not phase_match:
        return "missing phase"
    if not status_match:
        return "missing status"
    if not artifact_match:
        return "missing artifact block"

    phase = phase_match.group(1).lower()
    status = status_match.group(1).lower()
    artifact = artifact_match.group(1).strip()
    return phase, status, artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a plan-grill subagent artifact envelope.")
    parser.add_argument("phase", choices=sorted(PHASES))
    parser.add_argument("artifact_path", type=Path)
    args = parser.parse_args()

    try:
        text = args.artifact_path.read_text(encoding="utf-8")
    except OSError as exc:
        return invalid(f"cannot read artifact: {exc}")

    parsed = parse(text)
    if isinstance(parsed, str):
        return invalid(parsed)

    phase, status, artifact = parsed
    if phase not in PHASES:
        return invalid(f"unknown phase: {phase}")
    if phase != args.phase:
        return invalid(f"phase mismatch: expected {args.phase}, got {phase}")
    if status not in STATUSES:
        return invalid(f"unknown status: {status}")
    if status != "complete":
        return invalid(f"status is not complete: {status}")

    words = re.findall(r"\w+", artifact)
    if len(words) < 40:
        return invalid("artifact too short")

    lowered = artifact.lower()
    if any(marker in lowered for marker in PROGRESS_ONLY) and len(words) < 120:
        return invalid("artifact looks like progress-only output")

    if phase in {"planner", "synthesizer"}:
        if not re.search(r"(?m)^#\s+\S+", artifact):
            return invalid("plan artifact missing top-level title")
        if not re.search(r"(?m)^##\s+Goal\s*$", artifact):
            return invalid("plan artifact missing ## Goal")

    if phase == "grill":
        bullet_count = len(re.findall(r"(?m)^\s*[-*]\s+\S+", artifact))
        if bullet_count < 3:
            return invalid("grill artifact needs at least three findings or explicit checks")
        for label in (
            "Scenario Probes",
            "Code/doc contradictions",
            "Repo-unanswerable user questions",
        ):
            if not re.search(rf"(?mi)^\s*#+\s*{re.escape(label)}\s*$|^\s*[-*]\s*{re.escape(label)}\s*:", artifact):
                return invalid(f"grill artifact missing {label}")

    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
