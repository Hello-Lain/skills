---
name: literature-rag
description: Original demo.rag.ac.cn real-time DeepXiv chat wrapper. Use when Codex needs the same conversational literature-search behavior as the website, including streamed analysis, live search progress, and paper recommendations from prompts such as "请帮我找到和resnet相关的24-26年的论文".
---

# Literature RAG

## Quick Start

Use the demo chat stream, not the data API, when the user wants the original webpage effect:

```bash
python scripts/demo_chat.py "请帮我找到和resnet相关的24-26年的论文"
```

`demo_chat.py` calls `POST https://demo.rag.ac.cn/api/chat/stream`, parses SSE events, prints answer tokens in real time to stdout, and prints search/thinking progress to stderr. Default `effort` is `thorough`, matching the website option `Thorough - Deep research`.

## Auth

- Require a demo browser session token in `RAG_DEMO_TOKEN`.
- `scripts/demo_chat.py` automatically loads `.env` from this skill directory before reading environment variables.
- Get it by logging in with Google at `https://demo.rag.ac.cn/login`, then reading `localStorage.auth_token` in the browser.
- A local gitignored `.env` in this skill directory may hold `RAG_DEMO_TOKEN`; never paste tokens into Markdown, logs, transcripts, final answers, or committed files.
- Only the logged-in demo browser `localStorage.auth_token` is supported.
- Treat `401` or `403` as expired/invalid demo token and ask for a fresh browser `auth_token`.

## Main-Agent Workflow

When this skill triggers, the main agent must delegate the full retrieval workflow to a subagent to avoid polluting the main context with raw demo transcripts, candidate lists, and paper bodies.

1. Create one subagent in the user's current working directory. If no subagent tool is available, stop and tell the user this skill requires subagent execution.
2. Give the subagent the original user query, this skill path, and the current working directory. Do not preload raw demo output, prior final answers, or expected papers.
3. Wait for the subagent to finish. If it requests permission, handle that request; otherwise do not inspect temporary transcript/event/candidate files.
4. After completion, run `python ~/.codex/skills/literature-rag/scripts/validate_final.py --workdir "$PWD"` and `python ~/.codex/skills/literature-rag/scripts/audit_final.py --workdir "$PWD"`; read only their JSON reports plus the final Markdown if both pass.
5. Accept the result only if both validation scripts pass and the final Markdown satisfies the Main-Agent Acceptance Checklist below. If it fails, send exactly one correction request to the same subagent and wait again.
6. Report to the user only the final Markdown path, retry count/quality-gate status if stated, and any residual limitations. Do not paste raw demo responses.

Use this subagent prompt template:

```text
Use the literature-rag skill at ~/.codex/skills/literature-rag to answer this literature-search request end-to-end:

<USER_QUERY>

Run the complete Subagent Workflow from SKILL.md. Keep all raw demo transcripts, SSE events, quality reports, candidates, and paper-fetch notes under `${TMPDIR:-$HOME/tmp}`. Save exactly one final verified Markdown file and its same-prefix .audit.json in <WORKDIR>, register both with scripts/manage_outputs.py, and ensure no other final literature-rag output remains in <WORKDIR>.

Before finalizing, verify every selected paper from original sources. The final Markdown must include title/link, venue/year, core mechanism, core contribution, why useful/transferable insight, pseudocode/formula design, formula source, formula evidence, verification source, and an Excluded candidates summary. Write <final>.audit.json using the schema in SKILL.md. Include a short quality-gate note describing whether the initial raw answer passed or whether retries were used. Run scripts/validate_final.py --workdir <WORKDIR> and scripts/audit_final.py --workdir <WORKDIR> before returning.

Return only: final Markdown path, audit JSON path, retry count, accepted raw-answer quality status, number of papers selected, excluded candidate count with reasons summary, and both validation checks performed.
```

## Main-Agent Acceptance Checklist

