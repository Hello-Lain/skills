# Task 2 Skill Edits

## Changed Files
- `brightdata/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`
- `brightdata/skills/brightdata-web-search/SKILL.md`
- `brightdata/skills/brightdata-web-scrape/SKILL.md`

## Behavior Added
- Parent router now routes Bright Data MCP-first search, batch scrape, extraction, narrow readers, and usage stats to `brightdata-mcp-tools`.
- MCP child skill now checks available `mcp__brightdata` tools before falling back to `web.run`, `git clone`, serial scrapes, or shell loops.
- MCP reference now documents `discover`, `search_engine_batch`, `scrape_batch`, `extract`, `session_stats`, `web_data_github_repository_file`, and `web_data_reuter_news`.
- Fallback rules now cover empty content, block pages, malformed extraction, missing sampling support, account activation errors, auth errors, and workflows needing shell/repo reproducibility.
- Search and scrape child skills now redirect to MCP when MCP tools are available and shell reproducibility is not required.

## Verification
- Ran grep for `MCP-first`, `session_stats`, `web_data_github_repository_file`, `scrape_batch`, and `fallback` across scoped files.
- Result: PASS, 29 matches across the scoped Bright Data files.

## Dirty Work Preservation
- Existing dirty reference path fixes outside this task were not reverted.
- This task did not touch `brightdata/skills/brightdata-setup/references/agent-onboarding.md`, `brightdata/skills/brightdata-setup/references/bright-data-best-practices-cli-setup.md`, `brightdata/skills/brightdata-web-search/references/search.md`, `brightdata/skills/brightdata-web-search/references/discover-api.md`, or `brightdata/skills/brightdata-web-scrape/references/scrape.md`.
