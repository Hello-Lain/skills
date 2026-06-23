---
name: brightdata-web-search
description: >
  Search the web with Bright Data. Use for Bright Data `bdata search`, Google/Bing/Yandex SERP, SERP API via CLI, Discover API semantic search, research/RAG/high-relevance web discovery, finding candidate URLs before scraping, query flags, search result formats, and search-to-scrape workflows that need live web discovery.
---

# Bright Data Web Search

Find URLs or semantic web results before optional scraping.

## Workflow

1. If `mcp__brightdata` tools are available and shell reproducibility is not required, prefer `../brightdata-mcp-tools/SKILL.md` for relevance discovery (`discover`), multiple queries (`search_engine_batch`), and MCP usage tracking (`session_stats`).
2. Choose the surface before setup:
   - Keyword SERP / "what ranks for X" → `bdata search`.
   - Research, RAG, high-relevance source discovery, or "find pages about X for goal Y" → **Discover API**; prefer raw REST when content, `mode`, or API control matters.
   - Simple semantic one-off with CLI already available → `bdata discover` is acceptable.
3. Confirm setup for the chosen surface; CLI needs `bdata` auth, raw REST Discover needs `BRIGHTDATA_API_TOKEN` and Discover enabled. If missing, use `../brightdata-setup/SKILL.md`.
4. Read `references/search.md` for SERP/search workflow; for research/RAG/high-relevance tasks, read `references/discover-api.md` first and `../brightdata-mcp-tools/references/bright-data-mcp-research-rag.md` when using MCP.
5. Read only the needed detail:
   - `references/search-flags.md` for engines, geo/language, formats, pagination, or output flags.
   - `references/search-patterns.md` for query design, result filtering, dedupe, or search→scrape flow.
   - `references/search-examples.md` for concrete command examples.
   - `references/discover-api.md` for semantic Discover workflows.
   - `references/discover-api-api-reference.md` for Discover parameters and response details.
6. Use search/discover to identify sources; use `../brightdata-web-scrape/SKILL.md` only after URLs are known and Discover did not already return adequate `content`.
7. Distinguish live results from command examples; cite commands/output actually used.

## Boundaries

- Do not scrape pages from search results unless the user asks or the workflow requires it.
- Do not use platform-data feeds, pipelines, business-analysis templates, SEO audits, or brand-listening workflows.
- Redact credentials and avoid logging raw secrets in query examples.
