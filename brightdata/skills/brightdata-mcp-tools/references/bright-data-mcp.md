---
name: bright-data-mcp
description: Use Bright Data MCP as an agent tool layer for web search and webpage scraping when MCP tools are already configured or the user asks for MCP. This local minimal version excludes platform-specific `web_data_*` workflows.
---

# Bright Data MCP

Use this when the user wants Bright Data through an MCP tool layer instead of shelling out to `bdata`.

## Scope

Kept:
- `search_engine`
- `search_engine_batch`
- `scrape_as_markdown`
- `scrape_as_html`
- `scrape_batch`
- `extract`
- narrow cache/structured readers if already present, such as GitHub file or Reuters article readers

Excluded locally:
- ecommerce/social/business platform data workflows
- broad `web_data_*` platform extraction docs
- browser automation
- Pro group enablement recipes unless needed for the kept tools

## Setup Gate

1. Check available `mcp__brightdata__*` tools.
2. If no Bright Data MCP tools exist, read `bright-data-mcp-mcp-setup.md`.
3. If CLI is simpler for the task, use `brightdata-cli.md` instead.

## Tool Choice

| Need | Tool |
| --- | --- |
| Search SERP/current web | `search_engine` |
| Search multiple independent queries | `search_engine_batch` |
| Read one page as markdown | `scrape_as_markdown` |
| Read one page as HTML | `scrape_as_html` |
| Read up to 5 pages | `scrape_batch` |
| Convert page content to structured JSON | `extract` |
| Read supported GitHub file / Reuters article | matching narrow `web_data_*` reader, if available |

## Validation

- Inspect output before claiming success.
- For search, require non-empty results or explain the zero-result query.
- For scraping, reject block-page signatures: `captcha`, `Access Denied`, `Just a moment`, `Checking your browser`, `cf-browser-verification`.
- For extraction, verify the returned JSON fields match the user’s requested schema.

## References

- `bright-data-mcp-mcp-setup.md` — remote/local connection setup.
- `bright-data-mcp-mcp-tools.md` — kept minimal tool reference.
