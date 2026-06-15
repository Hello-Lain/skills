#!/usr/bin/env python3
"""Assess raw demo answers before candidate cleaning/verification."""

from __future__ import annotations

import argparse
import json
import os
import re
from typing import Any

from clean_literature import extract_papers, infer_constraints, strip_think

LOW_QUALITY_PATTERNS = [
    "无法找到",
    "没有找到",
    "未找到",
    "no matching",
    "not find",
    "没有足够",
    "建议进一步",
    "待确认",
    "未核验",
]

GENERIC_PATTERNS = [
    "综述",
    "趋势",
    "建议阅读",
    "相关方向",
    "可以关注",
    "建议关注",
    "趋势",
    "可能相关",
    "可作为参考",
    "背景文献",
]

DISALLOWED_CANDIDATE_PATTERNS = [
    "workshop",
    "arxiv only",
    "arxiv-only",
    "preprint only",
    "only arxiv",
    "survey",
    "benchmark",
    "dataset",
    "综述",
    "基准",
    "数据集",
    "相关工作",
]

STOPWORDS = {
    "http",
    "https",
    "arxiv",
    "abs",
    "paper",
    "papers",
    "论文",
    "文献",
    "顶刊",
    "顶会",
    "发表",
    "待发表",
    "检索",
    "找到",
    "了解",
    "相关",
    "类似",
    "方法",
    "解决",
    "问题",
    "请",
    "帮我",
    "更",
    "但是",
    "倾向",
}

def load_transcript(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)

def topic_terms(query: str) -> list[str]:
    lowered = query.lower()
    lowered = re.sub(r"https?://\S+", " ", lowered)
    lowered = re.sub(r"20?\d{2}|[0-9]{2}\s*[-~–—到至]\s*[0-9]{2}", " ", lowered)
    lowered = re.sub(r"[，。！？；、,.!?;:：()\[\]（）《》\"'`]+", " ", lowered)
    for stop in sorted(STOPWORDS, key=len, reverse=True):
        lowered = lowered.replace(stop, " ")
    terms = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}|[\u4e00-\u9fff]{2,8}", lowered)
    cleaned = []
    for term in terms:
        if term in STOPWORDS:
            continue
        if any(term == venue.lower() for venue in ["cvpr", "iccv", "eccv", "neurips", "iclr", "icml", "aaai", "acl", "emnlp", "coling"]):
            continue
        cleaned.append(term)
    return cleaned[:12]

def list_like_items(answer: str) -> int:
    count = 0
    for line in answer.splitlines():
        stripped = line.strip()
        if re.match(r"^\d+\.\s+", stripped) or stripped.startswith("|"):
            count += 1
    return count

def disallowed_candidate_hits(papers: list[Any]) -> tuple[list[str], int]:
    hits: list[str] = []
    bad_papers = 0
    for paper in papers:
        text = " ".join(
            [
                str(getattr(paper, "title", "")),
                str(getattr(paper, "venue", "")),
                str(getattr(paper, "mechanism", "")),
                str(getattr(paper, "contribution", "")),
            ]
        ).lower()
        paper_bad = False
        for pattern in DISALLOWED_CANDIDATE_PATTERNS:
            if pattern.lower() in text:
                hits.append(pattern)
                paper_bad = True
        if paper_bad:
            bad_papers += 1
    return sorted(set(hits)), bad_papers

def mentions_constraints(answer: str, query: str) -> dict[str, Any]:
    constraints = infer_constraints(query)
    years_hit = sorted(year for year in constraints.years if year in answer)
    venues_hit = sorted(venue for venue in constraints.venues if re.search(rf"(?<![A-Za-z]){re.escape(venue)}(?![A-Za-z])", answer, re.I))
    return {
        "years_hit": years_hit,
        "venues_hit": venues_hit,
        "years_total": sorted(constraints.years),
        "venues_total": sorted(constraints.venues),
    }

