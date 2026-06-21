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
| Bright Data MCP server setup, tool choice, MCP search/scrape/extract | `skills/brightdata-mcp-tools/SKILL.md` |

Load only the routed child `SKILL.md`, then follow its reference router. If a task spans phases, use setup → search/discover → scrape → MCP only when needed.

## Shared Rules

- Prefer CLI (`bdata`) for local workflows; use MCP only when configured in the active tool layer.
- Keep credentials out of prompts, logs, code, reports, and final answers; rely on local auth or env vars.
- Record blockers when CLI, MCP, network, zones, budget, or auth are unavailable.
- Cite commands/files used for analysis; do not invent live Bright Data results.

## Removed Scope

This local copy intentionally excludes structured platform data feeds, SDK/REST integration, proxy code templates, custom scraper building, Scraper Studio collectors, RAG/live-research pipelines, business-analysis templates, design mirroring, SEO audits, brand listening, price comparison, and Browser session debugging. Reinstall or restore those reference groups from `https://github.com/brightdata/skills` if needed.
