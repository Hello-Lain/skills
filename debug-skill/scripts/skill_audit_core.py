#!/usr/bin/env python3
"""Small stdlib helpers for the debug-skill workflow.

Adapted from concepts in NousResearch/hermes-agent-self-evolution (MIT):
- evolution/core/dataset_builder.py: eval examples and dataset splits
- evolution/skills/skill_module.py: skill load/find/reassemble patterns
- evolution/core/constraints.py: constraint result shape and guard checks
- evolution/core/fitness.py: multidimensional score shape
- evolution/core/external_importers.py: secret-like text filtering

This file intentionally does not import Hermes, DSPy, GEPA, OpenAI, or any
third-party package. It provides deterministic primitives for Codex skills.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_SKILLS_ROOT = Path("/data/lcq/.codex/skills")
DEFAULT_MAX_SKILL_CHARS = 15_000
DEFAULT_MAX_BODY_LINES = 500
DEFAULT_MAX_GROWTH = 0.20
TRACE_FIELDS = (
    "Skill(s)",
    "Task",
    "Trigger",
    "Loaded instructions",
    "Decisions",
    "Actions",
    "Failures / friction",
    "Recovery",
    "Validators",
    "Outcome",
    "Optimization hints",
    "Redaction",
    "Human approval required before edits",
)


SECRET_PATTERNS = re.compile(
    r"("
    r"sk-ant-api\S+"
    r"|sk-or-v1-\S+"
    r"|sk-\S{20,}"
    r"|ghp_\S+"
    r"|ghu_\S+"
    r"|xoxb-\S+"
    r"|xapp-\S+"
    r"|ntn_\S+"
    r"|AKIA[0-9A-Z]{16}"
    r"|Bearer\s+\S{20,}"
    r"|-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"
    r"|ANTHROPIC_API_KEY"
    r"|OPENAI_API_KEY"
    r"|OPENROUTER_API_KEY"
    r"|SLACK_BOT_TOKEN"
    r"|GITHUB_TOKEN"
    r"|AWS_SECRET_ACCESS_KEY"
    r"|DATABASE_URL"
    r"|\bpassword\s*[=:]\s*\S+"
    r"|\bsecret\s*[=:]\s*\S+"
    r"|\btoken\s*[=:]\s*\S{10,}"
    r")",
    re.IGNORECASE,
)


@dataclass
class SkillInfo:
    path: str
    raw: str
    frontmatter: str
    body: str
    name: str
    description: str


@dataclass
class SkillAuditExample:
    task_input: str
    expected_behavior: str
    skill_name: str
    trace_ref: str = ""
    outcome: str = ""
    defects: list[str] = field(default_factory=list)
    difficulty: str = "medium"
    source: str = "manual"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SkillAuditExample":
        allowed = cls.__dataclass_fields__.keys()
        values = {key: data[key] for key in allowed if key in data}
        return cls(**values)


@dataclass
class SkillAuditDataset:
    train: list[SkillAuditExample] = field(default_factory=list)
    val: list[SkillAuditExample] = field(default_factory=list)
    holdout: list[SkillAuditExample] = field(default_factory=list)

    @property
    def all_examples(self) -> list[SkillAuditExample]:
        return self.train + self.val + self.holdout

    def save(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        for split_name in ("train", "val", "holdout"):
            with (path / f"{split_name}.jsonl").open("w", encoding="utf-8") as handle:
                for example in getattr(self, split_name):
                    handle.write(json.dumps(example.to_dict(), ensure_ascii=False) + "\n")

    @classmethod
    def load(cls, path: Path) -> "SkillAuditDataset":
        dataset = cls()
        for split_name in ("train", "val", "holdout"):
            split_path = path / f"{split_name}.jsonl"
            if not split_path.exists():
                continue
            examples: list[SkillAuditExample] = []
            with split_path.open(encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        examples.append(SkillAuditExample.from_dict(json.loads(line)))
            setattr(dataset, split_name, examples)
        return dataset


@dataclass
class ConstraintResult:
    passed: bool
    constraint_name: str
    message: str
    severity: str = "error"
    details: str = ""


@dataclass
class FitnessScore:
    quality: float = 0.0
    efficiency: float = 0.0
    evidence: float = 0.0
    context: float = 0.0
    tooling: float = 0.0
    verification: float = 0.0
    user_friction: float = 0.0
    reuse: float = 0.0
    safety: float = 0.0
    feedback: str = ""

    @property
    def composite(self) -> float:
        score = (
            0.25 * self.quality
            + 0.15 * self.efficiency
            + 0.15 * self.evidence
            + 0.10 * self.context
            + 0.10 * self.tooling
            + 0.10 * self.verification
            + 0.05 * self.user_friction
            + 0.05 * self.reuse
            + 0.05 * self.safety
        )
        return round(_clamp(score), 3)


@dataclass
class CandidateScore:
    name: str
    summary: str
    fitness: FitnessScore
    benefit: str = ""
    risk: str = ""
    target_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["composite"] = self.fitness.composite
        return data


def redact_text(text: str) -> str:
    """Replace secret-like fragments with a stable redaction marker."""
    return SECRET_PATTERNS.sub("[REDACTED_SECRET]", text)


def load_skill(skill_path: Path) -> SkillInfo:
    """Load and parse a Codex SKILL.md file."""
    raw = skill_path.read_text(encoding="utf-8")
    frontmatter = ""
    body = raw
    if raw.strip().startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            body = parts[2].strip()

    name = ""
    description = ""
    for line in frontmatter.splitlines():
        stripped = line.strip()
        if stripped.startswith("name:"):
            name = stripped.split(":", 1)[1].strip().strip("'\"")
        elif stripped.startswith("description:"):
            description = stripped.split(":", 1)[1].strip().strip("'\"")

    return SkillInfo(
        path=str(skill_path),
        raw=raw,
        frontmatter=frontmatter,
        body=body,
        name=name,
        description=description,
    )


def find_skill(name_or_path: str, skills_root: Path = DEFAULT_SKILLS_ROOT) -> Path:
    """Find a Codex skill by path, directory name, or frontmatter name.

    Plugin-prefixed names such as "plugin:skill" are matched both as the full
    frontmatter name and by the suffix after ":".
    """
    direct = Path(name_or_path).expanduser()
    if direct.is_file():
        return direct.resolve()
    if direct.is_dir() and (direct / "SKILL.md").is_file():
        return (direct / "SKILL.md").resolve()

    candidates = [name_or_path]
    if ":" in name_or_path:
        candidates.append(name_or_path.split(":", 1)[1])

    for candidate in candidates:
        skill_path = skills_root / candidate / "SKILL.md"
        if skill_path.is_file():
            return skill_path.resolve()

    for skill_path in sorted(skills_root.rglob("SKILL.md")):
        if skill_path.parent.name in candidates:
            return skill_path.resolve()
        try:
            info = load_skill(skill_path)
        except OSError:
            continue
        if info.name in candidates or info.name == name_or_path:
            return skill_path.resolve()

    raise FileNotFoundError(f"Skill not found: {name_or_path} under {skills_root}")


def reassemble_skill(frontmatter: str, body: str) -> str:
    """Reassemble a SKILL.md while preserving frontmatter."""
    return f"---\n{frontmatter.strip()}\n---\n\n{body.strip()}\n"


def validate_skill_text(
    text: str,
    *,
    baseline_text: str | None = None,
    max_chars: int = DEFAULT_MAX_SKILL_CHARS,
    max_body_lines: int = DEFAULT_MAX_BODY_LINES,
    max_growth: float = DEFAULT_MAX_GROWTH,
) -> list[ConstraintResult]:
    """Validate skill text for structure and Codex-specific size guardrails."""
    results: list[ConstraintResult] = []
    stripped = text.strip()
    has_frontmatter = stripped.startswith("---")
    frontmatter = ""
    body = stripped
    if has_frontmatter:
        parts = stripped.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            body = parts[2].strip()

    has_name = bool(re.search(r"(?m)^\s*name\s*:", frontmatter))
    has_description = bool(re.search(r"(?m)^\s*description\s*:", frontmatter))
    results.append(
        ConstraintResult(
            passed=has_frontmatter and has_name and has_description,
            constraint_name="skill_structure",
            message="frontmatter has name and description"
            if has_frontmatter and has_name and has_description
            else "missing YAML frontmatter, name, or description",
        )
    )

    results.append(
        ConstraintResult(
            passed=bool(body.strip()),
            constraint_name="non_empty_body",
            message="body is non-empty" if body.strip() else "body is empty",
        )
    )

    size = len(text)
    results.append(
        ConstraintResult(
            passed=True,
            constraint_name="size_advisory",
            message=f"size {size}/{max_chars} chars",
            severity="warning" if size > max_chars else "info",
        )
    )

    body_lines = len(body.splitlines())
    results.append(
        ConstraintResult(
            passed=True,
            constraint_name="body_line_target",
            message=f"body lines {body_lines}/{max_body_lines}",
            severity="warning" if body_lines > max_body_lines else "info",
        )
    )

    if baseline_text is not None:
        growth = (len(text) - len(baseline_text)) / max(1, len(baseline_text))
        results.append(
            ConstraintResult(
                passed=True,
                constraint_name="growth_limit",
                message=f"growth {growth:+.1%}; max {max_growth:+.1%}",
                severity="warning" if growth > max_growth else "info",
            )
        )

    return results


def score_candidate(
    *,
    name: str,
    summary: str,
    quality: float,
    efficiency: float,
    evidence: float,
    context: float,
    tooling: float,
    verification: float,
    user_friction: float,
    reuse: float,
    safety: float = 0.0,
    benefit: str = "",
    risk: str = "",
    target_files: list[str] | None = None,
) -> CandidateScore:
    """Create a bounded candidate score with quality weighted highest."""
    fitness = FitnessScore(
        quality=_clamp(quality),
        efficiency=_clamp(efficiency),
        evidence=_clamp(evidence),
        context=_clamp(context),
        tooling=_clamp(tooling),
        verification=_clamp(verification),
        user_friction=_clamp(user_friction),
        reuse=_clamp(reuse),
        safety=_clamp(safety),
    )
    return CandidateScore(
        name=name,
        summary=summary,
        fitness=fitness,
        benefit=benefit,
        risk=risk,
        target_files=target_files or [],
    )


def build_report_skeleton(skill_name: str, skills_root: Path = DEFAULT_SKILLS_ROOT) -> str:
    """Build a stable report skeleton for a target skill."""
    skill_ref = skill_name
    missing = ""
    try:
        skill_path = find_skill(skill_name, skills_root)
        info = load_skill(skill_path)
        skill_ref = info.name or skill_path.parent.name
        skill_file = str(skill_path)
    except FileNotFoundError as exc:
        skill_file = "missing"
        missing = f"- {exc}"

    return f"""# Debug Skill Report: {skill_ref}