- `scripts/validate_final.py --workdir "$PWD"` and `scripts/audit_final.py --workdir "$PWD"` both return `passed: true`.
- Exactly one registered final Markdown and one same-prefix `.audit.json` exist in the user's current working directory; no stale literature-rag output remains.
- The final Markdown contains the original user query and a quality-gate/retry note.
- The final Markdown has at most 5 selected papers.
- Every selected paper has title/link, venue/year, core mechanism, core contribution, why useful/transferable insight, pseudocode/formula design, formula source, formula evidence, and verification source.
- Every selected paper visibly matches the user's year, venue, topic, and method-type constraints.
- Paper links, DOI/arXiv/publisher pages, and venue pages must point to the same paper. Mismatched verification links fail.
- `paper formula` is allowed only when the formula is directly found in the paper and the output names the equation/algorithm/section/page source. Otherwise use `derived formula`.
- Pseudocode/formulas must be method-specific and useful for research design. Generic loops, placeholder formulas, or vague score functions fail.
- The audit JSON has one `keep=true` entry for each Markdown paper and records every excluded candidate with a concrete reason.
- If no valid papers exist, the Markdown says so explicitly and explains exclusions instead of relaxing constraints.

## Subagent Workflow

The subagent must execute this workflow, not the main agent.

1. Preserve the user's prompt as a conversational query. Do not over-normalize it; the demo backend performs its own analysis and search planning.
2. At the start of every new literature answer, run `python scripts/manage_outputs.py --workdir "$PWD" --owned-md cleanup` to delete the previous round's registered output and stale literature-rag Markdown only.
3. Put `--jsonl-events`, `--transcript`, candidate Markdown, `--candidates-json`, and quality reports under a temporary directory such as `${TMPDIR:-$HOME/tmp}/literature-rag-<slug>/`, not in the user's working directory.
4. Run `scripts/demo_chat.py "<current prompt>" --jsonl-events "$tmp/events-<n>.jsonl" --transcript "$tmp/transcript-<n>.json"`.
5. Watch stderr for `[search]`, `[done]`, `[retry]`, and `[error]` progress lines. Do not copy the raw stream into the main-agent response.
6. Before candidate cleaning, run `python scripts/assess_response.py --transcript "$tmp/transcript-<n>.json" --output "$tmp/quality-<n>.json"`. Exit code `0` means the raw answer is heuristically usable; exit code `3` means retry is required.
7. Read the full raw demo answer and `$tmp/quality-<n>.json` before cleaning. The script is a gate, not the final judge: if the raw answer is generic, irrelevant, venue/year-hallucinated, too short, mostly a survey, lacks links, lacks query-constrained candidates, or would not satisfy the user, mark it failed even if the heuristic passed.
8. If the raw answer fails quality, rewrite the next prompt using the failure reasons in `quality-<n>.json`: preserve the original constraints, make the topic sharper, require exact `title / venue-year / arXiv-or-official-link / method type / why relevant`, forbid generic surveys and irrelevant baselines, and require “no valid matches” instead of fabricated venue/year. Retry the demo call. Do at most 3 retries after the initial call.
9. Only after an answer passes the agent quality gate, run `python scripts/clean_literature.py --transcript "$tmp/transcript-<n>.json" --events "$tmp/events-<n>.jsonl" --output "$tmp/candidates.md" --candidates-json "$tmp/candidates.json"`. The candidate extraction step must keep only papers explicitly mentioned in the accepted raw demo answer. It infers year and venue constraints from the user's query, e.g. `23-26年` means `2023-2026`, and `CVPR,Neurips，AAAI,ICLR` means only those venues.
10. Candidate files are temporary extraction artifacts only, not the final answer.
11. Before producing final Markdown, read the full accepted raw demo answer and the candidates JSON, then verify every candidate paper one by one from its paper page, arXiv page, DOI page, or publisher page. If the demo answer lacks enough detail, search/read the original paper source to fill missing mechanism and contribution.
12. Select at most 5 papers for the final Markdown. Rank candidates by relevance to the user's stated problem, venue/year constraint match, paper quality, and reference value. Use "宁缺毋滥": fewer high-confidence papers are better than five weak or partially verified papers. Drop weaker or less relevant candidates even if they passed extraction.
13. If the user asks for papers that `solve`, `address`, `mitigate`, `improve`, or `overcome` a defect, exclude the original/baseline paper that introduced the defective method unless it also proposes a separate remedy to its own defect. Do not include a problem-defining paper as a solution paper.
14. If all 3 retries fail or strict year/venue/topic constraints leave no valid solution papers, write a final Markdown that explicitly says no matching papers were found and explains which raw-answer defects or cited papers caused exclusion. Do not relax constraints silently and do not fill the list with related-but-invalid papers.
15. For every final paper, include only verified information: title, link, venue/year, core mechanism, core contribution, why useful/transferable insight, and pseudocode/formula design.
16. Define `Core mechanism` as the paper's central method: how the method works, main modules/signals/objectives/pipeline, and how it solves the target problem. Write about 150-300 Chinese characters per paper.
17. Define `Core contribution` as the new insight or breakthrough: what problem/phenomenon the paper identifies, what new view or capability it introduces, and how that leads to solving the problem. Write about 150-300 Chinese characters per paper.
18. Define `Why useful / transferable insight` as what the user can actually reuse: a research idea, module abstraction, scoring signal, training objective, ablation direction, or failure-mode insight. It must be concrete enough to inspire implementation or experiment design.
19. Define `Pseudocode and formula design` as a compact operational abstraction of the paper's core innovation. Include 6-15 substantive pseudocode lines and 1-3 formulas that show the key signal, objective, scoring rule, decoding update, loss, or module transformation. Do not use placeholder formulas such as `score=f(x)`.
20. Formula source discipline is strict. Use `paper formula` only if the formula is directly present in the paper, and include `Formula evidence: Eq. <n> / Algorithm <n> / Section <name> / page <n> from <source URL>`. If the formula is an agent abstraction from verified text, use `derived formula` and explain the exact method paragraph/algorithm/section it was derived from. Never label a derived abstraction as `paper formula`.
21. Pseudocode/formulas must make the method's core innovation visually obvious. Avoid generic training loops unless the loop exposes the paper's unique mechanism. Use clear variable names and short Chinese notes.
22. Mechanism, contribution, pseudocode, formulas, and usefulness cannot be copied from regex clues alone. They must be checked against the paper/original page. If a field cannot be verified or reasonably derived from accessible sources after search, remove that paper from the final list rather than marking it uncertain.
23. Before saving, run a self-audit over every selected paper: (a) title/venue/link refer to the same paper, (b) formula source label is honest, (c) pseudocode has method-specific steps, (d) usefulness insight is actionable, (e) the paper would help the user beyond a generic citation. Remove any paper that fails.
24. Save exactly one final verified Markdown file in the user's current working directory as `$PWD/<descriptive-name>.md`. Include a short `## Excluded candidates` section; it can summarize the audit JSON exclusions, but must not omit that exclusions exist.
25. Save a same-prefix audit JSON as `$PWD/<descriptive-name>.audit.json`. Use this schema exactly:

