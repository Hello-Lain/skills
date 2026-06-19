# Codex Integration

## MCP Config

Preferred Codex config in `/data/lcq/.codex/config.toml`:

```toml
[mcp_servers.codegraph]
command = "codegraph"
args = ["serve", "--mcp"]
```

No-global fallback:

```toml
[mcp_servers.codegraph]
command = "npx"
args = ["--yes", "@colbymchenry/codegraph", "serve", "--mcp"]
```

Restart Codex after config changes. The current session may not expose new MCP tools.

## Install / Verify

```bash
npm install -g @colbymchenry/codegraph
codegraph version
codegraph serve --help
```

Fallback:

```bash
npx --yes @colbymchenry/codegraph version
```

## MCP vs CLI

- Use MCP tools when present in the current tool list, especially `codegraph_explore` and `codegraph_node`.
- Use CLI for deterministic scripts, smoke tests, or when MCP did not load yet.
- If MCP fails at startup, verify PATH, then try the `npx` fallback config.

## Troubleshooting

- Stale lock: run `codegraph unlock <repo>`.
- Stale graph: run `codegraph sync <repo>`; if still wrong, run `codegraph index <repo>`.
- Slow filesystem: run MCP with `args = ["serve", "--mcp", "--no-watch"]`.
- Accidental index: remove `.codegraph/` only after confirming the repo does not need it.
