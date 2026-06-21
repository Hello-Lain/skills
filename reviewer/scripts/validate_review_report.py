#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

VERDICTS = {"PASS", "REVISE", "BLOCK"}
MODES = {"lite", "heavy", "blocked"}
ROUTES = {"inline", "subagent", "multi-subagent", "blocked"}
SEVERITIES = {"critical", "major", "minor", "nit"}
CONFIDENCE = {"Low", "Medium", "High"}
LOCAL_PATH_RE = re.compile(r"`([^`]+)`|(?<![\w:/.-])((?:\.{1,2}/|/)[^\s,;)\]]+|[A-Za-z0-9_.-]+/[^\s,;)\]]+)")
REQUIRED_SECTIONS = (
    "## Review Basis",
    "## Rubric",
    "## Mode Decision",
    "## Alignment Result",
    "## Quality Result",
    "## Findings",
    "## Recheck Plan",
    "## Residual Risks",
)
BLOCK_END_RE = re.compile(
    r"^\s*(?:[-*]\s*)?"
    r"(?:Goal|Artifact|Sources|Constraints|Validators|Cleanup|Route|Reason|Packet|"
    r"Raw transcript handling|Result|Evidence|Criterion|Impact|Fix Type|Revision)\s*:",
    re.IGNORECASE,
)


def _clean_path(raw: str) -> str:
    path = raw.strip().strip("`'\"")
    path = re.sub(r"(?::\d+(?::\d+)?)$", "", path)
    return path.rstrip(".,;:")


def _is_url(value: str) -> bool:
    return value.startswith(("http://", "https://"))


def _path_exists(raw: str, root: Path) -> bool:
    path = Path(_clean_path(raw))
    if _is_url(str(path)):
        return True
    if path.is_absolute():
        return path.exists()
    return (root / path).exists()


def _extract_local_paths(line: str) -> list[str]:
    paths: list[str] = []
    for match in LOCAL_PATH_RE.finditer(line):
        raw = match.group(1) or match.group(2)
        if not raw:
            continue
        values = raw.split() if match.group(1) and re.search(r"\s", raw) else [raw]
        for item in values:
            value = _clean_path(item)
            if _is_url(value) or value.startswith("<"):
                continue
            # Skip command names, flags, and words that are not path-like.
            if "/" not in value and not value.startswith("."):
                continue
            paths.append(value)
    return paths


def _section_lines(lines: list[str], heading: str) -> list[str]:
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return []
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return lines[start + 1:end]


def _source_or_evidence_blocks(lines: list[str]) -> list[tuple[int, list[str]]]:
    blocks: list[tuple[int, list[str]]] = []
    for index, line in enumerate(lines):
        if not re.match(r"^\s*[-*]?\s*(Sources|Evidence)\s*:", line):
            continue
        block = [line]
        cursor = index + 1
        while cursor < len(lines):
            next_line = lines[cursor]
            if not next_line.strip() or next_line.startswith("## "):
                break
            if re.match(r"^\s*[-*]\s*\[[A-Za-z]+\]\s+.+", next_line):
                break
            if BLOCK_END_RE.match(next_line):
                break
            block.append(next_line)
            cursor += 1
        blocks.append((index + 1, block))
    return blocks


