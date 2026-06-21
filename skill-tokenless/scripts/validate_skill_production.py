#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

REQUIRED_SECTIONS = (
    "## Behavior Lock",
    "## Token Budget",
    "## Deterministic Validators",
    "## Scenario Gate",
    "## Reviewer Gate",
    "## Reuse Attribution",
    "## Changed Files",
    "## Residual Risks",
)
CHANGE_TYPES = {"new-skill", "material-update", "validator-script", "metadata-update", "minor-update"}
VERDICTS = {"PASS", "BLOCK"}
FINAL_REVIEWER_VERDICTS = {"PASS", "REVISE", "BLOCK"}
DRAFT_REVIEWER_VERDICTS = FINAL_REVIEWER_VERDICTS | {"PENDING"}
CLEANUP_VALUES = ("archive", "kill", "not launched", "unavailable")
VALIDATOR_OUTCOMES = {"PASS", "BLOCK", "SKIPPED"}


def _field(text: str, name: str) -> str | None:
    match = re.search(rf"^\s*[-*]\s*{re.escape(name)}\s*:\s*(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _norm(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().strip("`").upper() or None


def _section(text: str, heading: str) -> str:
    marker = re.escape(heading)
    match = re.search(rf"^{marker}\s*$([\s\S]*?)(?=^##\s+|\Z)", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def _has_table_row(section: str) -> bool:
    rows = [line for line in section.splitlines() if line.strip().startswith("|")]
    data_rows = [line for line in rows if "---" not in line and "Source" not in line]
    return bool(data_rows)


def _validator_outcomes(section: str) -> list[str]:
    outcomes: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "|")) or ":" not in stripped:
            continue
        tail = stripped.rsplit(":", 1)[1].strip()
        match = re.match(r"^(PASS|BLOCK|SKIPPED)\b", tail)
        if match and match.group(1) in VALIDATOR_OUTCOMES:
            outcomes.append(match.group(1))
    return outcomes


def _validate_paths(section: str, root: Path) -> list[str]:
    errors: list[str] = []
    for line in section.splitlines():
        lowered = line.lower()
        allow_missing = any(marker in lowered for marker in ("unavailable", "not available"))
        raws = re.findall(r"`([^`]+)`", line)
        if not raws:
            stripped = line.strip()
            if stripped and not stripped.startswith("|"):
                raw = stripped.lstrip("-*").strip()
                raw = re.sub(r"\b(?:unavailable|not available)\b.*$", "", raw, flags=re.IGNORECASE).strip()
                if raw:
                    raws = [raw]
        for raw in raws:
            if raw.startswith(("http://", "https://")):
                continue
            if raw.startswith("<") or " " in raw:
                continue
            path = Path(raw)
            if not path.is_absolute():
                path = root / path
            if not path.exists() and not allow_missing:
                errors.append(f"changed file path does not exist: {raw}")
    return errors


def validate_report(path: Path, *, root: Path | None = None, stage: str = "final") -> list[str]:
    root = (root or Path.cwd()).resolve()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]

    errors: list[str] = []
    if stage not in {"draft", "final"}:
        errors.append(f"invalid stage: {stage!r}")
    if not re.search(r"^# Skill Production Report\s*$", text, re.MULTILINE):
        errors.append("missing title: # Skill Production Report")

    skill = _field(text, "Skill")
    change_type = _field(text, "Change Type")
    verdict = _norm(_field(text, "Verdict"))
    if not skill:
        errors.append("missing header field: Skill")
    if change_type not in CHANGE_TYPES:
        errors.append(f"invalid Change Type: {change_type!r}")
    if verdict not in VERDICTS:
        errors.append(f"invalid Verdict: {verdict!r}")

    for heading in REQUIRED_SECTIONS:
        body = _section(text, heading)
        if not body:
            errors.append(f"missing or empty section: {heading}")

    validators = _section(text, "## Deterministic Validators")
    validator_outcomes = _validator_outcomes(validators)
    if validators and not validator_outcomes:
        errors.append("Deterministic Validators must include PASS, BLOCK, or SKIPPED outcomes")

    reviewer = _section(text, "## Reviewer Gate")
    reviewer_verdict: str | None = None
    if reviewer:
        reviewer_verdict = _norm(_field(reviewer, "Verdict"))
        cleanup = (_field(reviewer, "Cleanup") or "").lower()
        cleanup_known = any(value in cleanup for value in CLEANUP_VALUES)
        if stage == "final":
            if reviewer_verdict not in FINAL_REVIEWER_VERDICTS:
                errors.append(f"Reviewer Gate has invalid final Verdict: {reviewer_verdict!r}")
        elif reviewer_verdict is not None and reviewer_verdict not in DRAFT_REVIEWER_VERDICTS:
            errors.append(f"Reviewer Gate has invalid draft Verdict: {reviewer_verdict!r}")
        if stage == "draft" and reviewer_verdict is None and "not launched" not in cleanup and "unavailable" not in cleanup:
            errors.append("draft Reviewer Gate may omit Verdict only when Cleanup records not launched or unavailable")
        if not cleanup_known:
            errors.append("Reviewer Gate Cleanup must record archive, kill, not launched, or unavailable")

    reuse = _section(text, "## Reuse Attribution")
    if reuse and not _has_table_row(reuse):
        errors.append("Reuse Attribution must include at least one data row")

    changed = _section(text, "## Changed Files")
    if changed:
        errors.extend(_validate_paths(changed, root))

    if verdict == "PASS" and "BLOCK" in validator_outcomes:
        errors.append("PASS production report cannot include BLOCK validator outcomes")
    if stage == "final" and verdict == "PASS":
        if reviewer_verdict in {"BLOCK", "REVISE"}:
            errors.append(f"PASS production report cannot include reviewer {reviewer_verdict}")
        if reviewer_verdict in {None, "PENDING"}:
            errors.append("PASS final production report requires reviewer PASS")

    return errors


def _valid_report(existing: Path, *, reviewer_verdict: str | None = "PASS") -> str:
    reviewer_line = "" if reviewer_verdict is None else f"- Verdict: {reviewer_verdict}\n"
    return f"""# Skill Production Report

- Skill: skill-tokenless
- Change Type: material-update
- Verdict: PASS

## Behavior Lock
- Preserved: trigger, workflow, validators.
- Changed intentionally: added production gate.
- Fallbacks: block on missing evidence.

## Token Budget
- Before: 10 lines.
- After: 12 lines.
- Moved to references: gate schema.

## Deterministic Validators
- `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`: PASS

## Scenario Gate
- Scenario: material skill update.
- RED/control: no gate.
- GREEN/retest: gate validator passes.
- Cleanup: not launched.

## Reviewer Gate
- Mode: lite
- Route: inline
{reviewer_line}- Report: not saved
- Cleanup: not launched

## Reuse Attribution
| Source | URL | Borrowed idea | Component | Adoption | Target change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- |
| Superpowers | https://github.com/obra/superpowers | review gate | none | adapted | skill gate | runtime differs |

## Changed Files
- `{existing}`

## Residual Risks
- None known.
"""


def run_self_test() -> list[str]:
    errors: list[str] = []
    root = Path.cwd().resolve()
    existing = Path(__file__).resolve()
    with tempfile.TemporaryDirectory(prefix="skill-production-report-") as tmp:
        tmp_path = Path(tmp)
        valid = tmp_path / "valid.md"
        valid.write_text(_valid_report(existing), encoding="utf-8")
        draft = tmp_path / "draft.md"
        draft.write_text(_valid_report(existing, reviewer_verdict="PENDING"), encoding="utf-8")
        draft_omitted = tmp_path / "draft-omitted.md"
        draft_omitted.write_text(_valid_report(existing, reviewer_verdict=None), encoding="utf-8")
        cases = [
            ("valid final", valid.read_text(encoding="utf-8"), "final", True),
            ("valid draft pending", draft.read_text(encoding="utf-8"), "draft", True),
            ("valid draft omitted", draft_omitted.read_text(encoding="utf-8"), "draft", True),
            ("final pending", draft.read_text(encoding="utf-8"), "final", False),
            ("missing title", valid.read_text(encoding="utf-8").replace("# Skill Production Report\n", ""), "final", False),
            ("bad change type", valid.read_text(encoding="utf-8").replace("material-update", "large"), "final", False),
            ("missing reviewer cleanup", valid.read_text(encoding="utf-8").replace("- Cleanup: not launched", "- Cleanup: "), "final", False),
            ("missing reuse row", re.sub(r"\| Superpowers .+\n", "", valid.read_text(encoding="utf-8")), "final", False),
            ("valid unbackticked path", valid.read_text(encoding="utf-8").replace(f"`{existing}`", str(existing)), "final", True),
            ("missing changed path", valid.read_text(encoding="utf-8").replace(str(existing), "/definitely/missing/skill.md"), "final", False),
            ("missing unbackticked changed path", valid.read_text(encoding="utf-8").replace(f"`{existing}`", "/definitely/missing/skill.md"), "final", False),
            ("unavailable changed path", valid.read_text(encoding="utf-8").replace(f"`{existing}`", "`/definitely/missing/skill.md` unavailable"), "final", True),
            ("pass with revise", valid.read_text(encoding="utf-8").replace("- Verdict: PASS\n- Report", "- Verdict: REVISE\n- Report"), "final", False),
            (
                "validator command contains block token",
                valid.read_text(encoding="utf-8").replace(
                    "`python3 skill-tokenless/scripts/validate_skill_production.py --self-test`: PASS",
                    "`rg -n \"PASS|REVISE|BLOCK\" .codex/work/report.md`: PASS",
                ),
                "final",
                True,
            ),
            (
                "pass with explicit block validator outcome",
                valid.read_text(encoding="utf-8").replace(
                    "`python3 skill-tokenless/scripts/validate_skill_production.py --self-test`: PASS",
                    "`python3 skill-tokenless/scripts/validate_skill_production.py --self-test`: BLOCK",
                ),
                "final",
                False,
            ),
        ]
        for index, (name, text, stage, should_pass) in enumerate(cases, 1):
            report = tmp_path / f"case-{index}.md"
            report.write_text(text, encoding="utf-8")
            case_errors = validate_report(report, root=root, stage=stage)
            passed = not case_errors
            if passed != should_pass:
                detail = "; ".join(case_errors) if case_errors else "unexpected pass"
                errors.append(f"{name}: expected pass={should_pass}, got pass={passed}: {detail}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Skill Production Gate report.")
    parser.add_argument("report", nargs="?", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--stage", choices=("draft", "final"), default="final")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        errors = run_self_test()
    elif args.report:
        errors = validate_report(args.report, root=args.root, stage=args.stage)
    else:
        parser.error("provide a report path or --self-test")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
