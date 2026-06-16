#!/usr/bin/env python3
"""Validate the final literature-rag Markdown artifact for main-agent acceptance."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from manage_outputs import load_manifest, owned_markdown_files

REQUIRED_SECTIONS = [
    "Core mechanism:",
    "Core contribution:",
    "Pseudocode and formula design:",
    "Formula source:",
    "Formula evidence:",
    "Why useful / transferable insight:",
    "Verification source:",
]

QUALITY_RE = re.compile(r"quality[- ]?gate|retry|重试|质量门|质量检查", re.IGNORECASE)
PAPER_RE = re.compile(r"^[ \t]*\d+\.\s+\*\*", re.MULTILINE)
PAPER_HEADING_RE = re.compile(r"(?m)^[ \t]*(\d+)\.\s+\*\*")
PAPER_LINK_RE = re.compile(r"^[ \t]*\d+\.\s+\*\*\[[^\]]+\]\(https?://[^)\s]+\)\*\*", re.MULTILINE)
CODE_FENCE_RE = re.compile(r"```(?:text|python|pseudo|pseudocode)?\n(.*?)```", re.DOTALL | re.IGNORECASE)
DISPLAY_FORMULA_RE = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)
FORMULA_SOURCE_RE = re.compile(r"Formula source:\s*(.+)", re.IGNORECASE)
FORMULA_EVIDENCE_RE = re.compile(r"Formula evidence:\s*(.+)", re.IGNORECASE)
USEFUL_RE = re.compile(r"Why useful / transferable insight:\s*(.+)", re.IGNORECASE)
EVIDENCE_ANCHOR_RE = re.compile(
    r"\b(eq\.?|equation|formula|algorithm|alg\.?|section|sec\.?|appendix|page|p\.|figure|fig\.?|table)\b|第\s*\d+\s*(节|页|式|公式|算法)",
    re.IGNORECASE,
)
BAD_PLACEHOLDER_RE = re.compile(
    r"not verifiable|needs_agent|待核验|无法核验|generic|method\s*\(\)|todo",
    re.IGNORECASE,
)
GENERIC_FORMULA_RE = re.compile(
    r"^\s*[A-Za-z_][\w{}\\]*\s*=\s*[A-Za-z_]\w*\s*\([^)]*\)\s*$"
    r"|^\s*(?:score|loss|objective|signal)\s*=\s*[A-Za-z_]\w*\s*\([^)]*\)\s*$",
    re.IGNORECASE,
)

def paper_blocks(text: str) -> list[tuple[int, str]]:
    matches = list(PAPER_HEADING_RE.finditer(text))
    blocks: list[tuple[int, str]] = []
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        blocks.append((int(match.group(1)), text[match.start():end]))
    return blocks

def validate_paper_block(index: int, block: str) -> list[str]:
    errors: list[str] = []
    heading = next((line for line in block.splitlines() if line.strip()), "")
    if not PAPER_LINK_RE.match(heading):
        errors.append(f"paper {index}: heading must use **[title](https://...)** link format")

    if BAD_PLACEHOLDER_RE.search(block):
        errors.append(f"paper {index}: contains unverifiable/generic placeholder")

    code_match = CODE_FENCE_RE.search(block)
    if not code_match:
        errors.append(f"paper {index}: missing fenced pseudocode")
    else:
        lines = [line for line in code_match.group(1).splitlines() if line.strip() and not line.strip().startswith("#")]
        if len(lines) < 6:
            errors.append(f"paper {index}: pseudocode has fewer than 6 substantive lines")
        if len(lines) > 15:
            errors.append(f"paper {index}: pseudocode has more than 15 substantive lines")

    if block.count("$$") % 2:
        errors.append(f"paper {index}: unbalanced display formula delimiters")
    formulas = [formula.strip() for formula in DISPLAY_FORMULA_RE.findall(block)]
    if not formulas:
        errors.append(f"paper {index}: missing display formula")
    if len(formulas) > 3:
        errors.append(f"paper {index}: more than 3 display formula blocks")
    for formula in formulas:
        normalized_formula = re.sub(r"\s+", " ", formula).strip()
        if GENERIC_FORMULA_RE.search(normalized_formula):
            errors.append(f"paper {index}: formula is too generic or placeholder-like")
            break

    source_match = FORMULA_SOURCE_RE.search(block)
    evidence_match = FORMULA_EVIDENCE_RE.search(block)
    useful_match = USEFUL_RE.search(block)
    source = source_match.group(1).strip().lower() if source_match else ""
    evidence = evidence_match.group(1).strip() if evidence_match else ""
    useful = useful_match.group(1).strip() if useful_match else ""

    if not source_match:
        errors.append(f"paper {index}: missing Formula source")
    elif "paper formula" not in source and "derived formula" not in source:
        errors.append(f"paper {index}: Formula source must be paper formula or derived formula")
    if not evidence_match or len(evidence) < 20:
        errors.append(f"paper {index}: missing substantive Formula evidence")
    elif "paper formula" in source and not EVIDENCE_ANCHOR_RE.search(evidence):
        errors.append(f"paper {index}: paper formula lacks equation/algorithm/section/page evidence anchor")
    if not useful_match or len(useful) < 30:
        errors.append(f"paper {index}: missing substantive user-useful transferable insight")

    if "Verification source:" not in block or not re.search(r"Verification source:.*https?://", block, re.IGNORECASE | re.DOTALL):
        errors.append(f"paper {index}: missing URL in Verification source")
    return errors

def visible_owned_markdown(workdir: str) -> list[Path]:
    return [path for path in owned_markdown_files(workdir) if path.name != "SKILL.md"]

def validate_markdown(path: Path) -> tuple[list[str], dict[str, int | bool | str]]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    paper_count = len(PAPER_RE.findall(text))
    linked_paper_count = len(PAPER_LINK_RE.findall(text))
    blocks = paper_blocks(text)
    counts = {section: text.count(section) for section in REQUIRED_SECTIONS}

    if "**Query:**" not in text:
        errors.append("missing **Query:** marker")
    if not QUALITY_RE.search(text):
        errors.append("missing quality-gate/retry note")
    if paper_count > 5:
        errors.append("more than 5 numbered paper entries")
    if linked_paper_count < paper_count:
        errors.append("every numbered paper entry must use **[title](https://...)** link format")
    if "Excluded candidates" not in text:
        errors.append("missing Excluded candidates summary")
    for section, count in counts.items():
        if paper_count and count < paper_count:
            errors.append(f"section count too low: {section} ({count} < {paper_count})")
    if not paper_count and not re.search(r"no valid|no matching|未找到|无匹配|没有符合", text, re.IGNORECASE):
        errors.append("no numbered papers and no explicit no-match explanation")
    for index, block in blocks:
        errors.extend(validate_paper_block(index, block))

    details: dict[str, int | bool | str] = {
        "paper_count": paper_count,
        "linked_paper_count": linked_paper_count,
        "paper_blocks": len(blocks),
        "has_query": "**Query:**" in text,
        "has_quality_note": bool(QUALITY_RE.search(text)),
    }
    details.update({section: count for section, count in counts.items()})
    return errors, details

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate literature-rag final Markdown output.")
    parser.add_argument("--workdir", default=os.getcwd())
    parser.add_argument("--file", help="Specific final Markdown path. Defaults to registered manifest file.")
    parser.add_argument("--strict-owned-md", action="store_true", default=True)
    parser.add_argument("--no-strict-owned-md", action="store_false", dest="strict_owned_md")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    root = Path(args.workdir).resolve()
    manifest_files = load_manifest(str(root))
    md_files = [path for path in manifest_files if path.suffix.lower() == ".md"]
    audit_files = [path for path in manifest_files if path.name.endswith(".audit.json")]
    selected = Path(args.file).resolve() if args.file else (md_files[0] if len(md_files) == 1 else None)
    errors: list[str] = []

    if len(md_files) != 1:
        errors.append(f"manifest must register exactly one Markdown file, found {len(md_files)}")
    if len(audit_files) != 1:
        errors.append(f"manifest must register exactly one audit JSON file, found {len(audit_files)}")
    elif not audit_files[0].exists():
        errors.append(f"audit JSON missing: {audit_files[0]}")
    if len(md_files) == 1 and len(audit_files) == 1 and audit_files[0] != md_files[0].with_suffix(".audit.json"):
        errors.append("audit JSON must be the same-prefix .audit.json for the final Markdown")
    if not selected:
        errors.append("no final Markdown file selected")
    elif root not in selected.parents and root != selected:
        errors.append("selected file is outside workdir")
    elif not selected.exists():
        errors.append(f"selected file missing: {selected}")
    elif selected.suffix.lower() != ".md":
        errors.append("selected file is not Markdown")

    owned = visible_owned_markdown(str(root))
    if args.strict_owned_md and selected:
        extras = [path for path in owned if path.resolve() != selected]
        if extras:
            errors.append("extra literature-rag Markdown files in workdir: " + ", ".join(str(path) for path in extras))

    details: dict[str, int | bool | str] = {}
    if selected and selected.exists() and selected.suffix.lower() == ".md":
        md_errors, details = validate_markdown(selected)
        errors.extend(md_errors)

    report = {
        "passed": not errors,
        "workdir": str(root),
        "registered_files": [str(path) for path in manifest_files],
        "selected_file": str(selected) if selected else "",
        "audit_file": str(audit_files[0]) if len(audit_files) == 1 else "",
        "owned_markdown_files": [str(path) for path in owned],
        "details": details,
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 4

if __name__ == "__main__":
    raise SystemExit(main())
