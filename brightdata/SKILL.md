---
name: brightdata
description: >
  Hub/router for local Bright Data skills. Use when a request mentions Bright Data, brightdata, bdata, Web Unlocker, SERP/Search API, Discover API, Bright Data MCP, CAPTCHA/bot bypass, scraping, search, or live web data and the best specific Bright Data sub-skill is unclear.
---

# Bright Data

Router-only parent for the local Bright Data skill group. Source license is preserved in `LICENSE`.

## Route

| Need | Use |
| --- | --- |
| Install, login, device auth, API key, auth errors, local prerequisites | `skills/brightdata-setup/SKILL.md` |
| General `bdata` CLI commands, zones, budget, config, status, syntax | `skills/brightdata-cli/SKILL.md` |
| Search engines, SERP, `bdata search`, Discover semantic search | `skills/brightdata-web-search/SKILL.md` |
| Known URL scraping, markdown/HTML/JSON/screenshots, batches, pagination | `skills/brightdata-web-scrape/SKILL.md` |
| Bright Data MCP-first search, batch scrape, extraction, usage stats, MCP setup | `skills/brightdata-mcp-tools/SKILL.md` |

Load only the routed child `SKILL.md`, then follow its reference router. If a task spans phases, use setup → search/discover → scrape with MCP-first at each phase; use CLI only when MCP is unavailable, blocked, or reproducibility/files/tests require it.

## Shared Rules

- Prefer MCP-first for search, relevance discovery, 2-5 URL scrape batches, one-page JSON extraction, and usage tracking when `mcp__brightdata` tools are available.
- Prefer CLI (`bdata`) when MCP is unavailable, output must be saved/replayed from shell, or the task needs local pipelines, files, history, tests, or broad repo work.
- Keep credentials out of prompts, logs, code, reports, and final answers; rely on local auth or env vars.
- Record blockers when CLI, MCP, network, zones, budget, or auth are unavailable.
- Cite commands/files used for analysis; do not invent live Bright Data results.

## Removed Scope

This local copy intentionally excludes structured platform data feeds, SDK/REST integration, proxy code templates, custom scraper building, Scraper Studio collectors, business-analysis templates, design mirroring, SEO audits, brand listening, price comparison, and Browser session debugging. Lightweight research/RAG Discover guidance lives in child references; restore broader upstream reference groups from `https://github.com/brightdata/skills` if needed.
