# Bright Data MCP Tool Reference

This local skill keeps current MCP tools that improve agent efficiency without restoring full platform-data workflows.

## Current Tools

| Tool | Use |
| --- | --- |
| `discover` | Search and AI-rank sources by relevance, intent, filters, geo, language, and date window |
| `search_engine` | Single Google/Bing/Yandex SERP query with URL/title/description results |
| `search_engine_batch` | Multiple independent SERP queries in one call |
| `scrape_as_markdown` | Read one webpage as clean markdown |
| `scrape_as_html` | Read one webpage as HTML when structure/source details matter |
| `scrape_batch` | Read 2-5 webpages as markdown with per-URL status |
| `extract` | Scrape one URL and AI-extract JSON; requires MCP sampling support or the local skill adapter |
| `session_stats` | Report current-session MCP call counts |

## Selection Rules

- Before declaring a known tool unavailable, use the active tool list; if the environment supports deferred tool discovery, search tool metadata for the expected tool.
- Unknown topic with relevance needs → `discover`, then scrape chosen URLs.
- Several known queries → `search_engine_batch`; single query or pagination → `search_engine`.
- Known URL → `scrape_as_markdown`.
- Need DOM/source details → `scrape_as_html`.
- 2-5 URLs → `scrape_batch`.
- Need a small JSON object from one page → `extract` only when sampling support or the local adapter is available and JSON field checks can pass.
- Need shell reproducibility, saved files, broad repo work, local tests, or history → prefer CLI/repo tools.

## Runtime Checks

- Search: require at least one relevant result or state that no result was found.
- Scrape: require non-empty content and reject block pages.
- Extract: verify required fields exist; do not invent missing fields.
- Stats: use `session_stats` before and after validation-heavy MCP work.

## Conditional Tool Rule

- Do not use `extract` as a default if both sampling support and the local adapter are absent or unverified.
- Do not assume any narrow cached reader is part of the v1 local routing set.
- Treat explicit access, activation, or sampling errors as fallback triggers and record the failure.

## Material Skill-Update Validation Matrix

For material skill updates or reliability claims, run a small public-target matrix and save an artifact:

1. `session_stats` before.
2. `discover` for one public docs/research query.
3. `search_engine_batch` for two independent public queries.
4. `scrape_batch` for 2-3 stable public URLs.
5. `extract` on one stable public page with a small schema prompt.
6. `session_stats` after.

Record tool, input class, success/failure, output check, fallback decision, and efficiency/stability signal. A failed `extract` still validates the fallback rule when the error is explicit.
