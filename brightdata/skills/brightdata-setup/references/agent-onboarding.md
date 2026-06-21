---
name: agent-onboarding
description: Minimal Bright Data onboarding for local live web-data work: install the Bright Data CLI, authenticate once, verify zones/budget, then route to CLI search/scrape or MCP.
---

# Bright Data — Minimal Agent Onboarding

Use this first when the agent or user has not yet configured Bright Data locally.

## Install

```bash
curl -fsSL https://cli.brightdata.com/install.sh | bash
# or
npm install -g @brightdata/cli
# or one-off
npx --yes --package @brightdata/cli brightdata <command>
```

Requires Node.js >= 20. Both `brightdata` and `bdata` should become available.

## Authenticate

```bash
bdata login
# headless / SSH
bdata login --device
# non-interactive
bdata login --api-key <key>
```

Do not paste API keys into prompts or final answers. Prefer local CLI auth.

## Verify

```bash
bdata version
bdata config
bdata zones
bdata budget
```

If verification fails, read `bright-data-best-practices-cli-setup.md`.

## Route

| Need | Reference |
| --- | --- |
| General CLI commands, config, budget, zones | `brightdata-cli.md` |
| Search Google/Bing/Yandex or Discover semantic results | `search.md`, `discover-api.md` |
| Scrape a known URL as markdown/HTML/JSON/screenshot | `scrape.md` |
| MCP tool/server setup or tool selection | `bright-data-mcp.md`, `bright-data-mcp-mcp-setup.md`, `bright-data-mcp-mcp-tools.md` |

## Default Flow

1. Search when URLs are unknown.
2. Scrape when the URL is known.
3. Use MCP when available and the user wants an agent tool layer rather than CLI commands.
