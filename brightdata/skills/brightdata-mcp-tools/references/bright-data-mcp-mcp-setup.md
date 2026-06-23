# Bright Data MCP Setup

Use only when the user wants MCP or `mcp__brightdata__*` tools are already available.

## Remote MCP Server

```text
https://mcp.brightdata.com/mcp?token=<YOUR_BRIGHTDATA_API_TOKEN>
```

Minimal mode is enough for this local skill: search + scrape tools.

Claude Code example:

```json
{
  "mcpServers": {
    "brightdata": {
      "url": "https://mcp.brightdata.com/mcp?token=YOUR_TOKEN"
    }
  }
}
```

## Local MCP Server

```bash
npm install -g @brightdata/mcp
API_TOKEN=your_token npx @brightdata/mcp
```

## Local Extract Adapter

Use this Codex-local adapter when the MCP client lacks server-initiated sampling and `extract` fails with `sampling/createMessage`.

```toml
[mcp_servers.brightdata]
command = "node"
args = ["/data/lcq/.codex/skills/brightdata/adapters/brightdata-mcp-extract-adapter.mjs"]
```

The adapter proxies all Bright Data MCP traffic to upstream `@brightdata/mcp`, intercepts only `tools/call` for `extract`, scrapes via Bright Data `/request`, then calls the local OpenAI-compatible endpoint for JSON conversion. Keep `API_TOKEN` and `GROUPS` in the MCP env block.

## Verify

Ask for a simple Bright Data MCP search. The tool registry should expose at least:

- `mcp__brightdata__search_engine`
- `mcp__brightdata__scrape_as_markdown`

Optional but useful:

- `mcp__brightdata__scrape_as_html`
- `mcp__brightdata__scrape_batch`
- `mcp__brightdata__search_engine_batch`
- `mcp__brightdata__extract`

## Troubleshooting

- No tools: check token, MCP URL, network, and client reconnect.
- Search/scrape tool missing: reconnect the MCP server; avoid enabling Pro/platform groups unless the user explicitly asks.
- `extract` reports `sampling/createMessage`: switch to the local extract adapter, then restart Codex/MCP.
- Auth errors: regenerate token from the Bright Data dashboard.