```json
{
  "query": "原始用户问题",
    "final_markdown": "~/path/to/final.md",
  "selection_policy": "at_most_5_relevance_constraints_quality_reference_value",
  "papers": [
    {
      "index": 1,
      "title": "论文标题",
      "url": "论文主链接",
      "venue": "CVPR",
      "year": "2025",
      "title_match": true,
      "venue_verified": true,
      "constraint_match": true,
      "method_relevance": "与用户问题的直接关系，50-150字",
      "mechanism_verified": true,
      "contribution_verified": true,
      "pseudocode_quality": "method_specific",
      "formula_source_type": "paper formula | derived formula",
      "formula_evidence_url": "https://...",
      "formula_evidence_locator": "Eq. 3 / Algorithm 1 / Section 4.2 / page 6",
      "formula_evidence_quote": "不超过25词或60个汉字的短证据线索",
      "derived_from": "仅 derived formula 必填，说明来自哪个方法段/算法/图示",
      "why_useful": "可复用的研究启发，50-150字",
      "keep": true,
      "drop_reason": ""
    }
  ],
  "excluded_candidates": [
    {
      "title": "被排除论文",
      "url": "https://...",
      "reason": "年份/venue不符、非解决方案、公式不可核验、帮助弱等"
    }
  ]
}
```