def score_response(query: str, answer: str) -> dict[str, Any]:
    clean = strip_think(answer).strip()
    constraints = infer_constraints(query)
    papers = extract_papers(clean, constraints)
    terms = topic_terms(query)
    term_hits = [term for term in terms if term.lower() in clean.lower()]
    links = re.findall(r"https?://|arXiv:|arxiv\.org/abs/", clean, re.I)
    constraint_hits = mentions_constraints(clean, query)
    list_items = list_like_items(clean)
    disallowed_hits, disallowed_count = disallowed_candidate_hits(papers)

    score = 0
    reasons: list[str] = []
    warnings: list[str] = []
    hard_fail = False

    if len(clean) >= 1200:
        score += 2
    else:
        reasons.append("raw answer too short for reliable cleaning")

    if len(papers) >= 3:
        score += 3
    elif papers:
        score += 1
        reasons.append("too few query-constrained candidate papers")
    else:
        reasons.append("no extractable papers satisfying query-inferred year/venue constraints")
        hard_fail = True

    if links:
        score += 1
    else:
        reasons.append("answer lacks paper links/arXiv identifiers")
        hard_fail = True

    if term_hits or not terms:
        score += 1
    else:
        reasons.append("answer does not visibly cover the query topic terms")
        hard_fail = True

    if constraint_hits["years_hit"]:
        score += 1
    else:
        reasons.append("answer does not visibly mention requested years")
        hard_fail = True

    if constraint_hits["venues_hit"] or constraints.inferred_venues:
        score += 1
    else:
        reasons.append("answer does not visibly mention requested venues")
        hard_fail = True

    low_quality_hits = [p for p in LOW_QUALITY_PATTERNS if p.lower() in clean.lower()]
    if low_quality_hits and len(papers) < 3:
        reasons.append("answer explicitly signals missing/insufficient retrieval")

    generic_hits = [p for p in GENERIC_PATTERNS if p.lower() in clean.lower()]
    if generic_hits and len(papers) < 3:
        warnings.append("answer appears generic relative to requested paper list")
        hard_fail = True

    if papers and disallowed_count == len(papers):
        reasons.append(f"candidate set appears dominated by non-solution/non-top-venue items: {', '.join(disallowed_hits)}")
        hard_fail = True

    if list_items >= 3 and len(papers) < 3:
        reasons.append("answer has list/table structure but too few rows include title + venue/year + link that match constraints")
        hard_fail = True

    if not constraints.inferred_venues:
        invalid_venue_mentions = re.findall(r"\bworkshop\b|arxiv\s*only|preprint\s*only", clean, re.I)
        if invalid_venue_mentions and len(papers) < 3:
            reasons.append("answer includes workshop/arXiv-only/preprint-only items under strict venue constraints")
            hard_fail = True

    passed = score >= 7 and len(papers) >= 3 and not hard_fail and not (low_quality_hits and len(papers) < 3)
    return {
        "passed": passed,
        "score": score,
        "reasons": reasons,
        "warnings": warnings,
        "candidate_count": len(papers),
        "list_like_items": list_items,
        "disallowed_candidate_hits": disallowed_hits,
        "disallowed_candidate_count": disallowed_count,
        "topic_terms": terms,
        "topic_term_hits": term_hits,
        "constraint_hits": constraint_hits,
        "retry_prompt": build_retry_prompt(query, reasons, warnings, constraints),
    }

def build_retry_prompt(query: str, reasons: list[str], warnings: list[str], constraints: Any) -> str:
    year_text = ", ".join(sorted(constraints.years))
    venue_text = ", ".join(sorted(constraints.venues))
    issue_text = "; ".join(reasons + warnings) or "上一轮回答未达到可清洗质量"
    return (
        f"{query}\n\n"
        "上一轮检索结果质量不足，问题是："
        f"{issue_text}。\n"
        "请重新进行深度检索，严格按以下要求输出：\n"
        f"1. 年份只能是：{year_text}。\n"
        f"2. 会议/期刊范围只能是：{venue_text}。\n"
        "3. 只列与用户问题直接相关、可作为解决方案或关键参考的方法论文；不要给泛泛综述、趋势或无关基线。\n"
        "4. 每篇必须给出 title、venue/year、arXiv/DOI/official link、方法类别、为何与问题匹配。\n"
        "5. 如果严格条件下没有足够论文，明确说明无匹配项，不要编造 venue 或年份。"
    )

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assess raw demo answer quality before cleaning.")
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    data = load_transcript(args.transcript)
    report = score_response(str(data.get("query", "")), str(data.get("answer", "")))
    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    print(args.output)
    return 0 if report["passed"] else 3

if __name__ == "__main__":
    raise SystemExit(main())
