---
name: brightdata-web-search
description: >
  Search the web with Bright Data. Use for Bright Data `bdata search`, Google/Bing/Yandex SERP, SERP API via CLI, Discover semantic search, finding candidate URLs before scraping, query flags, search result formats, and search-to-scrape workflows that need live web discovery.
---

# Bright Data Web Search

Find URLs or semantic web results before optional scraping.

## Workflow

1. Confirm Bright Data setup exists; if not, use `../brightdata-setup/SKILL.md`.
2. Read `references/search.md` for SERP/search workflow and command shape.
3. Read only the needed detail:
   - `references/search-flags.md` for engines, geo/language, formats, pagination, or output flags.
   - `references/search-patterns.md` for query design, result filtering, dedupe, or search→scrape flow.
   - `references/search-examples.md` for concrete command examples.
   - `references/discover-api.md` for semantic Discover workflows.
   - `references/discover-api-api-reference.md` for Discover parameters and response details.
4. Use search/discover to identify sources; use `../brightdata-web-scrape/SKILL.md` only after URLs are known.
5. Distinguish live results from command examples; cite commands/output actually used.

## Boundaries

- Do not scrape pages from search results unless the user asks or the workflow requires it.
- Do not use platform-data feeds, pipelines, business-analysis templates, SEO audits, or brand-listening workflows.
- Redact credentials and avoid logging raw secrets in query examples.
