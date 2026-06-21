---
name: brightdata-web-scrape
description: >
  Scrape known web pages with Bright Data CLI. Use for `bdata scrape`, Web Unlocker via CLI, page-to-markdown/HTML/JSON/screenshot output, single URL or batch URL collection, pagination patterns, anti-bot/CAPTCHA handling through Bright Data, and scrape command flags/examples.
---

# Bright Data Web Scrape

Collect content from known URLs through Bright Data CLI.

## Workflow

1. Confirm Bright Data setup exists; if not, use `../brightdata-setup/SKILL.md`.
2. If URLs are unknown, use `../brightdata-web-search/SKILL.md` first.
3. Read `references/scrape.md` for the core scrape workflow and command shape.
4. Read only the needed detail:
   - `references/scrape-flags.md` for output formats, screenshots, waits, geo, concurrency, or headers.
   - `references/scrape-patterns.md` for batching, pagination, retries, dedupe, and content normalization.
   - `references/scrape-examples.md` for concrete command examples.
5. Choose the smallest output format that satisfies the task: markdown for reading, HTML for structure, JSON when supported/needed, screenshot for visual evidence.
6. Save bulky outputs to files when useful; summarize results without dumping large page content into the final answer.

## Boundaries

- Do not scrape private, paywalled, credentialed, or sensitive pages unless the user has explicit rights and provides safe access instructions.
- Do not expose cookies, auth headers, tokens, API keys, or session material.
- Do not use upstream custom scraper, Scraper Studio, proxy-code templates, or platform-data workflows.
