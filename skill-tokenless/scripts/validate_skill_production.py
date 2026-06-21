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
REVIEWER_VERDICTS = {"PASS", "REVISE", "BLOCK"}
CLEANUP_VALUES = ("archive", "kill", "not launched", "unavailable")


def _field(text: str, name: str) -> str | None:
    match = re.search(rf"^\s*[-*]\s*{re.escape(name)}\s*:\s*(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _section(text: str, heading: str) -> str:
    marker = re.escape(heading)
    match = re.search(rf"^{marker}\s*$([\s\S]*?)(?=^##\s+|\Z)", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def _has_table_row(section: str) -> bool:
    rows = [line for line in section.splitlines() if line.strip().startswith("|")]
    data_rows = [line for line in rows if "---" not in line and "Source" not in line]
    return bool(data_rows)


def _validate_paths(section: str, root: Path) -> list[str]:
    errors: list[str] = []
    for raw in re.findall(r"`([^`]+)`", section):
        if raw.startswith(("http://", "https://")):
            continue
        if raw.startswith("<") or " " in raw:
            continue
        path = Path(raw)
        if not path.is_absolute():
            path = root / path
        if not path.exists():
            errors.append(f"changed file path does not exist: {raw}")
    return errors


def validate_report(path: Path, *, root: Path | None = None) -> list[str]:
    root = (root or Path.cwd()).resolve()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]

    errors: list[str] = []
    if not re.search(r"^# Skill Production Report\s*$", text, re.MULTILINE):
        errors.append("missing title: # Skill Production Report")

    skill = _field(text, "Skill")
    change_type = _field(text, "Change Type")
    verdict = _field(text, "Verdict")
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
    if validators and not re.search(r"\b(PASS|BLOCK|SKIPPED)\b", validators):
        errors.append("Deterministic Validators must include PASS, BLOCK, or SKIPPED outcomes")

    reviewer = _section(text, "## Reviewer Gate")
    if reviewer:
        reviewer_verdict = _field(reviewer, "Verdict")
        cleanup = (_field(reviewer, "Cleanup") or "").lower()
        if reviewer_verdict not in REVIEWER_VERDICTS:
            errors.append(f"Reviewer Gate has invalid Verdict: {reviewer_verdict!r}")
        if not any(value in cleanup for value in CLEANUP_VALUES):
            errors.append("Reviewer Gate Cleanup must record archive, kill, not launched, or unavailable")

    reuse = _section(text, "## Reuse Attribution")
    if reuse and not _has_table_row(reuse):
        errors.append("Reuse Attribution must include at least one data row")

    changed = _section(text, "## Changed Files")
    if changed:
        errors.extend(_validate_paths(changed, root))

    if verdict == "PASS" and re.search(r"\bBLOCK\b", validators):
        errors.append("PASS production report cannot include BLOCK validator outcomes")
    if verdict == "PASS" and "Verdict: BLOCK" in reviewer:
        errors.append("PASS production report cannot include reviewer BLOCK")
    if verdict == "PASS" and "Verdict: REVISE" in reviewer:
        errors.append("PASS production report cannot include reviewer REVISE")

    return errors


def _valid_report(existing: Path) -> str:
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
- Verdict: PASS
- Report: not saved
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
        cases = [
            ("valid", valid.read_text(encoding="utf-8"), True),
            ("missing title", valid.read_text(encoding="utf-8").replace("# Skill Production Report\n", ""), False),
            ("bad change type", valid.read_text(encoding="utf-8").replace("material-update", "large"), False),
            ("missing reviewer cleanup", valid.read_text(encoding="utf-8").replace("- Cleanup: not launched", "- Cleanup: "), False),
            ("missing reuse row", re.sub(r"\| Superpowers .+\n", "", valid.read_text(encoding="utf-8")), False),
            ("missing changed path", valid.read_text(encoding="utf-8").replace(str(existing), "/definitely/missing/skill.md"), False),
            ("pass with revise", valid.read_text(encoding="utf-8").replace("- Verdict: PASS\n- Report", "- Verdict: REVISE\n- Report"), False),
        ]
        for index, (name, text, should_pass) in enumerate(cases, 1):
            report = tmp_path / f"case-{index}.md"
            report.write_text(text, encoding="utf-8")
            case_errors = validate_report(report, root=root)
            passed = not case_errors
            if passed != should_pass:
                detail = "; ".join(case_errors) if case_errors else "unexpected pass"
                errors.append(f"{name}: expected pass={should_pass}, got pass={passed}: {detail}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Skill Production Gate report.")
    parser.add_argument("report", nargs="?", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        errors = run_self_test()
    elif args.report:
        errors = validate_report(args.report, root=args.root)
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
