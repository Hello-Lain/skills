# Literature RAG Final Contract

Use this only inside the literature-rag subagent workflow.

## Pipeline

1. Preserve the user's prompt; do not over-normalize.
2. Run `scripts/manage_outputs.py --workdir "$PWD" --owned-md cleanup`.
3. Put events/transcripts/candidates/quality reports under `${TMPDIR:-$HOME/tmp}/literature-rag-<slug>/`.
4. Run `scripts/demo_chat.py "<prompt>" --jsonl-events "$tmp/events-N.jsonl" --transcript "$tmp/transcript-N.json"`.
5. Run `scripts/assess_response.py --transcript "$tmp/transcript-N.json" --output "$tmp/quality-N.json"`.
6. If the raw answer is generic, irrelevant, too short, lacks links, violates constraints, or quality exits `3`, sharpen the prompt using failure reasons and retry. Max 3 retries after the initial call.
7. After an accepted raw answer, run `scripts/clean_literature.py --transcript "$tmp/transcript-N.json" --events "$tmp/events-N.jsonl" --output "$tmp/candidates.md" --candidates-json "$tmp/candidates.json"`.
8. Read accepted raw answer + candidates JSON. Verify each candidate from original paper/arXiv/DOI/publisher/venue sources.
9. Select at most 5 papers by relevance, constraint match, paper quality, and reference value. Fewer high-confidence papers beat weak filler.
10. If no valid papers remain, write a final Markdown saying no matches were found and explain exclusions.

## Selection Rules

- Strictly respect year, venue, topic, and method-type constraints.
- Links, DOI/arXiv/publisher pages, and venue pages must refer to the same paper.
- For defect-solution queries, exclude the baseline/problem-defining paper unless it proposes a separate remedy.
- Drop any paper whose mechanism, contribution, formula, usefulness, or verification source cannot be checked.

## Final Markdown

Required:

- Original query and quality-gate/retry note.
- At most 5 selected papers.
- For each paper: title/link, venue/year, core mechanism, core contribution, useful transferable insight, pseudocode/formula design, formula source, formula evidence, verification source.
- `Core mechanism`: central method, modules/signals/objectives/pipeline, and how it solves the target problem.
- `Core contribution`: new insight/breakthrough and why it solves the problem.
- `Why useful`: concrete reusable idea, signal, module, objective, ablation, or failure-mode insight.
- Pseudocode: 6-15 substantive method-specific lines, not generic loops.
- Formulas: 1-3 key signals/objectives/scoring rules/updates/losses/transformations.
- `paper formula` only if directly present in the paper; cite Eq./Algorithm/Section/page/source URL.
- `derived formula` if abstracted from verified method text; cite exact basis.
- `## Excluded candidates` section with concrete reasons.

## Audit JSON

Save same-prefix `<final>.audit.json` next to the final Markdown.

Minimum schema:

```json
{
  "query": "original user query",
  "final_markdown": "/abs/path/final.md",
  "selection_policy": "at_most_5_relevance_constraints_quality_reference_value",
  "papers": [
    {
      "index": 1,
      "title": "paper title",
      "url": "https://...",
      "venue": "CVPR",
      "year": "2025",
      "title_match": true,
      "venue_verified": true,
      "constraint_match": true,
      "method_relevance": "why relevant",
      "mechanism_verified": true,
      "contribution_verified": true,
      "pseudocode_quality": "method_specific",
      "formula_source_type": "paper formula | derived formula",
      "formula_evidence_url": "https://...",
      "formula_evidence_locator": "Eq. 3 / Algorithm 1 / Section 4.2 / page 6",
      "formula_evidence_quote": "short evidence clue",
      "derived_from": "required for derived formula",
      "why_useful": "transferable insight",
      "keep": true,
      "drop_reason": ""
    }
  ],
  "excluded_candidates": [
    {
      "title": "dropped paper",
      "url": "https://...",
      "reason": "concrete exclusion reason"
    }
  ]
}
```

## Finalization

After saving:

```bash
python scripts/manage_outputs.py --workdir "$PWD" register "$PWD/<final>.md" "$PWD/<final>.audit.json"
python scripts/validate_final.py --workdir "$PWD"
python scripts/audit_final.py --workdir "$PWD"
```

Fix content or remove weak papers until both checks pass. Do not bypass validation.
