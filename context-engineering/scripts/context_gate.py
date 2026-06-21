#!/usr/bin/env python3
"""Deterministic advisory gate for context-engineering artifact decisions."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Iterable


ACTIONS = {
    "internal",
    "wave-pack",
    "task-pack",
    "decision-packet",
    "capsule",
    "compact-request",
}

HIGH_RISKS = {"high", "critical"}
HIGH_PRESSURE = {"high", "critical"}
DECISION_CRITICAL = {
    "destructive",
    "security",
    "secret",
    "api",
    "schema",
    "data",
    "migration",
    "dependency",
    "release",
    "production",
    "git-history",
    "config",
    "auth",
}


@dataclass
class GateInput:
    phase: str = "implement"
    plan_tasks: int = 1
    task_risk: str = "low"
    context_pressure: str = "low"
    failures: list[str] = field(default_factory=list)
    decision_critical: list[str] = field(default_factory=list)
    ambiguity: bool = False
    cross_cutting: bool = False
    confidence_loss: bool = False
    phase_boundary: bool = False
    compact_ready: bool = False
    wave_pack_exists: bool = False


@dataclass
class GateResult:
    action: str
    mode: str
    reasons: list[str]
    references: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "action": self.action,
            "mode": self.mode,
            "reasons": self.reasons,
            "references": self.references,
        }


def normalize(values: Iterable[str]) -> list[str]:
    return [value.strip().lower() for value in values if value and value.strip()]


def decide(data: GateInput) -> GateResult:
    reasons: list[str] = []
    references = [
        "context-engineering/SKILL.md",
        "context-engineering/references/artifact-policy.md",
    ]

    critical = sorted(set(normalize(data.decision_critical)) & DECISION_CRITICAL)
    if critical:
        reasons.append("decision-critical: " + ",".join(critical))
        return GateResult("decision-packet", "full", reasons, references + ["context-engineering/references/modes.md"])

    pressure = data.context_pressure.lower()
    if pressure in HIGH_PRESSURE and data.phase_boundary:
        reasons.append(f"context-pressure={pressure}")
        reasons.append("phase-boundary=true")
        action = "compact-request" if data.compact_ready else "capsule"
        if action == "compact-request":
            reasons.append("capsule-or-compact-ready=true")
        return GateResult(action, "full", reasons, references + ["context-engineering/references/modes.md"])

    failures = normalize(data.failures)
    if failures or data.ambiguity or data.cross_cutting or data.confidence_loss or data.task_risk.lower() in HIGH_RISKS:
        if failures:
            reasons.append("failure=" + ",".join(failures))
        if data.ambiguity:
            reasons.append("ambiguity=true")
        if data.cross_cutting:
            reasons.append("cross-cutting=true")
        if data.confidence_loss:
            reasons.append("confidence-loss=true")
        if data.task_risk.lower() in HIGH_RISKS:
            reasons.append(f"task-risk={data.task_risk.lower()}")
        return GateResult("task-pack", "escalate", reasons, references + ["context-engineering/references/modes.md"])

    if pressure in HIGH_PRESSURE:
        reasons.append(f"context-pressure={pressure}")
        return GateResult("capsule", "full", reasons, references + ["context-engineering/references/modes.md"])

    if data.plan_tasks > 1 and not data.wave_pack_exists:
        reasons.append(f"plan-tasks={data.plan_tasks}")
        reasons.append("wave-pack-exists=false")
        return GateResult("wave-pack", "lite", reasons, references)

    reasons.append("routine-focused-context")
    return GateResult("internal", "lite", reasons, references)


def apply_scenario(args: argparse.Namespace) -> None:
    if args.scenario == "routine":
        args.phase = args.phase or "implement"
        args.task_risk = args.task_risk or "low"
    elif args.scenario == "plan":
        args.phase = args.phase or "implement"
        args.plan_tasks = max(args.plan_tasks or 0, 5)
    elif args.scenario == "failure":
        args.failure = args.failure or ["command"]
    elif args.scenario == "decision":
        args.decision_critical = args.decision_critical or ["security"]
    elif args.scenario == "pressure":
        args.context_pressure = args.context_pressure or "high"
        args.phase_boundary = True


def build_input(args: argparse.Namespace) -> GateInput:
    return GateInput(
        phase=args.phase or "implement",
        plan_tasks=args.plan_tasks,
        task_risk=args.task_risk,
        context_pressure=args.context_pressure,
        failures=args.failure or [],
        decision_critical=args.decision_critical or [],
        ambiguity=args.ambiguity,
        cross_cutting=args.cross_cutting,
        confidence_loss=args.confidence_loss,
        phase_boundary=args.phase_boundary,
        compact_ready=args.compact_ready,
        wave_pack_exists=args.wave_pack_exists,
    )


def format_text(result: GateResult) -> str:
    lines = [
        f"action: {result.action}",
        f"mode: {result.mode}",
        "reasons:",
    ]
    lines.extend(f"- {reason}" for reason in result.reasons)
    lines.append("references:")
    lines.extend(f"- {ref}" for ref in result.references)
    return "\n".join(lines)


def run_self_test() -> None:
    cases = [
        (
            "routine reversible task",
            GateInput(phase="implement", task_risk="low"),
            {"internal"},
        ),
        (
            "normal multi-task plan execution",
            GateInput(phase="implement", plan_tasks=5),
            {"wave-pack"},
        ),
        (
            "failed command",
            GateInput(phase="verify", failures=["command"]),
            {"task-pack"},
        ),
        (
            "patch miss",
            GateInput(phase="implement", failures=["patch"]),
            {"task-pack"},
        ),
        (
            "security decision",
            GateInput(decision_critical=["security"]),
            {"decision-packet"},
        ),
        (
            "api decision",
            GateInput(decision_critical=["api"]),
            {"decision-packet"},
        ),
        (
            "schema decision",
            GateInput(decision_critical=["schema"]),
            {"decision-packet"},
        ),
        (
            "pressure boundary before capsule",
            GateInput(context_pressure="high", phase_boundary=True),
            {"capsule"},
        ),
        (
            "pressure boundary after capsule",
            GateInput(context_pressure="high", phase_boundary=True, compact_ready=True),
            {"compact-request"},
        ),
        (
            "replay plan-contract-fail-fast default",
            GateInput(phase="implement", plan_tasks=5),
            {"wave-pack"},
        ),
        (
            "replay task-level escalation",
            GateInput(phase="implement", plan_tasks=5, failures=["test"]),
            {"task-pack"},
        ),
    ]

    failures: list[str] = []
    for name, data, expected in cases:
        result = decide(data)
        if result.action not in ACTIONS:
            failures.append(f"{name}: invalid action {result.action}")
        if result.action not in expected:
            failures.append(f"{name}: got {result.action}, expected one of {sorted(expected)}")

    if failures:
        print("SELF-TEST FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        raise SystemExit(1)
    print("SELF-TEST PASS")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Choose context governance action.")
    p.add_argument("--self-test", action="store_true", help="run built-in regression checks")
    p.add_argument("--json", action="store_true", help="emit JSON")
    p.add_argument("--scenario", choices=["routine", "plan", "failure", "decision", "pressure"])
    p.add_argument("--phase", choices=["explore", "design", "implement", "verify", "review", "handoff"])
    p.add_argument("--plan-tasks", type=int, default=1)
    p.add_argument("--task-risk", choices=["low", "medium", "high", "critical"], default="low")
    p.add_argument("--context-pressure", choices=["low", "medium", "high", "critical"], default="low")
    p.add_argument("--failure", action="append", choices=["command", "patch", "test", "tool", "scope", "context"])
    p.add_argument("--decision-critical", action="append", choices=sorted(DECISION_CRITICAL))
    p.add_argument("--ambiguity", action="store_true")
    p.add_argument("--cross-cutting", action="store_true")
    p.add_argument("--confidence-loss", action="store_true")
    p.add_argument("--phase-boundary", action="store_true")
    p.add_argument("--compact-ready", action="store_true", help="a capsule exists and compact request is now safe")
    p.add_argument("--wave-pack-exists", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.self_test:
        run_self_test()
        return 0
    apply_scenario(args)
    result = decide(build_input(args))
    if args.json:
        print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
