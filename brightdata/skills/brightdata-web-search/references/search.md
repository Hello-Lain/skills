---
name: search
description: Search the web via Bright Data — `bdata search` for Google/Bing/Yandex SERP, `bdata discover` for simple intent-ranked semantic results, and Discover API raw REST for research/RAG/high-relevance source discovery. Use when the user wants SERP results, needs URLs to feed into scraping, or wants semantic web discovery with optional page content.
---

# Bright Data — Search

Find things on the web. Route by search intent:

- **`bdata search`** — classic keyword SERP (Google/Bing/Yandex). Best when you want "what ranks for keyword X."
- **Discover API** — AI intent-ranked discovery with optional page content. Best for research, RAG, high-relevance source discovery, or "pages about topic Y that match goal Z."
- **`bdata discover`** — CLI wrapper for simple Discover jobs when CLI setup already exists.

## Setup gate (run after choosing surface)

For raw REST Discover, skip the CLI gate and verify `BRIGHTDATA_API_TOKEN` plus Discover account access instead (see `discover-api.md`). For CLI surfaces, run:

```bash
if ! command -v bdata >/dev/null 2>&1; then
    echo "bdata CLI not installed — see ../../brightdata-setup/references/bright-data-best-practices-cli-setup.md"
elif ! bdata zones >/dev/null 2>&1; then
    echo "bdata not authenticated — run: bdata login  (or: bdata login --device for SSH)"
fi
```

Halt and route to `../../brightdata-setup/references/bright-data-best-practices-cli-setup.md` if a selected CLI surface fails either check. Do **not** block REST Discover just because `bdata` is missing.

## Pick your path

| Situation | Action |
|---|---|
| Single keyword query, just SERP | `bdata search "<query>" --engine google --json --pretty` |
| Paginated SERP (more results) | loop `--page 0`, `--page 1`, … (0-indexed) |
| Multiple queries | shell loop over a queries file |
| Research / RAG / high-relevance source discovery | read `discover-api.md`; use raw REST with sharp `intent`, `mode`, and often `include_content` |
| Intent-ranked / semantic (not keyword) | `bdata discover "<query>" --intent "<intent>" --num-results 20` |
| Want page bodies along with results, one pass | `bdata discover ... --include-content` |
| News / images / shopping SERP | `bdata search "<query>" --type news` (or `images`, `shopping`) |
| Have URLs, want content | **hand off to `scrape`** |

## Action

Core commands:

```bash
# Google SERP, structured JSON
bdata search "site:example.com privacy policy" --engine google --json --pretty

# Localized Bing (German results, German language)
bdata search "datenschutz" --engine bing --country de --language de --json

# Second page of results (0-indexed)
bdata search "machine learning papers" --page 1 --json

# Mobile SERP (rankings differ from desktop)
bdata search "best coffee shops" --device mobile --json

# News vertical
bdata search "openai" --type news --json --pretty

# Intent-ranked discovery
bdata discover "enterprise LLM platforms" \
    --intent "vendor pages with pricing" \
    --num-results 15 --json

# Discovery with page content in markdown
bdata discover "webhook best practices" \
    --include-content --num-results 10 -o results.json

# Date-filtered discovery
bdata discover "react server components" \
    --start-date 2025-01-01 --end-date 2025-12-31 --num-results 20
```

Full flag reference: [`search-flags.md`](search-flags.md).

### `search` vs `discover` — pick the right one

| You want | Use |
|---|---|
| "What Google ranks for this exact keyword" | `search` |
| "Pages that match this meaning/intent" | `discover` |
| Research/RAG/high-relevance sources with bodies | Discover API raw REST, usually `include_content:true` |
| "News / images / shopping vertical SERP" | `search --type <vertical>` |
| "Results + page bodies in one call" | `discover --include-content` |
| "Dedup / semantic ranking across queries" | `discover` |

## Verification gate

1. **JSON parses cleanly:** `jq . <output>` returns 0.
2. **Result array non-empty** — if empty, the query is legitimately zero-result; relax the query and re-run. Don't claim success on empty results without telling the user.
3. **Required fields present:**
   - `search`: results live at `.organic[]`; each has `title` + `link`
   - `discover`: results live at `.results[]`; each has `title` + `link`; if `--include-content`, also `content`
4. **For `discover --include-content`:** no block-page signatures in the `content` field (same list as scrape, case-insensitive):
   - `Access Denied`
   - `Just a moment`
   - `Attention Required`
   - `Checking your browser`
   - `captcha`
   - `cf-browser-verification`
   - `cloudflare` *(with < 2KB total body)*
5. **Geo sanity:** if the user expected country-specific results, inspect TLDs / languages of top results. If mis-localized, re-run with explicit `--country` and `--language`.

## Red flags

- Scraping every SERP result blindly — filter first (domain allowlist, keyword in title, relevance heuristic).
- Confusing `search` (keyword) with `discover` (semantic). They answer different questions.
- Running multiple queries without deduping URLs across result sets before scraping.
- Assuming SERP order is universal — it's personalized by geo + device. Always set `--country` and `--device` explicitly for reproducibility.
- Using `--page` as a result count — it's a page index, not a limit. Each page returns ~10 results.
- Assuming SERP results are at `.results[]` — for `bdata search` they live at `.organic[]`. (Discover uses `.results[]`.)
- Hardcoding `--num-results 100` on `discover` without realizing the pipeline polls until that many are found; can be slow.

## References

- [`search-flags.md`](search-flags.md) — full flags for `search` and `discover` with when-to-use notes.
- [`search-patterns.md`](search-patterns.md) — multi-query dedup, SERP → filter → scrape pipeline, `search` vs `discover` decision, legacy `curl` fallback, shared verification checklist.
- [`search-examples.md`](search-examples.md) — (1) single Google query, (2) localized Bing, (3) batch queries + dedup into URL list, (4) `discover --include-content` end-to-end.
- [`discover-api.md`](discover-api.md) — REST-first Discover workflow for research/RAG/high-relevance retrieval.
