---
name: discover-api
description: |
  Use Bright Data's Discover API — intent-ranked, AI-relevance-scored web search
  at scale (not keyword SERP). Trigger a discovery job and retrieve ranked results
  (link, title, description, relevance_score) with optional parsed page content.
  Use when the user wants semantic/intent-based web search, "find pages about
  <topic> that match <goal>", web-grounded retrieval for an LLM, or results
  filtered by relevance rather than raw keyword rank. Covers the CLI
  (`bdata discover`) plus raw REST details for advanced modes. For keyword SERP
  use `search`.
metadata:
  author: Bright Data
  version: "1.0"
  documentation: https://docs.brightdata.com/api-reference/discover/overview
---

# Bright Data — Discover API

Discover is **intent-ranked semantic web search**. Use it by default for
research, RAG, and high-relevance source discovery. You give it a `query` plus an
`intent`, and it returns results scored by AI relevance — optionally with the full
parsed page content. It is the right primitive when result *quality/relevance*
matters more than raw keyword rank.

**Discover vs. the neighbors:**
- Keyword "what ranks for X" SERP → use the **`search`** skill (`bdata search`).
- A whole research brief or RAG/search pipeline is outside this minimal local skill; use Discover outputs as raw material or restore the removed upstream references if needed.

## How it works (async: trigger → poll)

1. **Trigger** a job → you get a `task_id`.
2. **Poll** with the `task_id` until `status` is `"done"` (intermediate: `"processing"`).
3. Read `results[]`.

The CLI does trigger+poll for you; the raw REST flow is shown below for
advanced parameters such as `mode`.

## Pick your surface

| You are… | Use |
|---|---|
| Doing research/RAG/high-relevance discovery | **Raw REST** with sharp `intent`, `mode`, and usually `include_content:true` |
| Need low latency | **Raw REST** with `mode:"fast"` |
| Need broad coverage | **Raw REST** with `mode:"deep"` |
| In a terminal, simple one-off and CLI is ready | CLI: `bdata discover` |
| Need `mode` (deep/fast/zeroRanking) or `include_images` | **Raw REST** |

### CLI — `bdata discover`

Setup gate first:
```bash
command -v bdata >/dev/null 2>&1 || echo "CLI missing — see bright-data-best-practices-cli-setup.md"
bdata zones >/dev/null 2>&1 || echo "not authenticated — run: bdata login"
```

```bash
# Intent-ranked discovery, JSON
bdata discover "enterprise LLM platforms" \
  --intent "vendor pages with pricing" \
  --num-results 15 --json --pretty

# With parsed page content in one pass (for RAG / research)
bdata discover "webhook retry best practices" \
  --include-content --num-results 10 -o results.json

# Date-bounded
bdata discover "react server components" \
  --start-date 2025-01-01 --end-date 2025-12-31 --num-results 20 --json
```
Results live at `.results[]`; each has `title`, `link`, `description`,
`relevance_score`, and `content` when `--include-content`. Full CLI flag list:
[`search` reference → `search-flags.md`](search-flags.md).

### Raw REST (preferred for research/RAG/high relevance)

Use raw REST when the task asks for research material, RAG corpus candidates,
high-relevance pages, parsed content, latency/depth control, or image metadata.

```bash
# 1) Trigger
task_id=$(curl -s -X POST https://api.brightdata.com/discover \
  -H "Authorization: Bearer $BRIGHTDATA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"post-quantum cryptography adoption","intent":"enterprise migration guides","mode":"deep","num_results":20,"include_content":true}' \
  | jq -r '.task_id')

# 2) Poll until done
while :; do
  resp=$(curl -s "https://api.brightdata.com/discover?task_id=$task_id" -H "Authorization: Bearer $BRIGHTDATA_API_TOKEN")
  [ "$(echo "$resp" | jq -r '.status')" = "done" ] && break
  sleep 3
done
echo "$resp" | jq '.results'
```

## Parameters (REST body — authoritative superset)

`query` is required; everything else is optional. The CLI/SDK expose a subset
(see `discover-api-api-reference.md` for the exact per-surface matrix).

