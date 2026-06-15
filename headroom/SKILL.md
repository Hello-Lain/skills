---
name: headroom
description: Use when configuring or using Headroom with Codex, Claude Code, Cursor, OpenAI-compatible proxies, MCP, token/context compression, tool-output compression, or when the user asks to wrap/unwrap Codex with Headroom or install Headroom on another machine.
---

# Headroom

Headroom compresses agent context, tool outputs, logs, files, RAG chunks, and proxy traffic before it reaches the model. For Codex, prefer this skill's stable launcher:

```bash
codex-headroom
```

Use this skill when the user wants Codex token/context compression, Headroom setup, proxy mode, MCP mode, or portable machine setup.

## Quick Setup

Run the bundled setup script from this skill:

```bash
~/.codex/skills/headroom/scripts/setup-headroom-codex.sh --yes
```

What it does:
- Installs or upgrades `headroom-ai[all]` using `pipx`, `uv tool`, or `python -m pip --user`.
- Verifies `headroom` is available.
- Runs `headroom wrap codex --prepare-only` so Codex config is prepared without launching an interactive Codex session.
- Creates `~/.local/bin/codex-headroom`, a stable launcher that runs `headroom wrap codex -- "$@"`.
- The launcher backs up `~/.codex/config.toml` before wrap and restores it after exit, so bare `codex` remains the fallback path.
- Leaves Headroom's own Codex config backup/restore behavior in charge.

For China/no-proxy environments:

```bash
~/.codex/skills/headroom/scripts/setup-headroom-codex.sh --yes --mirror tuna --no-proxy
```

## Daily Use

Start Codex through Headroom:

```bash
codex-headroom
```

Pass Codex args after `--`:

```bash
codex-headroom --model gpt-5
```

Show savings/stats when available:

```bash
headroom stats
```

Undo Codex integration:

```bash
headroom unwrap codex
```

Or via the setup script:

```bash
~/.codex/skills/headroom/scripts/setup-headroom-codex.sh --unwrap
```

## Portable Setup

After moving this `headroom/` skill directory to another machine, run:

```bash
~/.codex/skills/headroom/scripts/setup-headroom-codex.sh --yes --prepare-only
```

China/no-proxy:

```bash
~/.codex/skills/headroom/scripts/setup-headroom-codex.sh --yes --prepare-only --mirror tuna --no-proxy
```

Production expectation:
- `headroom` installed and on PATH.
- Codex Headroom integration prepared.
- `codex-headroom` launcher installed under `~/.local/bin`.
- Original `codex` remains untouched for fallback/debugging.

## Proxy Mode

Use proxy mode when configuring SDKs or OpenAI-compatible tools manually:

```bash
headroom proxy --port 8787
```

Then route OpenAI-compatible clients to:

```text
http://localhost:8787/v1
```

## Context Tool

`headroom wrap ...` uses RTK by default. To prefer `lean-ctx`:

```bash
HEADROOM_CONTEXT_TOOL=lean-ctx headroom wrap codex --prepare-only
```

Use `rtk` unless the user explicitly wants lean-ctx integration.

## Safety

- Do not overwrite a user's Codex config manually. Use `headroom wrap codex --prepare-only` or `headroom unwrap codex`.
- If Codex auth breaks after wrapping, run `headroom unwrap codex`, then retry setup with the latest Headroom.
- Avoid committing Headroom runtime caches, logs, or model/data artifacts.