26. After saving both files, run `python scripts/manage_outputs.py --workdir "$PWD" register "$PWD/<descriptive-name>.md" "$PWD/<descriptive-name>.audit.json"`, then run `python scripts/validate_final.py --workdir "$PWD"` and `python scripts/audit_final.py --workdir "$PWD"`. If either fails, fix the content or remove weak papers; do not bypass validation. Remove or leave only temporary artifacts outside `$PWD`; the user's working directory should contain only this single final output pair for the round.

## Final Markdown Format

```markdown
# <topic> Verified Literature

**Query:** <original user query>
**Selection rule:** at most 5 papers, selected by relevance, constraint match, paper quality, and reference value.

1. **[Paper title](link)**
   - Venue/year: <venue year>
   - Core mechanism: <150-300 Chinese characters, verified from paper/original source>
   - Core contribution: <150-300 Chinese characters, verified from paper/original source>
   - Why useful / transferable insight: <concrete reusable idea, signal, module, objective, ablation, or failure-mode insight>
   - Pseudocode and formula design:
     ```text
     # 6-15 lines; expose the core innovation, not a generic loop
     ```
     Formula:
     $$ <1-3 paper or derived formulas> $$
     Formula source: <paper formula | derived formula>
     Formula evidence: <Eq./Algorithm/Section/page/source URL for paper formula, or exact verified text basis for derived formula>
   - Verification source: <paper/arXiv/DOI/publisher URL>

## Excluded candidates

- <title>: <exclusion reason>
```

## Examples

```bash
python scripts/demo_chat.py "请帮我找到和resnet相关的24-26年的论文"
python scripts/demo_chat.py "Find recent papers about ResNet variants in remote sensing" --effort thorough
python scripts/demo_chat.py "总结2025年NeurIPS里和diffusion相关的论文" --jsonl-events events.jsonl --transcript transcript.json
python scripts/manage_outputs.py --workdir "$PWD" --owned-md cleanup
mkdir -p "${TMPDIR:-$HOME/tmp}"
tmp="$(mktemp -d "${TMPDIR:-$HOME/tmp}/literature-rag-XXXXXX")"
python scripts/demo_chat.py "帮我检索解决MLLM中的视觉幻觉现象问题的24-26年发表的顶刊顶会文献" --jsonl-events "$tmp/events.jsonl" --transcript "$tmp/transcript.json"
python scripts/assess_response.py --transcript "$tmp/transcript.json" --output "$tmp/quality.json"
python scripts/clean_literature.py --transcript "$tmp/transcript.json" --events "$tmp/events.jsonl" --output "$tmp/candidates.md" --candidates-json "$tmp/candidates.json"
# Verify candidates against original paper sources, write "$PWD/mllm-visual-hallucination.md", then:
python scripts/manage_outputs.py --workdir "$PWD" register "$PWD/mllm-visual-hallucination.md" "$PWD/mllm-visual-hallucination.audit.json"
python scripts/validate_final.py --workdir "$PWD"
python scripts/audit_final.py --workdir "$PWD"
```

## Token Extraction Link

Ask the user to open `https://demo.rag.ac.cn` in a browser where they are already logged in, then run the bookmarklet from `references/api.md` to display `localStorage.auth_token`.
