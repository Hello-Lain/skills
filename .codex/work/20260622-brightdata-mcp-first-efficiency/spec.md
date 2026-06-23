# Spec: Bright Data MCP-first efficiency

## Objective
Upgrade the local Bright Data skill group so future Codex/agent sessions use currently available Bright Data MCP tools first when they improve speed, reliability, or structured output quality, while keeping safe fallbacks.

## Users
- Primary: future Codex/agent sessions operating in `/data/lcq/.codex/skills`.
- Secondary: the user reviewing or extending the Bright Data skill group.

## Problem
The current Bright Data skills describe CLI/search/scrape/MCP basics, but they underuse MCP tools already exposed in this environment. This leads agents to default to `web.run`, `git clone`, or ordinary shell loops for tasks that MCP can do faster or with cleaner structure, especially search discovery, batch scraping, JSON extraction, and GitHub single-file reads.

## Success Criteria
- The Bright Data router and MCP child skill make MCP-first routing explicit for search, batch scrape, extraction, GitHub file reads, and session usage tracking.
- Search/scrape child skills point agents to MCP when `mcp__brightdata` tools are available and the task benefits from them.
- A real MCP validation pass runs against public low-risk targets with about 10-15 total calls and records success/failure, output quality, and fallback behavior.
- The validation pass demonstrates at least one efficiency or stability improvement: fewer tool calls than serial alternatives, direct structured JSON output, cache/structured GitHub file retrieval, or successful anti-bot scrape where ordinary access is unreliable.
- No credentials, API tokens, cookies, private pages, or paid/pro-only setup assumptions are added to skill files or reports.

## Scope
### In
- Update `brightdata/SKILL.md` routing language to prefer MCP when it is already configured and useful.
- Update `brightdata/skills/brightdata-mcp-tools/SKILL.md` and its references with a current MCP-first decision tree.
- Add explicit routing for these currently available MCP tools: `discover`, `search_engine`, `search_engine_batch`, `scrape_as_markdown`, `scrape_as_html`, `scrape_batch`, `extract`, `web_data_github_repository_file`, `web_data_reuter_news`, and `session_stats`.
- Add fallback rules for unavailable tools, empty content, protected/login pages, failed extraction, or tasks requiring repo history/build/test execution.
- Add brief cross-links in `brightdata-web-search` and `brightdata-web-scrape` so agents switch to MCP when available rather than duplicating guidance.
- Add a validation artifact under the topic workspace or skill artifacts area with real MCP call results.

### Out
- Do not enable, install, or configure new MCP tools.
- Do not modify Bright Data credentials, CP settings, tokens, zones, or environment secrets.
- Do not restore full `web_data_*` platform-data skills, Browser automation, dataset search, GEO, Code, Pro groups, or CP configuration docs in v1.
- Do not replace CLI workflows that need reproducible saved files, local shell pipelines, repo history, tests, or broad multi-file repository operations.

## Requirements
### Functional
- Agents must check for available `mcp__brightdata` tools before defaulting to `web.run`, `git clone`, or serial scrape loops for Bright Data-suitable tasks.
- For source discovery, agents should prefer `discover` when relevance ranking or filters matter, and `search_engine_batch` when multiple independent queries are known.
- For known URLs, agents should prefer `scrape_batch` for 2-5 pages, `scrape_as_markdown` for one readable page, and `scrape_as_html` only when structure/DOM details are required.
- For structured fields from one page, agents should prefer `extract` with an explicit schema prompt before manual markdown parsing.
- For GitHub single-file reads, agents should prefer `web_data_github_repository_file` when only a few files are needed; use `git clone` or repository tools when history, many files, tests, or local execution are required.
- Agents should use `session_stats` before and after validation-heavy MCP work to make usage visible.
- Skill guidance must require inspection of MCP outputs before claiming success and must define fallback when output is empty, blocked, malformed, stale, or irrelevant.

### Non-Functional
- Keep guidance short enough for skill loading; detailed validation logs belong in artifacts, not `SKILL.md`.
- Keep credentials out of prompts, files, examples, logs, and final reports.
- Prefer bounded MCP calls and batch tools to reduce latency and request count.
- Preserve current CLI-first guidance where MCP is unavailable, unconfigured, or less reproducible.

## Constraints
- Live validation is mandatory before implementation is accepted.
- Validation budget target is about 10-15 MCP calls total against public low-risk URLs and queries.
- Validation must not depend on `https://brightdata.com/cp/mcp` content because it behaves like an auth-protected control panel page and may return empty output without proving MCP failure.
- Existing unrelated dirty files in the Bright Data skill tree must not be overwritten or reverted.

## Assumptions To Validate
- [ ] `mcp__brightdata` tools remain available in future sessions - validate by checking the tool registry before applying MCP-first rules.
- [ ] `discover` improves source selection for research-like tasks - validate with one public query and relevance inspection.
- [ ] `search_engine_batch` reduces serial search overhead - validate with two independent queries in one call.
- [ ] `scrape_batch` returns usable content for multiple stable public pages - validate with 2-3 simple URLs.
- [ ] `extract` returns usable JSON for a simple public page - validate required fields exist.
- [ ] `web_data_github_repository_file` is reliable for a GitHub blob URL - validate against a public Bright Data MCP repository file.

## Risks
- MCP tools may consume credits - mitigate with a small fixed validation matrix and `session_stats`.
- Auth-protected or dynamic pages may return empty output - mitigate by excluding them from pass/fail validation and documenting fallback.
- MCP outputs may be malformed or incomplete - mitigate with required output checks and fallback to CLI/web/shell tools.
- Over-prioritizing MCP may hurt reproducibility for repo work - mitigate by keeping `git clone` and CLI routes for multi-file/history/test workflows.
- Existing dirty files may contain user changes - mitigate by checking diffs before editing and touching only scoped files.

## Acceptance Checks
- Run a live MCP validation matrix with public targets:
  - `session_stats` before validation.
  - `discover` for one current, public docs/research query.
  - `search_engine_batch` for two independent public queries.
  - `scrape_batch` for 2-3 stable public pages.
  - `extract` on one stable public page with a small schema prompt.
  - `web_data_github_repository_file` on one public GitHub blob URL.
  - `session_stats` after validation.
- Record for each MCP call: tool, input class, success status, output check, fallback decision, and observed efficiency/stability signal.
- Inspect final diffs for only scoped Bright Data skill/reference changes.
- Confirm the updated skills include MCP-first rules, fallback rules, validation requirements, and explicit v1 exclusions.

## Open Questions
- None for spec creation. Implementation may discover that a specific MCP tool is unavailable or unreliable and should record that as validation evidence rather than silently removing the requirement.

## Reviewer Lite Gate
- Route: lite.
- Verdict: PASS.
- Basis: user explicitly approved the restated intent; this spec includes objective, users, problem, testable success criteria, scope in/out, functional requirements, constraints, assumptions, risks, and executable live-MCP acceptance checks.
- Residual risk: live MCP reliability remains unproven until the implementation phase runs the required validation matrix.
