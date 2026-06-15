# Demo RAG Chat API Reference

Use this reference only for reverse-engineering and calling the original `https://demo.rag.ac.cn` real-time webpage behavior.

## Authentication

The demo uses Google Sign-In and stores a browser token in `localStorage.auth_token`.

Use locally:

```bash
export RAG_DEMO_TOKEN="<localStorage.auth_token>"
```

The token is sent as:

```http
Authorization: Bearer <RAG_DEMO_TOKEN>
Content-Type: application/json
```

Only the logged-in demo browser `localStorage.auth_token` is supported.

## Token Extraction Bookmarklet

Open `https://demo.rag.ac.cn` in a browser where you are already logged in, then run this JavaScript URL from the address bar/bookmark:

```text
javascript:(()=>{const t=localStorage.getItem('auth_token');if(!t){alert('No localStorage.auth_token found. Open https://demo.rag.ac.cn/login and sign in first.');return;}document.body.innerHTML='<main style="font:16px/1.5 sans-serif;padding:24px;max-width:900px;margin:auto"><h1>demo.rag.ac.cn token</h1><p>Copy this value into Codex as RAG_DEMO_TOKEN:</p><textarea autofocus style="width:100%;height:160px">'+t.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))+'</textarea></main>';})()
```

If the browser strips `javascript:` when pasted, create a bookmark with this URL, open the logged-in demo page, then click the bookmark.

## Chat Stream

`POST https://demo.rag.ac.cn/api/chat/stream`

Request:

```json
{
  "query": "请帮我找到和resnet相关的24-26年的论文",
  "history": [],
  "effort": "thorough"
}
```

Response is Server-Sent Events. Each event line starts with `data: ` and contains JSON.

Observed event types:

- `thinking`, `thinking_delta`, `thinking_content`: analysis/planning stream.
- `sql_start`: retrieval step started; may include `task` and `sql`.
- `sql_retry`: retrieval step retried; may include `task`, `sql`, `error`.
- `sql_done`: retrieval step complete; may include `task`, `sql`, `row_count`, `results`, `error`.
- `answer_start`: final answer is starting.
- `token`: final answer delta in `content`.
- `done`: terminal event; may include full `answer`.
- `error`: stream error with `message`.

Website effort values are:

- `quick`: `Quick - Fast overview`
- `balanced`: `Balanced - Standard search`
- `thorough`: `Thorough - Deep research`

`demo_chat.py` defaults to `effort=thorough`.

## Session APIs

These reproduce website chat history/sidebar behavior. `demo_chat.py` does not need them for one-shot streaming.

- `GET /api/sessions`: list sessions.
- `POST /api/sessions`: create session.
- `DELETE /api/sessions/{id}`: delete session.
- `PATCH /api/sessions/{id}` with `{ "name": "..." }`: rename session.
- `POST /api/sessions/{id}/generate-name` with `{ "first_query": "..." }`: generate session name.
- `GET /api/sessions/{id}/messages`: list messages.
- `POST /api/sessions/{id}/messages` with `{ "role": "...", "content": "...", "sql_calls": [] }`: persist a message.

## Failure Handling

- Missing token: ask user for `RAG_DEMO_TOKEN`.
- `401` or `403`: token expired/invalid; ask for a fresh browser `localStorage.auth_token`.
- `502`: likely wrong token class or demo backend unavailable.

## Cleaning Requirement

For literature-search tasks, first run `scripts/manage_outputs.py --workdir "$PWD" --owned-md cleanup` to delete the previous round's registered output and stale literature-rag Markdown. Put transcript/events/candidate files under a temporary directory, not the user's working directory. Run `scripts/demo_chat.py` with `--jsonl-events` and `--transcript`, then run `scripts/assess_response.py`; retry with the reported `retry_prompt` when quality fails. Only after the raw answer passes, run `scripts/clean_literature.py --transcript "$tmp/transcript.json" --events "$tmp/events.jsonl" --output "$tmp/candidates.md" --candidates-json "$tmp/candidates.json"`. The extractor reads the raw transcript, extracts only papers explicitly named by the demo answer, infers year/venue constraints from the original query, and writes candidate files.

Candidate files are not final. A Codex agent must verify each candidate paper one by one from its paper page, arXiv page, DOI page, or publisher page. If the demo answer lacks complete information, the cleaning stage must search/read original paper sources to fill missing fields. Then write final Markdown with at most 5 papers selected by relevance, constraint match, paper quality, and reference value:

- title and link
- venue/year
- arXiv ID when available
- authors/citations when available
- verified core mechanism: the paper's central method, i.e. how it works, main modules/signals/objectives/pipeline, and how it solves the target problem; about 150-300 Chinese characters.
- verified core contribution: the new insight or breakthrough, i.e. what problem/phenomenon it identifies, what new view or capability it introduces, and how that leads to solving the problem; about 150-300 Chinese characters.
- why useful / transferable insight: a concrete idea, signal, module, objective, ablation, or failure-mode insight the user can reuse.
- pseudocode and formula design: 6-15 substantive lines of pseudocode plus 1-3 formulas showing the paper's core signal, objective, scoring rule, decoding update, loss, or module transformation. Avoid generic loops and placeholder formulas.
- formula source and evidence: use `paper formula` only for formulas directly present in the paper, with Eq./Algorithm/Section/page evidence; otherwise use `derived formula` and explain the verified method text that supports the abstraction.

Use "宁缺毋滥": fewer high-confidence papers are better than filling five slots. If a mechanism, contribution, usefulness insight, pseudocode, or formula cannot be verified or reasonably derived from an accessible source, remove the paper from the final list. Avoid generic pseudocode; it must expose the paper's distinctive method. The paper link, DOI/arXiv/publisher page, venue page, and verification URL must refer to the same paper.

Every final answer must produce a same-prefix audit JSON next to the final Markdown: `<final>.audit.json`. Register both files. The audit JSON must contain `query`, `final_markdown`, `selection_policy`, `papers`, and `excluded_candidates`. Each kept paper in Markdown must have one audit entry with matching `index`, `title`, and `url`; every dropped candidate must have a concrete exclusion reason. For `paper formula`, provide a formula evidence URL plus Eq./Algorithm/Section/Page locator. For `derived formula`, provide `derived_from` that names the verified method section, paragraph, algorithm, or figure used to derive the abstraction.

For defect-solution queries, exclude the original/baseline paper that introduced the defective method unless it also proposes a separate remedy to that defect. If strict year/venue/topic constraints leave no valid solution papers, write a final Markdown stating that no matching papers were found and list excluded related papers with exclusion reasons. Do not silently relax constraints.

Save exactly one final Markdown file and one audit JSON file in the user's working directory. After saving them, run `scripts/manage_outputs.py --workdir "$PWD" register "$PWD/<final>.md" "$PWD/<final>.audit.json"`, `scripts/validate_final.py --workdir "$PWD"`, and `scripts/audit_final.py --workdir "$PWD"` so the main agent can accept the result from concise JSON reports.