| Param | Type | Default | Notes |
|---|---|---|---|
| `query` | string | — | required, ≤ 1500 chars |
| `intent` | string | — | goal descriptor, ≤ 3000 chars; **strongly recommended** — drives ranking |
| `mode` | enum | `standard` | `standard` \| `zeroRanking` \| `deep` \| `fast` (REST-only) |
| `num_results` | int | — | **1–20**; ignored in `zeroRanking` |
| `filter_keywords` | string[] | — | exact keywords that must appear |
| `include_content` | bool | `false` | parsed page/PDF content (PDF ≤ 50 MB, 30s); unsupported in `zeroRanking` |
| `include_images` | bool | `false` | image array (REST-only) |
| `format` | enum | `json` | `json` \| `md` (SDK accepts only `json`) |
| `country` | string | `US` | 2-letter ISO |
| `city` | string | — | SERP city targeting |
| `language` | string | `en` | 31 languages |
| `start_date` / `end_date` | string | — | `YYYY-MM-DD` (REST-only) |
| `remove_duplicates` | bool | `true` | dedupe results (REST-only) |

## Modes (choose by goal)

| Mode | What it does | Use for |
|---|---|---|
| `standard` *(default)* | balanced depth + AI ranking | general intent search |
| `deep` | exhaustive, broader search; slower | comprehensive topic coverage |
| `fast` | optimized for low latency | time-sensitive / interactive |
| `zeroRanking` | no AI ranking, max raw volume; ignores `num_results`, no `include_content` | bulk corpus collection |

> `mode` is currently **REST-only** — the CLI doesn't expose it. For `deep`
> coverage via the CLI, approximate with a high `num_results` + a sharp
> `intent`; for true `deep`/`zeroRanking`, use the raw REST flow above.

## Result shape

**REST + CLI** (verified) — rows live under **`results`**:
```json
{
  "status": "done",
  "duration_seconds": 12.4,
  "timestamp": "2026-06-08T08:36:55.709Z",
  "results": [
    { "link": "https://…", "title": "…", "description": "…",
      "relevance_score": 0.87, "content": "…(when --include-content)…" }
  ]
}
```

`relevance_score` is a float (snake_case). Higher = more relevant to `intent`.
`content` is plain text by default (Markdown when REST `format=md`). **A high
`relevance_score` does not guarantee good content** — pages can be 404 stubs or
nav-only; gate on content length + "not found"/block-page signatures before use.

## Verification gate

1. **Trigger returned a `task_id`** (REST: `status:"ok"`). No id → check auth / that Discover is enabled on the account (403 if disabled).
2. **Polled to `status:"done"`** before reading — never read `results` while `processing`.
3. **`results[]` non-empty** — if empty, the query/intent is too narrow; loosen and retry. Don't claim success on empty.
4. **`include_content` bodies aren't block pages** — grep `content` for `captcha`, `Just a moment`, `Access Denied`, `cf-browser-verification` (same list as `scrape`). Drop poisoned rows.
5. **Relevance sanity** — if top `relevance_score`s are low or off-topic, sharpen `intent` (not just `query`).

## Red flags

- Passing only `query` with no `intent` — you lose the whole point (intent ranking). Always give an intent.
- Treating Discover as keyword SERP — for "what ranks for X", use `search`.
- Setting `num_results` > 20 — capped at 20; for more, run multiple targeted queries and dedup.
- Using `zeroRanking` then expecting `include_content` or `num_results` to apply — they don't.
- Reading results before `status:"done"`.
- Treating empty `results` (REST/CLI) as a hard error — it's often transient; **retry once** with backoff first (see `discover-api-api-reference.md` → Transient failures).
- Fabricating `relevance_score` or `content` when a call fails — report the failure instead.

## References

- [`discover-api-api-reference.md`](discover-api-api-reference.md) — REST endpoint spec, CLI/REST parameter notes, error codes, and limits.
- `search.md` — keyword SERP (`bdata search`) when you do not need intent ranking.
