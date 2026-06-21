---
name: brightdata-cli
description: >
  Use Bright Data CLI (`bdata`) command guidance. Trigger on `bdata` command syntax, CLI help, config, zones, budget, account/status checks, command flags, output formats, local CLI troubleshooting after auth, or choosing the right CLI command outside search/scrape-specific workflows.
---

# Bright Data CLI

Operate the Bright Data CLI as the shared command layer for local Bright Data workflows.

## Workflow

1. Read `references/brightdata-cli.md` for CLI overview, command families, auth assumptions, and safe usage rules.
2. Read `references/brightdata-cli-commands.md` for command syntax, options, zones, budget, config, status, and examples.
3. If auth/install is missing, switch to `../brightdata-setup/SKILL.md` before live calls.
4. For task-specific collection, prefer the dedicated skill:
   - Search/Discover: `../brightdata-web-search/SKILL.md`
   - Scrape known URLs: `../brightdata-web-scrape/SKILL.md`
   - MCP tool layer: `../brightdata-mcp-tools/SKILL.md`
5. Report exact commands run and relevant output; redact tokens, API keys, session IDs, cookies, and credentials.

## Boundaries

- Do not duplicate task-specific flag tables in the answer; load the relevant reference only when needed.
- Do not use deprecated platform-data, feeds, pipelines, SDK, proxy, or custom-scraper workflows from upstream.
- Do not assume live command success; check local CLI/auth state or state the blocker.