## Verdict
- Impact: inconclusive
- Confidence: low
- One-line reason: Evidence inventory has not been completed.

## Evidence Used
- Skill files: {skill_file}
- Conversation / trace:
- Artifacts / diffs:
- Commands / validation:
- External reuse sources:
- Missing evidence:
{missing}

## Execution Trace
1. Trigger:
2. Skill instructions loaded:
3. Decisions:
4. Actions:
5. Failures / friction:
6. Recovery:
7. Verification:
8. Result:

## Effectiveness
- Quality:
- Efficiency:
- Evidence use:
- Context handling:
- Tooling:
- Verification:
- User friction:
- Reuse discipline:

## Findings
- No findings recorded yet.

## Reuse Search
- Defect:

| Source project/repo | Source link | Mature signal | Borrowed idea | Reusable component/CLI/schema | Adoption mode | Target skill change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | direct/adapted/pattern-only/rejected | | |

- Search boundary:
- No mature component found:
- Reuse-to-candidate mapping:

## Candidate Improvements
| Candidate | Target surface | Reuse source | Summary | Benefit | Risk / maintenance cost | Fitness / safety |
| --- | --- | --- | --- | --- | --- | --- |
| A | | | | | | |
| B | | | | | | |
| C | | | | | | |

## Promotion Gates
- Evidence sufficient:
- Real user-visible impact:
- Observable behavior improvement:
- Constraints pass:
- Rollback clear:
- Human approval before execution:

