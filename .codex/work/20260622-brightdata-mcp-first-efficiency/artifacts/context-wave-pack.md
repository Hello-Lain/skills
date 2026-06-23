# Context Wave Pack: Bright Data MCP-first efficiency

## Goal
Implement `.codex/work/20260622-brightdata-mcp-first-efficiency/spec.md` by updating local Bright Data skill guidance to prefer currently available MCP tools when they improve speed, reliability, or structure.

## Mode
- Context state: focused, decision-critical for skill workflow updates.
- Context gate: `wave-pack`.
- Execution mode: primary-agent `plan2do`.

## Authoritative Sources
- `/data/lcq/.codex/AGENTS.md`
- `.codex/work/20260622-brightdata-mcp-first-efficiency/spec.md`
- `brightdata/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`
- `brightdata/skills/brightdata-web-search/SKILL.md`
- `brightdata/skills/brightdata-web-scrape/SKILL.md`
- `spec2plan/references/plan-contract.md`
- `plan2do/references/execution-contract.md`
- `skill-tokenless/references/skill-production-gate.md`

## Constraints
- Preserve unrelated dirty Bright Data reference edits.
- Do not change credentials, tokens, CP settings, zones, or MCP configuration.
- Do not restore Pro/platform/browser/dataset/GEO/Code skills in v1.
- Run real MCP validation with public low-risk targets before accepting implementation.
- Keep bulky logs in artifacts.

## Current Dirty Work
- Existing before this wave: `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`, `brightdata/skills/brightdata-setup/references/agent-onboarding.md`, `brightdata/skills/brightdata-setup/references/bright-data-best-practices-cli-setup.md`, `brightdata/skills/brightdata-web-scrape/references/scrape.md`, `brightdata/skills/brightdata-web-search/references/discover-api.md`, `brightdata/skills/brightdata-web-search/references/search.md`.
- Treat those edits as user work unless this plan intentionally extends the same file.

## Verification
- MCP validation matrix artifact.
- `validate_plan_contract.py`.
- `compile_execution.py`.
- `validate_skill_production.py` draft and final stages.
- `pre_review_ready.py`.
- `validate_review_report.py`.
- `validate_execution.py`.
