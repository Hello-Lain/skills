---
name: bright-data-mcp
description: Use Bright Data MCP as an MCP-first agent tool layer for web search, relevance discovery, batch scraping, conditional extraction, research/RAG discovery, and usage tracking when MCP tools are already configured or the user asks for MCP. This local version keeps only current lightweight tools and excludes broad platform-data workflows.
---

# Bright Data MCP

Use this when Bright Data MCP tools are available and the task can benefit from fewer calls, anti-bot scraping, relevance-ranked discovery, conditional structured extraction, or visible MCP usage stats.

## Scope

Kept current tools:
- `search_engine`
- `search_engine_batch`
- `discover`
- `scrape_as_markdown`
- `scrape_as_html`
- `scrape_batch`
- `extract`
- `session_stats`

Excluded locally:
- ecommerce/social/business platform data workflows
- broad `web_data_*` platform extraction docs
- narrow cached readers
- browser automation
- Pro group enablement recipes unless needed for the kept tools

## Setup Gate

1. Check available `mcp__brightdata` tools.
2. If a known MCP tool is not visible and the environment supports deferred tool discovery, search tool metadata before declaring it unavailable.
3. If no Bright Data MCP tools exist, read `bright-data-mcp-mcp-setup.md`.
4. If CLI is simpler for the task, use `../../brightdata-cli/references/brightdata-cli.md` instead.
5. For validation-heavy MCP work, call `session_stats` before and after to expose usage.

## Runtime Checklist

- Tool is visible or discoverable in current tool metadata.
- Task matches the tool capability and active schema.
- `extract` sampling support is verified, or the local skill adapter is configured, before structured JSON extraction.
- Output is non-empty and not a block page.
- Fallback path is named when the tool is missing, malformed, or blocked.
- Use `session_stats` for validation-heavy or multi-call MCP work.

## Tool Choice

| Need | Tool |
| --- | --- |
| Relevance-ranked source discovery | `discover` |
| Search SERP/current web | `search_engine` |
| Search multiple independent queries | `search_engine_batch` |
| Read one page as markdown | `scrape_as_markdown` |
| Read one page as HTML | `scrape_as_html` |
| Read 2-5 pages | `scrape_batch` |
| Convert one page to structured JSON | `extract`, only when sampling or the local adapter returns valid JSON |
| Track MCP call volume | `session_stats` |

## MCP-First Rules

- Multi-query search → `search_engine_batch` before serial `search_engine` or `web.run`.
- Research/source discovery → `discover` before manual SERP filtering.
- 2-5 known URLs → `scrape_batch` before repeated `scrape_as_markdown`.
- One known URL → `scrape_as_markdown`; use `scrape_as_html` only when DOM/source structure matters.
- One-page JSON fields → `extract` with an explicit schema prompt only when sampling is supported or the local adapter is active; if JSON is malformed, scrape then parse manually.
- Research/RAG source discovery → read `bright-data-mcp-research-rag.md`.

## Validation

- Inspect output before claiming success.
- For search, require non-empty results or explain the zero-result query.
- For scraping, reject block-page signatures: `captcha`, `Access Denied`, `Just a moment`, `Checking your browser`, `cf-browser-verification`.
- For extraction, verify the returned JSON fields match the user’s requested schema.
- Record explicit MCP errors and fallback choices in task artifacts for material workflow changes.

## References

- `bright-data-mcp-mcp-setup.md` — remote/local connection setup.
- `bright-data-mcp-mcp-tools.md` — current tool reference, selection rules, and validation matrix.
- `bright-data-mcp-research-rag.md` — lightweight Discover research/RAG workflow.
