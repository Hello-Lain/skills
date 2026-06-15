#!/usr/bin/env python3
"""Deep audit for final literature-rag Markdown + structured paper audit JSON."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from manage_outputs import load_manifest

BAD_TEXT_RE = re.compile(
    r"generic|not verifiable|needs_agent|待核验|无法核验|todo|tbd|unknown|待确认",
    re.IGNORECASE,
)
LOCATOR_RE = re.compile(
    r"\b(eq\.?|equation|algorithm|alg\.?|section|sec\.?|page|p\.|appendix|figure|fig\.?|table)\b|第\s*\d+\s*(节|页|式|公式|算法|图|表)",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://\S+")
PAPER_RE = re.compile(r"(?m)^\s*(\d+)\.\s+\*\*(?:\[([^\]]+)\]\(([^)]+)\)|([^*]+))\*\*")
NO_MATCH_RE = re.compile(r"no valid|no matching|未找到|无匹配|没有符合", re.IGNORECASE)

REQUIRED_BOOL_TRUE = [
    "title_match",
    "venue_verified",
    "constraint_match",
    "mechanism_verified",
    "contribution_verified",
]

def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)

def manifest_pair(workdir: str) -> tuple[Path | None, Path | None, list[str], list[Path]]:
    files = load_manifest(workdir)
    md_files = [path for path in files if path.suffix.lower() == ".md"]
    audit_files = [path for path in files if path.name.endswith(".audit.json")]
    errors: list[str] = []
    if len(md_files) != 1:
        errors.append(f"manifest must register exactly one Markdown file, found {len(md_files)}")
    if len(audit_files) != 1:
        errors.append(f"manifest must register exactly one audit JSON file, found {len(audit_files)}")
    return (md_files[0] if len(md_files) == 1 else None, audit_files[0] if len(audit_files) == 1 else None, errors, files)

def parse_markdown_papers(text: str) -> list[dict[str, Any]]:
    papers: list[dict[str, Any]] = []
    for match in PAPER_RE.finditer(text):
        title = (match.group(2) or match.group(4) or "").strip()
        url = (match.group(3) or "").strip()
        papers.append({"index": int(match.group(1)), "title": title, "url": url})
    return papers

def short_quote_ok(value: str) -> bool:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]*", value)
    cjk = re.findall(r"[\u4e00-\u9fff]", value)
    return len(words) <= 25 and len(cjk) <= 60

def substantive(value: Any, minimum: int = 30) -> bool:
    return isinstance(value, str) and len(value.strip()) >= minimum and not BAD_TEXT_RE.search(value)

def validate_paper(item: dict[str, Any], md_by_index: dict[int, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    index = item.get("index")
    prefix = f"paper {index}"
    if not isinstance(index, int):
        return ["paper entry missing integer index"]

    keep = item.get("keep")
    if keep is not True:
        if index in md_by_index:
            errors.append(f"{prefix}: keep=false paper appears in final Markdown")
        if not substantive(item.get("drop_reason"), 8):
            errors.append(f"{prefix}: dropped paper missing drop_reason")
        return errors

    md_item = md_by_index.get(index)
    if not md_item:
        errors.append(f"{prefix}: kept paper missing from Markdown")
    else:
        if str(item.get("title", "")).strip() != md_item["title"]:
            errors.append(f"{prefix}: audit title does not match Markdown title")
        if str(item.get("url", "")).strip() and md_item["url"] and str(item.get("url", "")).strip() != md_item["url"]:
            errors.append(f"{prefix}: audit URL does not match Markdown URL")

    for field in ["title", "url", "venue", "year"]:
        if not str(item.get(field, "")).strip():
            errors.append(f"{prefix}: missing {field}")
    if not URL_RE.search(str(item.get("url", ""))):
        errors.append(f"{prefix}: url must be http(s)")
    for field in REQUIRED_BOOL_TRUE:
        if item.get(field) is not True:
            errors.append(f"{prefix}: {field} must be true")
    if item.get("pseudocode_quality") != "method_specific":
        errors.append(f"{prefix}: pseudocode_quality must be method_specific")
    if not substantive(item.get("method_relevance"), 30):
        errors.append(f"{prefix}: method_relevance too short or placeholder")
    if not substantive(item.get("why_useful"), 30):
        errors.append(f"{prefix}: why_useful too short or placeholder")

    source_type = str(item.get("formula_source_type", "")).strip().lower()
    if source_type not in {"paper formula", "derived formula"}:
        errors.append(f"{prefix}: formula_source_type must be paper formula or derived formula")
    evidence_url = str(item.get("formula_evidence_url", "")).strip()
    locator = str(item.get("formula_evidence_locator", "")).strip()
    quote = str(item.get("formula_evidence_quote", "")).strip()
    if not URL_RE.search(evidence_url):
        errors.append(f"{prefix}: formula_evidence_url must be http(s)")
    if not quote:
        errors.append(f"{prefix}: formula_evidence_quote missing")
    elif not short_quote_ok(quote):
        errors.append(f"{prefix}: formula_evidence_quote too long")
    if source_type == "paper formula":
        if not LOCATOR_RE.search(locator):
            errors.append(f"{prefix}: paper formula locator must cite Eq/Algorithm/Section/Page/etc.")
    elif source_type == "derived formula":
        if not substantive(item.get("derived_from"), 20):
            errors.append(f"{prefix}: derived formula missing derived_from")
    return errors

def validate(markdown_path: Path, audit_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    if not markdown_path.exists():
        errors.append(f"Markdown missing: {markdown_path}")
        text = ""
    else:
        text = markdown_path.read_text(encoding="utf-8", errors="replace")
    try:
        audit = load_json(audit_path)
    except (OSError, json.JSONDecodeError) as exc:
        audit = {}
        errors.append(f"Audit JSON unreadable: {exc}")

    if not isinstance(audit, dict):
        audit = {}
        errors.append("Audit JSON must be an object")

    papers = audit.get("papers")
    excluded = audit.get("excluded_candidates")
    if not isinstance(papers, list):
        papers = []
        errors.append("audit.papers must be a list")
    if not isinstance(excluded, list):
        excluded = []
        errors.append("audit.excluded_candidates must be a list")

    if str(audit.get("query", "")).strip() and str(audit.get("query", "")).strip() not in text:
        errors.append("audit.query is not present in Markdown")
    final_markdown = str(audit.get("final_markdown", "")).strip()
    if final_markdown and Path(final_markdown).resolve() != markdown_path.resolve():
        errors.append("audit.final_markdown does not match Markdown path")

    md_papers = parse_markdown_papers(text)
    md_by_index = {item["index"]: item for item in md_papers}
    kept = [item for item in papers if isinstance(item, dict) and item.get("keep") is True]
    if len(kept) != len(md_papers):
        errors.append(f"kept audit papers ({len(kept)}) must equal Markdown papers ({len(md_papers)})")
    if not kept:
        if not NO_MATCH_RE.search(text):
            errors.append("no kept papers requires explicit no-match explanation in Markdown")
        if not excluded:
            errors.append("no kept papers requires non-empty excluded_candidates")

    for item in papers:
        if not isinstance(item, dict):
            errors.append("audit.papers entries must be objects")
            continue
        errors.extend(validate_paper(item, md_by_index))

    if excluded and "Excluded candidates" not in text:
        errors.append("Markdown must include an Excluded candidates summary when audit has exclusions")
    for idx, item in enumerate(excluded, 1):
        if not isinstance(item, dict):
            errors.append(f"excluded candidate {idx}: must be object")
            continue
        if not str(item.get("title", "")).strip():
            errors.append(f"excluded candidate {idx}: missing title")
        if not substantive(item.get("reason"), 8):
            errors.append(f"excluded candidate {idx}: missing reason")

    return {
        "passed": not errors,
        "markdown": str(markdown_path),
        "audit": str(audit_path),
        "paper_count": len(md_papers),
        "kept_audit_count": len(kept),
        "excluded_count": len(excluded),
        "errors": errors,
    }

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit final literature-rag Markdown against structured paper audit JSON.")
    parser.add_argument("--workdir", default=os.getcwd())
    parser.add_argument("--markdown")
    parser.add_argument("--audit")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    manifest_files: list[Path] = []
    manifest_errors: list[str] = []
    if args.markdown or args.audit:
        markdown = Path(args.markdown).resolve() if args.markdown else None
        audit = Path(args.audit).resolve() if args.audit else None
        if markdown is None:
            manifest_errors.append("--markdown is required when --audit is supplied")
        if audit is None:
            manifest_errors.append("--audit is required when --markdown is supplied")
    else:
        markdown, audit, manifest_errors, manifest_files = manifest_pair(args.workdir)

    if markdown and audit:
        report = validate(markdown, audit)
        report["manifest_files"] = [str(path) for path in manifest_files]
        report["errors"] = manifest_errors + report["errors"]
        report["passed"] = not report["errors"]
    else:
        report = {
            "passed": False,
            "markdown": str(markdown) if markdown else "",
            "audit": str(audit) if audit else "",
            "manifest_files": [str(path) for path in manifest_files],
            "paper_count": 0,
            "kept_audit_count": 0,
            "excluded_count": 0,
            "errors": manifest_errors,
        }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 4

if __name__ == "__main__":
    raise SystemExit(main())
