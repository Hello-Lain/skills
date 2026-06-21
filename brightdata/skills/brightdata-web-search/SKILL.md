---
name: brightdata-web-search
description: >
  Search the web with Bright Data. Use for Bright Data `bdata search`, Google/Bing/Yandex SERP, SERP API via CLI, Discover API semantic search, research/RAG/high-relevance web discovery, finding candidate URLs before scraping, query flags, search result formats, and search-to-scrape workflows that need live web discovery.
---

# Bright Data Web Search

Find URLs or semantic web results before optional scraping.

## Workflow

1. Choose the surface before setup:
   - Keyword SERP / "what ranks for X" → `bdata search`.
   - Research, RAG, high-relevance source discovery, or "find pages about X for goal Y" → **Discover API**; prefer raw REST when content, `mode`, or API control matters.
   - Simple semantic one-off with CLI already available → `bdata discover` is acceptable.
2. Confirm setup for the chosen surface; CLI needs `bdata` auth, raw REST Discover needs `BRIGHTDATA_API_TOKEN` and Discover enabled. If missing, use `../brightdata-setup/SKILL.md`.
3. Read `references/search.md` for SERP/search workflow; for research/RAG/high-relevance tasks, read `references/discover-api.md` first.
4. Read only the needed detail:
   - `references/search-flags.md` for engines, geo/language, formats, pagination, or output flags.
   - `references/search-patterns.md` for query design, result filtering, dedupe, or search→scrape flow.
   - `references/search-examples.md` for concrete command examples.
   - `references/discover-api.md` for semantic Discover workflows.
   - `references/discover-api-api-reference.md` for Discover parameters and response details.
5. Use search/discover to identify sources; use `../brightdata-web-scrape/SKILL.md` only after URLs are known and Discover did not already return adequate `content`.
6. Distinguish live results from command examples; cite commands/output actually used.

## Boundaries

- Do not scrape pages from search results unless the user asks or the workflow requires it.
- Do not use platform-data feeds, pipelines, business-analysis templates, SEO audits, or brand-listening workflows.
- Redact credentials and avoid logging raw secrets in query examples.
