# MCP Validation Matrix

## Summary
- Date: 2026-06-22.
- Scope: Current `mcp__brightdata` tools available in this Codex session.
- Result: Partial PASS. `discover`, `search_engine_batch`, `scrape_batch`, and `session_stats` worked. `extract` and `web_data_github_repository_file` exposed reliability/config blockers that require fallback guidance.
- Efficiency signal: `search_engine_batch` handled two Google queries in one call; `scrape_batch` fetched two pages in one call.
- Stability signal: batch tools returned structured per-item status/result records; failures returned explicit errors rather than silent partial success.

## Calls

### 1. `session_stats` before validation
- Input class: usage tracking.
- Status: PASS.
- Output check: returned session counts for prior MCP calls.
- Fallback decision: none.
- Evidence: showed prior calls to `scrape_as_markdown`, `scrape_as_html`, `discover`, and `session_stats`.

### 2. `discover`
- Input class: AI-ranked source discovery.
- Query: `Bright Data MCP official GitHub tools documentation discover search_engine_batch scrape_batch extract`.
- Status: PASS.
- Output check: returned five ranked results with links, titles, descriptions, and relevance scores.
- Best official/primary result: `https://docs.brightdata.com/ai/mcp-server/tools`.
- Fallback decision: use `search_engine` or web search only if `discover` gives irrelevant or zero results.
- Efficiency/stability signal: one call ranked sources instead of requiring manual result filtering.

### 3. `search_engine_batch`
- Input class: two independent Google queries.
- Queries:
  - `site:github.com/brightdata/brightdata-mcp assets Tools.md scrape_batch extract discover`
  - `site:github.com/brightdata/brightdata-mcp web_data_github_repository_file session_stats`
- Status: PASS.
- Output check: both query results returned in one array; first found `assets/Tools.md` and repo root; second found `manifest.json` and `assets/Tools.md`.
- Fallback decision: use single `search_engine` only for pagination or one query; use `web.run` only if MCP unavailable or results require browser/source citations outside Bright Data.
- Efficiency/stability signal: two independent SERP calls collapsed into one batch request.

### 4. `scrape_batch`
- Input class: known public URLs.
- URLs:
  - `https://example.com/`
  - `https://www.iana.org/domains/reserved`
- Status: PASS.
- Output check: both items returned `status: fulfilled` with URL and markdown content; content was non-empty and not a block page.
- Fallback decision: use `scrape_as_markdown` for one page, `scrape_batch` for 2-5 pages, CLI scrape when output must be saved/replayed.
- Efficiency/stability signal: two URL reads completed in one request with per-URL fulfillment status.

### 5. `extract`
- Input class: structured JSON extraction from `https://example.com/`.
- Prompt: keys `title`, `primary_link_text`, `primary_link_url`.
- Status: FAIL.
- Output check: no JSON returned.
- Error: `MCP error -32601: sampling/createMessage`.
- Fallback decision: guidance must say `extract` depends on MCP sampling support; if unavailable or malformed, scrape markdown/html then parse manually or use CLI/agent-side extraction.
- Reliability signal: failure was explicit and actionable.

### 6. `web_data_github_repository_file`
- Input class: GitHub single-file structured reader.
- URL: `https://github.com/brightdata/brightdata-mcp/blob/main/assets/Tools.md`.
- Status: FAIL.
- Output check: no file content returned.
- Error: `HTTP 400: Customer is not active`.
- Fallback decision: guidance must say this reader is preferred only when account/tool access is active; fall back to direct GitHub raw/web, local `git clone`, or repo-aware tools when inactive or when many files/history/tests are needed.
- Reliability signal: failure identifies account activation rather than ambiguous scrape failure.

### 7. `session_stats` after validation
- Input class: usage tracking.
- Status: PASS.
- Output check: counts increased for `discover`, `search_engine_batch`, `scrape_batch`, `extract`, `web_data_github_repository_file`, and `session_stats`.
- Fallback decision: use before/after validation-heavy MCP work to expose usage/cost trend.

## Guidance Impact
- Promote `discover`, `search_engine_batch`, and `scrape_batch` to MCP-first for matching tasks.
- Promote `extract` only with a sampling-support check and hard fallback.
- Promote `web_data_github_repository_file` only with active account/tool access and hard fallback.
- Require output inspection before success claims.
- Record empty output, explicit MCP errors, and account/sampling blockers in artifacts rather than hiding them.
