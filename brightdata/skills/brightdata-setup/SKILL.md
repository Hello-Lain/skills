---
name: brightdata-setup
description: >
  Set up and repair Bright Data CLI access. Use when installing or locating `bdata`, logging in with browser/device/API key, configuring zones, checking account/budget prerequisites, diagnosing auth/path errors, or preparing Bright Data before search, scrape, Discover, or MCP work.
---

# Bright Data Setup

Prepare local Bright Data access before live web-data calls.

## Workflow

1. Read `references/agent-onboarding.md` for first-time setup, auth path choice, and safe credential handling.
2. Read `references/bright-data-best-practices-cli-setup.md` when install/login/device auth, PATH, zone, budget, or environment troubleshooting is needed.
3. Prefer local CLI auth (`bdata login` or `bdata login --device`) over putting secrets in prompts or files.
4. Verify readiness with the smallest safe non-secret check, such as CLI version/status/help or a documented account/config command.
5. If setup is blocked, report the missing command, auth state, env var, zone, budget, network, or MCP config without exposing secrets.

## Boundaries

- Do not run paid or live collection commands just to prove setup unless the user requested it.
- Do not store API keys in repo files, shell history examples, logs, reports, or final answers.
- For generic `bdata` syntax after setup, use `../brightdata-cli/SKILL.md`.
- For search/scrape workflows, use the matching child skill after setup succeeds.