def validate_report(path: Path, *, root: Path | None = None) -> list[str]:
    root = (root or Path.cwd()).resolve()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]

    errors: list[str] = []
    lines = text.splitlines()

    top_verdicts = []
    for lineno, line in enumerate(lines, 1):
        match = re.match(r"^\s*[-*]\s*Verdict\s*:\s*`?(PASS|REVISE|BLOCK)`?\s*$", line)
        if match:
            top_verdicts.append((lineno, match.group(1).upper()))
    if len(top_verdicts) != 1:
        errors.append(f"expected exactly one top-level '- Verdict: PASS|REVISE|BLOCK' line, found {len(top_verdicts)}")
        verdict = None
    else:
        verdict = top_verdicts[0][1]

    mode = None
    route = None
    for line in lines:
        mode_match = re.match(r"^\s*[-*]\s*Review Mode\s*:\s*`?([A-Za-z-]+)`?\s*$", line)
        if mode_match:
            mode = mode_match.group(1).lower()
        route_match = re.match(r"^\s*[-*]\s*Review Route\s*:\s*`?([A-Za-z-]+)`?\s*$", line)
        if route_match:
            route = route_match.group(1).lower()

    if mode not in MODES:
        errors.append(f"missing or invalid Review Mode: expected one of {sorted(MODES)}")
    if route not in ROUTES:
        errors.append(f"missing or invalid Review Route: expected one of {sorted(ROUTES)}")

    for required in ("Artifact Type", "Confidence"):
        if not any(re.match(rf"^\s*[-*]\s*{re.escape(required)}\s*:", line) for line in lines):
            errors.append(f"missing required header field: {required}")

    confidence_values = [
        match.group(1)
        for line in lines
        for match in [re.match(r"^\s*[-*]\s*Confidence\s*:\s*`?([A-Za-z]+)`?\s*$", line)]
        if match
    ]
    if confidence_values and confidence_values[-1] not in CONFIDENCE:
        errors.append(f"invalid Confidence: expected one of {sorted(CONFIDENCE)}")

    headings = {line.strip() for line in lines if line.startswith("## ")}
    for section in REQUIRED_SECTIONS:
        if section not in headings:
            errors.append(f"missing section: {section}")

    for section in ("## Alignment Result", "## Quality Result"):
        section_block = _section_lines(lines, section)
        if section_block and not any(
            re.match(r"^\s*[-*]\s*Result\s*:\s*`?(PASS|REVISE|BLOCK)`?\s*$", line)
            for line in section_block
        ):
            errors.append(f"{section} lacks Result: PASS|REVISE|BLOCK")

    finding_indices: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^\s*[-*]\s*\[([A-Za-z]+)\]\s+.+", line)
        if not match:
            continue
        severity = match.group(1).lower()
        if severity not in SEVERITIES:
            errors.append(f"line {index + 1}: invalid severity {severity!r}")
        finding_indices.append((index, severity))

    if verdict == "PASS":
        blocking = [severity for _, severity in finding_indices if severity in {"critical", "major"}]
        if blocking:
            errors.append("PASS report cannot contain critical or major findings")

    for pos, (index, severity) in enumerate(finding_indices):
        next_index = finding_indices[pos + 1][0] if pos + 1 < len(finding_indices) else len(lines)
        block = lines[index + 1:next_index]
        if severity in {"critical", "major"}:
            evidence_lines = [line for line in block if re.match(r"^\s*Evidence\s*:\s*\S+", line)]
            if not evidence_lines:
                errors.append(f"line {index + 1}: {severity} finding lacks non-empty Evidence line")

    for lineno, block in _source_or_evidence_blocks(lines):
        for offset, line in enumerate(block):
            lowered = line.lower()
            allow_missing = any(marker in lowered for marker in ("missing", "unavailable", "not available", "not inspected"))
            if allow_missing:
                continue
            for raw in _extract_local_paths(line):
                if not _path_exists(raw, root):
                    errors.append(f"line {lineno + offset}: cited local path does not exist or is not marked missing: {raw}")

    return errors


def _valid_report(mode: str, route: str, verdict: str, evidence_path: Path) -> str:
    return f"""# Review: self-test {mode}

- Artifact Type: self-test
- Confidence: High
- Review Mode: {mode}
- Review Route: {route}
- Verdict: {verdict}

## Review Basis
- Goal: validate the report parser.
- Artifact: `{evidence_path}`
- Sources: `{evidence_path}`
- Constraints: read-only.
- Validators: `python3 reviewer/scripts/validate_review_report.py --self-test`

## Rubric
- Schema: required headers and sections are present.

## Mode Decision
- Route: {route}
- Reason: self-test.

## Alignment Result
- Result: {verdict}
- Reason: self-test alignment.

## Quality Result
- Result: {verdict}
- Reason: self-test quality.

## Findings
Findings: None

## Recheck Plan
- Run self-test.

## Residual Risks
- None known.
"""


