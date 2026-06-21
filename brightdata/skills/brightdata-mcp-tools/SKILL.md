---
name: brightdata-mcp-tools
description: >
  Use Bright Data MCP server/tool guidance. Trigger on Bright Data MCP setup, MCP web data tools, choosing between MCP search/scrape/extract tools, configuring the MCP server for Codex/agents, or using Bright Data through an agent tool layer instead of the local `bdata` CLI.
---

# Bright Data MCP Tools

Use the Bright Data MCP layer when it is configured in the active agent environment.

## Workflow

1. Read `references/bright-data-mcp.md` for the MCP overview, supported minimal web-data use, and CLI-vs-MCP choice.
2. Read `references/bright-data-mcp-mcp-setup.md` when installing/configuring the Bright Data MCP server or connecting it to an agent.
3. Read `references/bright-data-mcp-mcp-tools.md` when choosing MCP tools for search, scrape, extract, or browser-like retrieval.
4. Prefer `bdata` child skills when MCP is unavailable, unconfigured, or unnecessary for the task.
5. Before claiming MCP results, verify the corresponding MCP tool exists in the current tool list and cite the tool call/output actually used.

## Boundaries

- Do not invent MCP tools or assume the server is installed.
- Do not route to removed platform-data workflows (`web_data_*`, feeds, pipelines, marketplace datasets) in this local skill.
- Keep credentials in MCP/env config, not in prompts, code, logs, or final answers.
