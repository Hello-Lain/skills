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
- Auth errors: regenerate token from the Bright Data dashboard.