def run_self_test() -> list[str]:
    errors: list[str] = []
    root = Path.cwd().resolve()
    evidence = Path(__file__).resolve()
    with tempfile.TemporaryDirectory(prefix="reviewer-report-test-") as tmp:
        tmp_path = Path(tmp)
        valid_lite = tmp_path / "valid-lite.md"
        valid_lite.write_text(_valid_report("lite", "inline", "PASS", evidence), encoding="utf-8")
        valid_heavy = tmp_path / "valid-heavy.md"
        valid_heavy.write_text(_valid_report("heavy", "subagent", "PASS", evidence), encoding="utf-8")

        cases: list[tuple[str, str, bool]] = [
            ("valid lite", valid_lite.read_text(encoding="utf-8"), True),
            ("valid heavy", valid_heavy.read_text(encoding="utf-8"), True),
            ("missing verdict", valid_lite.read_text(encoding="utf-8").replace("- Verdict: PASS\n", ""), False),
            ("duplicate verdict", valid_lite.read_text(encoding="utf-8") + "\n- Verdict: PASS\n", False),
            ("lowercase verdict", valid_lite.read_text(encoding="utf-8").replace("- Verdict: PASS", "- Verdict: pass"), False),
            ("invalid confidence", valid_lite.read_text(encoding="utf-8").replace("- Confidence: High", "- Confidence: Certain"), False),
            ("invalid route", valid_lite.read_text(encoding="utf-8").replace("- Review Route: inline", "- Review Route: remote"), False),
            ("missing mode decision", valid_lite.read_text(encoding="utf-8").replace("## Mode Decision\n", ""), False),
            ("mode decision prose only", valid_lite.read_text(encoding="utf-8").replace("## Mode Decision\n", "This prose mentions ## Mode Decision but is not a heading.\n"), False),
            ("missing alignment result", valid_lite.read_text(encoding="utf-8").replace("## Alignment Result\n", ""), False),
            ("command evidence path", valid_lite.read_text(encoding="utf-8").replace("Findings: None", "- [minor] command evidence\n  Evidence: `python3 reviewer/scripts/validate_review_report.py --self-test`\n  Criterion: schema.\n  Impact: none.\n  Fix Type: patch current artifact\n  Revision: none."), True),
            ("invalid severity", valid_lite.read_text(encoding="utf-8").replace("Findings: None", "- [bad] malformed\n  Evidence: `reviewer/SKILL.md`"), False),
            ("missing major evidence", valid_lite.read_text(encoding="utf-8").replace("Findings: None", "- [major] no evidence"), False),
            ("pass with major", valid_lite.read_text(encoding="utf-8").replace("Findings: None", "- [major] blocked\n  Evidence: `reviewer/SKILL.md`"), False),
            ("missing source", valid_lite.read_text(encoding="utf-8").replace(f"`{evidence}`", "`/definitely/absent/reviewer-source.md`"), False),
            ("missing source continuation", valid_lite.read_text(encoding="utf-8").replace(f"- Sources: `{evidence}`", "- Sources:\n  - `/definitely/absent/reviewer-source.md`"), False),
            ("missing marker scoped", valid_lite.read_text(encoding="utf-8").replace(f"- Sources: `{evidence}`", "- Sources: missing `/definitely/absent/allowed.md`\n  - `/definitely/absent/not-allowed.md`"), False),
        ]

        for index, (name, text, should_pass) in enumerate(cases, 1):
            report_path = tmp_path / f"case-{index}.md"
            report_path.write_text(text, encoding="utf-8")
            case_errors = validate_report(report_path, root=root)
            passed = not case_errors
            if passed != should_pass:
                detail = "; ".join(case_errors) if case_errors else "unexpected pass"
                errors.append(f"{name}: expected pass={should_pass}, got pass={passed}: {detail}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate reviewer v2 review report structure.")
    parser.add_argument("report", nargs="?", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Root for relative local source paths.")
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
