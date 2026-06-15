#!/usr/bin/env python3
"""Extract query-constrained candidate papers from demo chat output."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import Any

TOP_VENUE_RE = re.compile(
    r"(?<![A-Za-z])(CVPR|ICCV|ECCV|NeurIPS|NIPS|ICLR|ICML|AAAI|IJCAI|ACL|EMNLP|NAACL|COLING|KDD|SIGIR|WWW|TheWebConf|TPAMI|IJCV|JMLR|TMLR)(?![A-Za-z])",
    re.IGNORECASE,
)
YEAR_RE = re.compile(r"\b(20[0-9]{2})\b")
TITLE_RE = re.compile(r'\*\*(?:"([^"]+)"|([^*]+))\*\*')
ARXIV_RE = re.compile(
    r"(?:arXiv:\s*|arxiv_id['\"]?:\s*['\"]?|arxiv\.org/abs/|\[)(\d{4}\.\d{4,5})",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://[^\s)\]]+")
YEAR_RANGE_RE = re.compile(
    r"(?<!\d)(20)?([0-9]{2})\s*(?:-|~|–|—|到|至|年到|年至)\s*(20)?([0-9]{2})(?:\s*年)?"
)

VENUE_CANONICAL = {
    "CVPR": "CVPR",
    "ICCV": "ICCV",
    "ECCV": "ECCV",
    "NEURIPS": "NeurIPS",
    "NIPS": "NeurIPS",
    "ICLR": "ICLR",
    "ICML": "ICML",
    "AAAI": "AAAI",
    "IJCAI": "IJCAI",
    "ACL": "ACL",
    "EMNLP": "EMNLP",
    "NAACL": "NAACL",
    "COLING": "COLING",
    "KDD": "KDD",
    "SIGIR": "SIGIR",
    "WWW": "WWW",
    "THEWEBCONF": "TheWebConf",
    "TPAMI": "TPAMI",
    "IJCV": "IJCV",
    "JMLR": "JMLR",
    "TMLR": "TMLR",
}
DEFAULT_YEARS = {"2024", "2025", "2026"}
DEFAULT_VENUES = set(VENUE_CANONICAL.values())

NON_PAPER_TITLES = {
    "计算资源开销大",
    "推理延迟增加",
    "双模型加载",
    "内存占用翻倍",
    "需要同家族模型",
    "小模型不可用",
    "规模差异敏感",
    "线性外推局限性",
    "简单问题失败",
    "事实性降级",
    "Logits平坦化",
    "信息量不足",
    "小模型不稳定",
    "过早退出",
    "温度T任务依赖",
    "层次选择困难",
    "α掩码参数",
    "推理速度下降",
    "FLOPs增加",
    "多样性-事实性冲突",
    "粗粒度对比",
    "潜在错误传播",
    "分布偏移",
}


@dataclass
class Paper:
    title: str
    venue: str = ""
    year: str = ""
    arxiv_id: str = ""
    authors: str = ""
    citation: str = ""
    mechanism: str = ""
    contribution: str = ""
    url: str = ""


@dataclass(frozen=True)
class Constraints:
    years: set[str]
    venues: set[str]
    inferred_years: bool = False
    inferred_venues: bool = False


def constraints_to_dict(constraints: Constraints) -> dict[str, Any]:
    return {
        "years": sorted(constraints.years),
        "venues": sorted(constraints.venues),
        "inferred_years": constraints.inferred_years,
        "inferred_venues": constraints.inferred_venues,
    }


def paper_to_dict(paper: Paper) -> dict[str, str]:
    return {
        "title": paper.title,
        "venue": paper.venue,
        "year": paper.year,
        "arxiv_id": paper.arxiv_id,
        "authors": paper.authors,
        "citation": paper.citation,
        "url": paper.url,
        "raw_mechanism_clue": paper.mechanism,
        "raw_contribution_clue": paper.contribution,
        "verification_status": "needs_agent_paper_source_verification",
    }


def canonical_venue(value: str) -> str:
    return VENUE_CANONICAL.get(re.sub(r"[^A-Za-z]", "", value).upper(), value)


def normalize_year(value: str, prefix: str | None = None) -> str:
    if len(value) == 4:
        return value
    if prefix:
        return f"{prefix}{value}"
    return f"20{value}"


def infer_years(query: str) -> tuple[set[str], bool]:
    years: set[str] = set()
    for match in YEAR_RANGE_RE.finditer(query):
        start = int(normalize_year(match.group(2), match.group(1)))
        end = int(normalize_year(match.group(4), match.group(3) or match.group(1)))
        if start > end:
            start, end = end, start
        if end - start <= 20:
            years.update(str(year) for year in range(start, end + 1))
    years.update(YEAR_RE.findall(query))
    if years:
        return years, False
    return set(DEFAULT_YEARS), True


def infer_venues(query: str) -> tuple[set[str], bool]:
    venues = {canonical_venue(match.group(1)) for match in TOP_VENUE_RE.finditer(query)}
    if venues:
        return venues, False
    return set(DEFAULT_VENUES), True


def infer_constraints(query: str) -> Constraints:
    years, inferred_years = infer_years(query)
    venues, inferred_venues = infer_venues(query)
    return Constraints(years=years, venues=venues, inferred_years=inferred_years, inferred_venues=inferred_venues)


def load_transcript(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_events(path: str | None) -> list[dict[str, Any]]:
    if not path or not os.path.exists(path):
        return []
    events = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                events.append(json.loads(line))
    return events


def strip_think(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)


def strip_inline_markup(value: str) -> str:
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\[\[([^\]]+)\]\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[\[([^\]]+)\]\]", r"\1", value)
    value = re.sub(r"[*_`]+", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" -|")

def clean_title(value: str) -> str:
    candidates: list[str] = []
    normalized = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    for part in normalized.splitlines():
        text = strip_inline_markup(part)
        if text:
            candidates.append(text)
    full = strip_inline_markup(value)
    if full:
        candidates.append(full)
    for candidate in reversed(candidates):
        candidate = re.sub(
            r"^\s*(?:[A-Z][A-Z0-9-]{1,12})\s+(?:CVPR|ICCV|ECCV|NeurIPS|NIPS|ICLR|ICML|AAAI|IJCAI)\s+20\d{2}\s*",
            "",
            candidate,
            flags=re.I,
        )
        candidate = re.sub(
            r"\b(?:CVPR|ICCV|ECCV|NeurIPS|NIPS|ICLR|ICML|AAAI|IJCAI)\s+20\d{2}\b",
            "",
            candidate,
            flags=re.I,
        ).strip(" -|")
        if is_probable_paper_title(candidate):
            return candidate
    return full.strip(" -|")

def cell_text(cells: list[str], indexes: list[int]) -> str:
    values = []
    for index in indexes:
        if 0 <= index < len(cells):
            values.append(strip_inline_markup(cells[index]))
    return " ".join(value for value in values if value).strip()


def extract_line_value(block: str, label: str) -> str:
    pattern = re.compile(rf"^\s*-\s*{re.escape(label)}:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(block)
    return match.group(1).strip() if match else ""


def infer_mechanism(title: str, text: str) -> str:
    lower = f"{title} {text}".lower()
    if "dpo" in lower or "preference optimization" in lower:
        return "Vision-guided preference optimization/alignment."
    if "editing" in lower or "projectaway" in lower or "representation" in lower:
        return "Interpret and edit internal vision-language representations."
    if "bottom-up" in lower or "holistic reasoning" in lower:
        return "Bottom-up holistic visual reasoning before answer generation."
    if "magnifying" in lower or "perception magnification" in lower:
        return "Adaptive perception magnification during decoding."
    if "attention" in lower or "defocus" in lower:
        return "Use visual attention defocus to reveal and rectify hallucinations."
    if "multi-object" in lower or "rope" in lower:
        return "Evaluate/mitigate multi-object hallucination under object-level settings."
    if "negative queries" in lower or "finer" in lower:
        return "Expose fine-grained negative-query hallucination cases."
    if "early" in lower or "layer" in lower or "exit" in lower:
        return "Uses internal-layer or early-exit contrastive signal."
    if "distillation" in lower or "distill" in lower:
        return "Distills contrastive signal to avoid dual-model inference."
    return "needs_agent_paper_source_verification"


def infer_contribution(title: str, text: str) -> str:
    lower = f"{title} {text}".lower()
    if "survey" in lower:
        return "Survey/systematization of causes, evaluation, and mitigation."
    if "detect" in lower or "reveals" in lower:
        return "Detection or diagnosis signal for model hallucination/factuality."
    if "mitigat" in lower or "rectif" in lower or "hallucination-free" in lower:
        return "Mitigation method for reducing hallucinations or factual errors."
    if "multi-object" in lower:
        return "Benchmark/analysis for multi-object hallucination."
    return "needs_agent_paper_source_verification"


def build_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""


def extract_url(text: str, arxiv_id: str) -> str:
    match = URL_RE.search(text)
    if match:
        return match.group(0)
    return build_url(arxiv_id)


def venue_and_year(text: str, constraints: Constraints) -> tuple[str, str]:
    venues = [canonical_venue(match.group(1)) for match in TOP_VENUE_RE.finditer(text)]
    years = YEAR_RE.findall(text)
    for venue in venues:
        if venue not in constraints.venues:
            continue
        for year in years:
            if year in constraints.years:
                return venue, year
    return "", ""


def is_probable_paper_title(title: str) -> bool:
    return bool(title and len(title) >= 3 and title not in NON_PAPER_TITLES)


def extract_papers(answer: str, constraints: Constraints) -> list[Paper]:
    body = strip_think(answer)
    papers = extract_papers_from_tables(body, constraints)
    papers.extend(extract_papers_from_numbered_lines(body, constraints))
    return dedupe_papers(papers)


def extract_papers_from_tables(answer: str, constraints: Constraints) -> list[Paper]:
    papers: list[Paper] = []
    for line in answer.splitlines():
        if not line.lstrip().startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        row_text = " | ".join(cells)
        if not URL_RE.search(row_text):
            continue
        venue, year = venue_and_year(row_text, constraints)
        if not venue:
            continue
        title = clean_title(cells[0])
        if not is_probable_paper_title(title):
            title_cell = next((cell for cell in cells if URL_RE.search(cell)), cells[-1])
            link_match = re.search(r"\[([^\]]+)\]\([^)]+\)", title_cell)
            title = clean_title(link_match.group(1) if link_match else title_cell)
        if not is_probable_paper_title(title):
            continue
        arxiv_match = ARXIV_RE.search(row_text)
        arxiv_id = arxiv_match.group(1) if arxiv_match else ""
        papers.append(
            Paper(
                title=title,
                venue=venue,
                year=year,
                arxiv_id=arxiv_id,
                mechanism=cell_text(cells, [1, 2]) or infer_mechanism(title, row_text),
                contribution=cell_text(cells, [3, 4]) or "needs_agent_paper_source_verification",
                url=extract_url(row_text, arxiv_id),
            )
        )
    return papers


def extract_papers_from_numbered_lines(answer: str, constraints: Constraints) -> list[Paper]:
    papers: list[Paper] = []
    current_venue = ""
    for line in answer.splitlines():
        heading = re.match(r"\s*#{2,4}\s+\*\*(.+?)\*\*", line)
        if heading:
            venues = [canonical_venue(match.group(1)) for match in TOP_VENUE_RE.finditer(heading.group(1))]
            current_venue = venues[0] if len(venues) == 1 else ""
            continue
        match = re.match(r"\s*\d+\.\s+\*\*(.+?)\*\*\s*(.*)$", line)
        if not match:
            continue
        title = clean_title(match.group(1))
        rest = match.group(2)
        row_text = f"{title} {rest}"
        if current_venue and not TOP_VENUE_RE.search(row_text):
            row_text = f"{current_venue} {row_text}"
        venue, year = venue_and_year(row_text, constraints)
        if not venue or not is_probable_paper_title(title):
            continue
        arxiv_match = ARXIV_RE.search(row_text)
        arxiv_id = arxiv_match.group(1) if arxiv_match else ""
        papers.append(
            Paper(
                title=title,
                venue=venue,
                year=year,
                arxiv_id=arxiv_id,
                mechanism=infer_mechanism(title, row_text),
                contribution=infer_contribution(title, row_text),
                url=extract_url(row_text, arxiv_id),
            )
        )
    return papers


def dedupe_papers(papers: list[Paper]) -> list[Paper]:
    seen: set[str] = set()
    unique: list[Paper] = []
    for paper in papers:
        normalized_title = re.sub(r"[^a-z0-9]+", "", paper.title.lower())
        normalized_url = re.sub(r"[?#].*$", "", paper.url.lower()).rstrip("/")
        key = paper.arxiv_id or normalized_url or normalized_title
        if key in seen:
            continue
        seen.add(key)
        unique.append(paper)
    return unique


def enrich_from_events(papers: list[Paper], events: list[dict[str, Any]]) -> None:
    by_title = {re.sub(r"[^a-z0-9]+", "", p.title.lower()): p for p in papers}
    by_arxiv = {p.arxiv_id: p for p in papers if p.arxiv_id}
    for event in events:
        for result in event.get("results") or []:
            if not isinstance(result, dict):
                continue
            title = re.sub(r"[^a-z0-9]+", "", str(result.get("title") or "").lower())
            arxiv_id = str(result.get("arxiv_id") or "")
            paper = by_arxiv.get(arxiv_id) or by_title.get(title)
            if paper:
                paper.url = paper.url or result.get("url") or build_url(result.get("arxiv_id", ""))
                paper.arxiv_id = paper.arxiv_id or result.get("arxiv_id", "")
                if not paper.authors and isinstance(result.get("authors"), list):
                    paper.authors = ", ".join(result["authors"])


def render_markdown(query: str, papers: list[Paper], constraints: Constraints) -> str:
    year_text = ", ".join(sorted(constraints.years))
    venue_text = ", ".join(sorted(constraints.venues))
    year_source = "defaulted" if constraints.inferred_years else "from query"
    venue_source = "defaulted" if constraints.inferred_venues else "from query"
    lines = [
        "# Candidate Literature From demo.rag.ac.cn",
        "",
        f"**Query:** {query}",
        "",
        f"**Filter:** only papers explicitly mentioned in the raw demo answer; years ({year_source}): {year_text}; venues ({venue_source}): {venue_text}.",
        "",
        "**Verification status:** candidates only. A Codex agent must verify each paper's mechanism, contribution, pseudocode, and formula design from the paper/original page, then select at most 5 most relevant/reference-worthy papers before producing the final cleaned Markdown.",
        "",
        "## Papers",
        "",
    ]
    if not papers:
        lines.append("_No papers matching the query-inferred year/venue constraints were explicitly extractable from the raw answer._")
        return "\n".join(lines) + "\n"
    for index, paper in enumerate(papers, 1):
        title = f"[{paper.title}]({paper.url})" if paper.url else paper.title
        lines.extend(
            [
                f"{index}. **{title}**",
                f"   - Venue/year: {paper.venue} {paper.year}",
                f"   - arXiv: {paper.arxiv_id or 'not provided in raw answer'}",
                f"   - Authors: {paper.authors or 'not provided in raw answer'}",
                f"   - Citation: {paper.citation or 'not provided in raw answer'}",
                f"   - Raw mechanism clue: {paper.mechanism}",
                f"   - Raw contribution clue: {paper.contribution}",
                "   - Pseudocode/formula design: required in final Markdown after paper-source verification",
                "   - Agent verification: required before final use",
                "",
            ]
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract query-constrained candidate papers from demo transcript.")
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--events")
    parser.add_argument("--output", required=True)
    parser.add_argument("--candidates-json", help="Write extracted candidates and constraints as JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_transcript(args.transcript)
    query = data.get("query", "")
    constraints = infer_constraints(query)
    papers = extract_papers(data.get("answer", ""), constraints)
    enrich_from_events(papers, load_events(args.events))
    if args.candidates_json:
        payload = {
            "query": query,
            "constraints": constraints_to_dict(constraints),
            "papers": [paper_to_dict(paper) for paper in papers],
            "verification_required": True,
            "verification_rule": (
                "For every candidate paper, an agent must inspect the paper/original page and replace raw clues with "
                "verified core mechanism, core contribution, pseudocode, and formula design. Final output keeps at most "
                "5 papers ranked by relevance, constraint match, quality, and reference value. Core mechanism means how "
                "the method works; core contribution means the new insight/breakthrough and problem/phenomenon addressed. "
                "Each should be about 150-300 Chinese characters. Pseudocode should be 6-15 lines, and formulas should "
                "show the core signal/objective/scoring rule/decoding update/loss/module transformation."
            ),
        }
        os.makedirs(os.path.dirname(os.path.abspath(args.candidates_json)) or ".", exist_ok=True)
        with open(args.candidates_json, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
    markdown = render_markdown(query, papers, constraints)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(markdown)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
