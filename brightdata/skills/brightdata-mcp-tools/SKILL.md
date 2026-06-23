---
name: brightdata-mcp-tools
description: >
  Use Bright Data MCP server/tool guidance. Trigger on Bright Data MCP setup, MCP-first web search, Discover, batch scrape, extraction, session stats, choosing between MCP search/scrape/extract tools, configuring the MCP server for Codex/agents, or using Bright Data through an agent tool layer instead of the local `bdata` CLI.
---

# Bright Data MCP Tools

Use the Bright Data MCP layer first when configured in the active agent environment and the task benefits from live search, batching, structured output, or MCP usage tracking.

## Workflow

1. Check available `mcp__brightdata` tools before falling back to `web.run`, `git clone`, serial scrapes, or shell loops.
2. Read `references/bright-data-mcp.md` for MCP-first routing, current tool choice, output checks, and fallback rules.
3. Read `references/bright-data-mcp-mcp-tools.md` when choosing `discover`, `search_engine_batch`, `scrape_batch`, `extract`, or `session_stats`.
4. Read `references/bright-data-mcp-mcp-setup.md` when installing/configuring the Bright Data MCP server or connecting it to an agent.
5. Prefer `bdata` child skills when MCP is unavailable, unconfigured, or weaker for reproducible shell/file workflows.
6. For material skill updates involving MCP routing, run a small live MCP validation matrix and store results in an artifact before finalizing guidance.

## Boundaries

- Do not invent MCP tools or assume the server is installed.
- Do not route to broad platform-data workflows (feeds, pipelines, marketplace datasets) in this local skill; narrow `web_data_*` readers are out of v1 routing.
- Do not claim `extract` success unless JSON fields are present and the sampling path is supported.
- Keep credentials in MCP/env config, not in prompts, code, logs, or final answers.