## Recommendation
- Recommended action:
- Target files:
- Verification:
- Reuse rationale:
- Execute now: no; requires explicit user approval.
"""


def build_trace_skeleton(skill_name: str) -> str:
    """Build a lightweight in-run trace skeleton."""
    lines = [
        f"# Debug Skill Trace: {skill_name}",
        "",
        "- Mode: trace",
    ]
    for field_name in TRACE_FIELDS:
        default = "yes" if field_name == "Human approval required before edits" else ""
        lines.append(f"- {field_name}: {default}")
    return "\n".join(lines) + "\n"


def _clamp(value: float) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = 0.0
    return min(1.0, max(0.0, numeric))


def _self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        skill_dir = root / "sample-skill"
        skill_dir.mkdir()
        skill_text = """---
name: sample-skill
description: Sample skill for self-test
---

# Sample Skill

Use this for self-tests.
"""
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text(skill_text, encoding="utf-8")

        found = find_skill("sample-skill", root)
        assert found == skill_path

        info = load_skill(found)
        assert info.name == "sample-skill"
        assert "Sample Skill" in info.body
        assert "description:" in reassemble_skill(info.frontmatter, info.body)

        constraints = validate_skill_text(info.raw)
        assert all(result.passed for result in constraints if result.severity == "error")

        bad_constraints = validate_skill_text("# Missing frontmatter\n")
        assert any(not result.passed and result.constraint_name == "skill_structure" for result in bad_constraints)

        redacted = redact_text("token=abcdefghijklmnop and OPENAI_API_KEY")
        assert "[REDACTED_SECRET]" in redacted

        candidate = score_candidate(
            name="A",
            summary="Improve evidence gate",
            quality=0.9,
            efficiency=0.6,
            evidence=0.8,
            context=0.7,
            tooling=0.5,
            verification=0.8,
            user_friction=0.6,
            reuse=0.9,
            safety=0.9,
        )
        assert 0.0 <= candidate.fitness.composite <= 1.0

        skeleton = build_report_skeleton("sample-skill", root)
        assert "# Debug Skill Report: sample-skill" in skeleton

        trace = build_trace_skeleton("sample-skill")
        assert "# Debug Skill Trace: sample-skill" in trace
        assert "- Trigger:" in trace
        assert "- Validators:" in trace
        assert "- Human approval required before edits: yes" in trace


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="debug-skill deterministic helper")
    parser.add_argument("--skills-root", default=str(DEFAULT_SKILLS_ROOT))
    parser.add_argument("--skill", help="Skill name or path to inspect")
    parser.add_argument("--report-skeleton", help="Emit a report skeleton for a skill")
    parser.add_argument("--trace-skeleton", help="Emit a lightweight trace skeleton for a skill or skill chain")
    parser.add_argument("--json", action="store_true", help="Emit JSON for --skill")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-test")
    args = parser.parse_args(argv)

    root = Path(args.skills_root).expanduser()

    if args.self_test:
        _self_test()
        print("SELF_TEST_OK")
        return 0

    if args.report_skeleton:
        print(build_report_skeleton(args.report_skeleton, root))
        return 0

    if args.trace_skeleton:
        print(build_trace_skeleton(args.trace_skeleton))
        return 0

    if args.skill:
        skill_path = find_skill(args.skill, root)
        info = load_skill(skill_path)
        constraints = validate_skill_text(info.raw)
        data = {
            "skill": asdict(info),
            "constraints": [asdict(result) for result in constraints],
        }
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"Skill: {info.name or skill_path.parent.name}")
            print(f"Path: {skill_path}")
            for result in constraints:
                status = "PASS" if result.passed else "FAIL"
                print(f"{status} {result.constraint_name}: {result.message}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
