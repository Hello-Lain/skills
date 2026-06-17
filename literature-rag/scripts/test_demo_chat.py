#!/usr/bin/env python3
"""Tests for demo_chat.py."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from assess_response import score_response
from clean_literature import extract_papers, infer_constraints, render_markdown
from demo_chat import parse_args, parse_sse_events
from manage_outputs import cleanup, register


def write_valid_markdown(path: Path) -> None:
    path.write_text(
        """# VCD Defect Verified Literature

**Query:** q
**Quality gate:** initial raw answer passed after 1 retry.
**Selection rule:** at most 5 papers.

1. **[Paper A](https://example.com/a)**
   - Venue/year: CVPR 2024
   - Core mechanism: 方法说明。
   - Core contribution: 贡献说明。
   - Why useful / transferable insight: 这个方法给用户的可迁移启发是把核心信号抽成可替换模块，能直接启发后续实验设计。
   - Pseudocode and formula design:
     ```text
     input x
     encode evidence e
     compute signal s
     apply method-specific update u
     rank candidate outputs
     return best output
     ```
     Formula:
     $$ c_t = \\cos(e_t, v_t) - \\lambda \\max(0, h_{lang} - h_{vis}) $$
     Formula source: derived formula
     Formula evidence: derived from Method section and Algorithm 1 description on the verified paper page.
   - Verification source: https://example.com/a

## Excluded candidates

- None.

## Handoff

- Goal: Produce a verified literature summary.
- Current state: One validated paper selected.
- Authoritative artifacts: final.md, final.audit.json.
- Decisions: Keep only the verified paper.
- Verification: validate_final.py and audit_final.py pass.
- Remaining risks: None.
- Next action: Use this Markdown and audit pair as the continuation artifact.
- Suggested skills: literature-rag, conductor.
- Redactions / omitted raw data: Raw demo transcript and SSE events stay in tmp.
""",
        encoding="utf-8",
    )


def write_valid_audit(path: Path, markdown: Path, *, source_type: str = "derived formula") -> None:
    paper = {
        "index": 1,
        "title": "Paper A",
        "url": "https://example.com/a",
        "venue": "CVPR",
        "year": "2024",
        "title_match": True,
        "venue_verified": True,
        "constraint_match": True,
        "method_relevance": "该方法直接面向用户问题中的视觉证据约束，可作为后续实验中的核心解码信号设计参考。",
        "mechanism_verified": True,
        "contribution_verified": True,
        "pseudocode_quality": "method_specific",
        "formula_source_type": source_type,
        "formula_evidence_url": "https://example.com/a",
        "formula_evidence_locator": "Section 3.2 Algorithm 1",
        "formula_evidence_quote": "method-specific signal update",
        "derived_from": "Derived from Method section and Algorithm 1 on the verified paper page.",
        "why_useful": "这个方法给用户的可迁移启发是把核心信号抽成可替换模块，能直接启发后续实验设计。",
        "keep": True,
        "drop_reason": "",
    }
    if source_type == "paper formula":
        paper["formula_evidence_locator"] = "Eq. 3, page 5"
        paper["derived_from"] = ""
    path.write_text(
        json.dumps(
            {
                "query": "q",
                "final_markdown": str(markdown),
                "selection_policy": "at_most_5_relevance_constraints_quality_reference_value",
                "papers": [paper],
                "excluded_candidates": [],
                "handoff": {
                    "goal": "Produce a verified literature summary.",
                    "current_state": "One validated paper selected.",
                    "authoritative_artifacts": [str(markdown), str(markdown.with_suffix(".audit.json"))],
                    "decisions": ["Keep only the verified paper."],
                    "verification": ["validate_final.py", "audit_final.py"],
                    "remaining_risks": ["None."],
                    "next_action": "Use this Markdown and audit pair as the continuation artifact.",
                    "suggested_skills": ["literature-rag", "conductor"],
                    "redactions_or_omitted_raw_data": ["Raw demo transcript and SSE events stay in tmp."],
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


class DemoChatTests(unittest.TestCase):
    def test_parse_sse_events(self) -> None:
        chunks = [
            b'data: {"type":"answer_start"}\n\n',
            b'data: {"type":"token","content":"hello"}\n\n',
            b'data: {"type":"sql_done","task":"search","row_count":2}\n\n',
        ]
        events = list(parse_sse_events(chunks))
        self.assertEqual(events[0]["type"], "answer_start")
        self.assertEqual(events[1]["content"], "hello")
        self.assertEqual(events[2]["row_count"], 2)

    def test_parse_error(self) -> None:
        events = list(parse_sse_events([b"data: not-json\n\n"]))
        self.assertEqual(events[0]["type"], "parse_error")

    def test_default_effort_is_thorough(self) -> None:
        args = parse_args(["query"])
        self.assertEqual(args.effort, "thorough")

    def test_extract_top_venue_paper(self) -> None:
        answer = '''1. **"V-DPO: Mitigating Hallucination in Large Vision Language Models via Vision-Guided Direct Preference Optimization"** - ICLR 2025
   - arXiv: 2411.02712
   - Citation: 64
   - Authors: Yuxi Xie et al.

1. **"Some preprint"** - arXiv 2025
   - arXiv: 2501.00001
'''
        papers = extract_papers(answer, infer_constraints("检索24-26年ICLR论文"))
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].venue, "ICLR")
        self.assertEqual(papers[0].year, "2025")

    def test_infer_query_constraints(self) -> None:
        constraints = infer_constraints("23-26年的CVPR,Neurips，AAAI,ICLR文献")
        self.assertEqual(constraints.years, {"2023", "2024", "2025", "2026"})
        self.assertEqual(constraints.venues, {"CVPR", "NeurIPS", "AAAI", "ICLR"})
        self.assertFalse(constraints.inferred_years)
        self.assertFalse(constraints.inferred_venues)

    def test_candidate_markdown_requires_agent_verification(self) -> None:
        constraints = infer_constraints("检索24-26年ICLR论文")
        markdown = render_markdown("检索24-26年ICLR论文", [], constraints)
        self.assertIn("candidates only", markdown)
        self.assertIn("agent must verify", markdown)
        self.assertIn("at most 5", markdown)
        self.assertIn("pseudocode", markdown)
        self.assertIn("formula", markdown)

    def test_assess_response_rejects_low_quality_answer(self) -> None:
        report = score_response(
            "检索24-26年CVPR论文解决视觉幻觉",
            "没有找到足够相关论文，建议进一步搜索。",
        )
        self.assertFalse(report["passed"])
        self.assertIn("retry_prompt", report)
        self.assertIn("严格按以下要求", report["retry_prompt"])

    def test_assess_response_accepts_candidate_rich_answer(self) -> None:
        answer = """1. **"Paper A: Mitigating Visual Hallucination"** - CVPR 2024
   - arXiv: 2401.00001
   - Link: https://arxiv.org/abs/2401.00001
   - Method: visual hallucination mitigation.
2. **"Paper B: Training-Free Visual Hallucination Reduction"** - CVPR 2025
   - arXiv: 2501.00002
   - Link: https://arxiv.org/abs/2501.00002
   - Method: training-free decoding for visual hallucination.
3. **"Paper C: Hallucination Alignment"** - CVPR 2026
   - arXiv: 2601.00003
   - Link: https://arxiv.org/abs/2601.00003
   - Method: alignment for visual hallucination.
""" + ("视觉幻觉 " * 300)
        report = score_response("检索24-26年CVPR论文解决视觉幻觉", answer)
        self.assertTrue(report["passed"])
        self.assertEqual(report["candidate_count"], 3)

    def test_assess_response_rejects_generic_survey_like_answer(self) -> None:
        answer = """以下是建议关注的趋势和可能相关文献：
| Paper | Venue | Link |
| --- | --- | --- |
| **A Survey on MLLM Hallucination** | arXiv only 2025 | https://arxiv.org/abs/2501.11111 |
| **Visual Hallucination Benchmark Dataset** | Workshop 2024 | https://example.com/workshop |
| **Related Work Summary** | arXiv only 2026 | https://arxiv.org/abs/2601.22222 |
"""
        report = score_response("检索24-26年CVPR论文解决视觉幻觉", answer)
        self.assertFalse(report["passed"])
        self.assertTrue(report["reasons"])

    def test_table_title_cleaning_prefers_real_title_after_br(self) -> None:
        answer = """| Paper | Method | Why | Link |
| --- | --- | --- | --- |
| **VCD** [[CVPR 2024]](https://openaccess.thecvf.com/) <br> *Mitigating Object Hallucinations in Large Vision-Language Models through Visual Contrastive Decoding* | training-free decoding | uses distorted visual contrast | https://arxiv.org/abs/2401.00001 |
"""
        papers = extract_papers(answer, infer_constraints("23-26年的CVPR文献"))
        self.assertEqual(len(papers), 1)
        self.assertEqual(
            papers[0].title,
            "Mitigating Object Hallucinations in Large Vision-Language Models through Visual Contrastive Decoding",
        )
        self.assertNotIn("Targets VCD defect", papers[0].contribution)

    def test_cleanup_owned_markdown_removes_stale_skill_outputs_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            owned = root / "old-result.md"
            normal = root / "notes.md"
            owned.write_text(
                "# Test Verified Literature\n\n**Query:** q\n\nCore mechanism:\nCore contribution:\nVerification source:\n",
                encoding="utf-8",
            )
            normal.write_text("# Personal note\n", encoding="utf-8")
            cleanup(tmp, owned_md=True)
            self.assertFalse(owned.exists())
            self.assertTrue(normal.exists())

    def test_validate_final_accepts_well_formed_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            write_valid_markdown(final)
            audit = root / "final.audit.json"
            write_valid_audit(audit, final)
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("validate_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue(json.loads(proc.stdout)["passed"])

    def test_validate_final_rejects_missing_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            audit = root / "final.audit.json"
            write_valid_markdown(final)
            final.write_text(final.read_text(encoding="utf-8").split("\n## Handoff\n", 1)[0], encoding="utf-8")
            write_valid_audit(audit, final)
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("validate_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("Handoff", proc.stdout)

    def test_validate_final_rejects_missing_quality_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            final.write_text(
                """# Bad

**Query:** q

1. **[Paper A](https://example.com/a)**
   - Venue/year: CVPR 2024
   - Core mechanism: 方法说明。
   - Core contribution: 贡献说明。
   - Pseudocode and formula design: x
     Formula source: derived formula
   - Verification source: https://example.com/a
""",
                encoding="utf-8",
            )
            register(tmp, [str(final)])
            script = Path(__file__).with_name("validate_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("quality", proc.stdout.lower())

    def test_validate_final_rejects_paper_formula_without_evidence_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            final.write_text(
                """# Bad Formula Evidence

**Query:** q
**Quality gate:** passed after retry.

1. **[Paper A](https://example.com/a)**
   - Venue/year: CVPR 2024
   - Core mechanism: 方法说明。
   - Core contribution: 贡献说明。
   - Why useful / transferable insight: 这个方法能启发用户把视觉证据约束做成独立打分项，而不是只依赖语言模型输出。
   - Pseudocode and formula design:
     ```text
     input x
     encode image evidence
     compute visual score
     compute language score
     subtract unsupported language prior
     decode next token
     ```
     Formula:
     $$ z = a - b $$
     Formula source: paper formula
     Formula evidence: copied from the paper.
   - Verification source: https://example.com/a
""",
                encoding="utf-8",
            )
            register(tmp, [str(final)])
            script = Path(__file__).with_name("validate_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("evidence anchor", proc.stdout)

    def test_validate_final_rejects_missing_linked_paper_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            audit = root / "final.audit.json"
            write_valid_markdown(final)
            final.write_text(
                final.read_text(encoding="utf-8").replace(
                    "1. **[Paper A](https://example.com/a)**",
                    "1. **Paper A**",
                ),
                encoding="utf-8",
            )
            write_valid_audit(audit, final)
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("validate_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("link format", proc.stdout)

    def test_validate_final_rejects_more_than_15_pseudocode_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            audit = root / "final.audit.json"
            write_valid_markdown(final)
            text = final.read_text(encoding="utf-8")
            long_code = "\n".join(f"     step {index}" for index in range(1, 17))
            text = text.replace(
                """     input x
     encode evidence e
     compute signal s
     apply method-specific update u
     rank candidate outputs
     return best output""",
                long_code,
            )
            final.write_text(text, encoding="utf-8")
            write_valid_audit(audit, final)
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("validate_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("more than 15", proc.stdout)

    def test_validate_final_rejects_generic_formula(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            audit = root / "final.audit.json"
            write_valid_markdown(final)
            final.write_text(
                final.read_text(encoding="utf-8").replace(
                    "$$ c_t = \\cos(e_t, v_t) - \\lambda \\max(0, h_{lang} - h_{vis}) $$",
                    "$$ score = g(x) $$",
                ),
                encoding="utf-8",
            )
            write_valid_audit(audit, final)
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("validate_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("too generic", proc.stdout)

    def test_audit_final_accepts_valid_markdown_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            audit = root / "final.audit.json"
            write_valid_markdown(final)
            write_valid_audit(audit, final)
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("audit_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue(json.loads(proc.stdout)["passed"])

    def test_audit_final_rejects_missing_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            audit = root / "final.audit.json"
            write_valid_markdown(final)
            write_valid_audit(audit, final)
            data = json.loads(audit.read_text(encoding="utf-8"))
            data.pop("handoff")
            audit.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("audit_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("audit.handoff", proc.stdout)

    def test_validate_final_rejects_missing_audit_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            write_valid_markdown(final)
            register(tmp, [str(final)])
            script = Path(__file__).with_name("validate_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("audit JSON", proc.stdout)

    def test_audit_final_rejects_paper_formula_without_locator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            audit = root / "final.audit.json"
            write_valid_markdown(final)
            write_valid_audit(audit, final, source_type="paper formula")
            data = json.loads(audit.read_text(encoding="utf-8"))
            data["papers"][0]["formula_evidence_locator"] = "copied from paper"
            audit.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("audit_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("locator", proc.stdout)

    def test_audit_final_rejects_derived_formula_without_derived_from(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            audit = root / "final.audit.json"
            write_valid_markdown(final)
            write_valid_audit(audit, final)
            data = json.loads(audit.read_text(encoding="utf-8"))
            data["papers"][0]["derived_from"] = ""
            audit.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("audit_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("derived_from", proc.stdout)

    def test_audit_final_rejects_markdown_paper_without_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            audit = root / "final.audit.json"
            write_valid_markdown(final)
            final.write_text(
                final.read_text(encoding="utf-8").replace(
                    "1. **[Paper A](https://example.com/a)**",
                    "1. **Paper A**",
                ),
                encoding="utf-8",
            )
            write_valid_audit(audit, final)
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("audit_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("linked", proc.stdout)

    def test_audit_final_rejects_wrong_audit_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            audit = root / "other.audit.json"
            write_valid_markdown(final)
            write_valid_audit(audit, final)
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("audit_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("same-prefix", proc.stdout)

    def test_audit_final_rejects_dropped_paper_in_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            audit = root / "final.audit.json"
            write_valid_markdown(final)
            write_valid_audit(audit, final)
            data = json.loads(audit.read_text(encoding="utf-8"))
            data["papers"][0]["keep"] = False
            data["papers"][0]["drop_reason"] = "公式无法核验"
            data["excluded_candidates"] = [{"title": "Paper A", "url": "https://example.com/a", "reason": "公式无法核验"}]
            audit.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("audit_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("keep=false", proc.stdout)

    def test_audit_final_rejects_no_kept_papers_without_exclusions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            final = root / "final.md"
            audit = root / "final.audit.json"
            final.write_text(
                """# No Match

**Query:** q
**Quality gate:** passed after retry.

无匹配文献。

## Handoff

- Goal: Produce a verified literature summary.
- Current state: No kept papers.
- Authoritative artifacts: final.md, final.audit.json.
- Decisions: Drop all candidates.
- Verification: audit_final.py pending expected rejection.
- Remaining risks: No excluded candidate details.
- Next action: Add concrete exclusions.
- Suggested skills: literature-rag.
- Redactions / omitted raw data: Raw demo transcript and SSE events stay in tmp.
""",
                encoding="utf-8",
            )
            audit.write_text(
                json.dumps(
                    {
                        "query": "q",
                        "final_markdown": str(final),
                        "selection_policy": "at_most_5_relevance_constraints_quality_reference_value",
                        "papers": [],
                        "excluded_candidates": [],
                        "handoff": {
                            "goal": "Produce a verified literature summary.",
                            "current_state": "No kept papers.",
                            "authoritative_artifacts": [str(final), str(audit)],
                            "decisions": ["Drop all candidates."],
                            "verification": ["audit_final.py pending expected rejection."],
                            "remaining_risks": ["No excluded candidate details."],
                            "next_action": "Add concrete exclusions.",
                            "suggested_skills": ["literature-rag"],
                            "redactions_or_omitted_raw_data": ["Raw demo transcript and SSE events stay in tmp."],
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            register(tmp, [str(final), str(audit)])
            script = Path(__file__).with_name("audit_final.py")
            proc = subprocess.run(
                [sys.executable, str(script), "--workdir", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("excluded_candidates", proc.stdout)


if __name__ == "__main__":
    unittest.main()
