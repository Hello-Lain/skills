---
name: literature-rag
description: "Use when the user wants the original demo.rag.ac.cn literature-search experience: streamed answers, live search progress, paper recommendations, or DeepXiv-style retrieval such as ResNet papers from 2024 to 2026. Delegate the full retrieval workflow to a subagent and keep raw demo transcripts out of the main context."
---

# Literature RAG

Use `scripts/demo_chat.py`; it calls the demo chat stream with `effort=thorough` by default. Final Markdown and audit JSON must include handoff data.

## Auth

- `RAG_DEMO_TOKEN` is required.
- `scripts/demo_chat.py` loads `.env` in this skill directory first.
- 401/403 usually means expired or invalid demo token.

## Main Agent

- Delegate the full retrieval workflow to a subagent.
- If no subagent tool is available, stop and tell the user this skill needs subagent execution.
- Pass only the original user query, this skill path, and the current workdir.
- Do not preload raw demo output, candidate lists, prior final answers, or expected papers.
- After completion, run `scripts/validate_final.py --workdir "$PWD"` and `scripts/audit_final.py --workdir "$PWD"` and read only their JSON reports plus the final Markdown.
- Accept only if validation passes and the final Markdown meets the checklist in `references/final_contract.md`.
- If needed, send one correction request to the same subagent and wait again.
- Report only the final Markdown path, audit JSON path, retry count or gate status, handoff next action, and residual limitations.

## Subagent

- Read `references/final_contract.md` before search/finalization.
- Keep raw transcripts, SSE events, candidate files, and quality reports under `${TMPDIR:-$HOME/tmp}`.
- Run `scripts/manage_outputs.py --workdir "$PWD" --owned-md cleanup` at the start of each round.
- Call `scripts/demo_chat.py`, then `scripts/assess_response.py`; retry only when quality fails.
- Only after the raw answer passes, run `scripts/clean_literature.py`.
- Verify every selected paper from original sources before final Markdown.
- Save exactly one final Markdown and one same-prefix `.audit.json`, both with handoff data, register both, then run validate/audit.
- Keep the user's working directory free of stale literature-rag outputs except the final pair.

## Token Extraction

Open `https://demo.rag.ac.cn` while logged in, then use the bookmarklet in `references/api.md` to copy `localStorage.auth_token` into `RAG_DEMO_TOKEN`.
