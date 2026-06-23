# Skill Production Report

- Skill: brightdata
- Change Type: material-update
- Verdict: PASS

## Behavior Lock
- Preserved: Bright Data parent router, setup/CLI/search/scrape/MCP child routes, credential redaction, setup blockers, removed-scope exclusions, and CLI fallback for reproducible shell workflows.
- Changed intentionally: MCP guidance is now MCP-first for current available tools when they improve search, relevance discovery, batch scraping, extraction, narrow readers, or usage tracking.
- Fallbacks: fall back to CLI/web/repo tools when MCP is unavailable, unconfigured, blocked by account activation, lacks sampling support, returns empty content, returns block pages, returns malformed JSON, or is weaker for local files/history/tests.

## Token Budget
- Before: `brightdata/SKILL.md` 32 lines; `brightdata-mcp-tools/SKILL.md` 23 lines; `bright-data-mcp.md` 55 lines; `bright-data-mcp-mcp-tools.md` 38 lines; `brightdata-web-search/SKILL.md` 32 lines; `brightdata-web-scrape/SKILL.md` 27 lines.
- After: `brightdata/SKILL.md` 33 lines; `brightdata-mcp-tools/SKILL.md` 26 lines; `bright-data-mcp.md` 71 lines; `bright-data-mcp-mcp-tools.md` 51 lines; `brightdata-web-search/SKILL.md` 33 lines; `brightdata-web-scrape/SKILL.md` 28 lines.
- Moved to references: Detailed tool matrix, validation matrix, output checks, and fallback rules remain in `brightdata/skills/brightdata-mcp-tools/references/`.

## Deterministic Validators
- `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260622-brightdata-mcp-first-efficiency/plan.md --mode light`: PASS
- `python3 plan2do/scripts/compile_execution.py .codex/work/20260622-brightdata-mcp-first-efficiency/plan.md`: PASS
- `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`: PASS
- `python3 .system/skill-creator/scripts/quick_validate.py brightdata`: PASS
- `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-mcp-tools`: PASS
- `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-web-search`: PASS
- `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-web-scrape`: PASS
- `grep -R "MCP-first\|session_stats\|web_data_github_repository_file\|scrape_batch\|fallback" ...`: PASS

## Scenario Gate
- Scenario: Future agent needs live source discovery, batch page reads, structured one-page extraction, GitHub single-file read, or MCP usage tracking.
- RED/control: Prior local MCP skill explicitly kept a minimal search/scrape/extract scope and parent router preferred CLI for local workflows, causing underuse of exposed MCP tools.
- GREEN/retest: Live MCP validation showed `discover`, `search_engine_batch`, `scrape_batch`, and `session_stats` work; failures in `extract` and `web_data_github_repository_file` produced explicit sampling/account blockers that are now documented fallback triggers.
- Cleanup: not launched; no temp fixtures or subagents created for scenario testing.

## Reviewer Gate
- Mode: heavy
- Route: inline
- Verdict: PASS
- Report: `.codex/work/20260622-brightdata-mcp-first-efficiency/review.md`
- Cleanup: not launched

## Reuse Attribution
| Source | URL | Borrowed idea | Component | Adoption | Target change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- |
| pre-commit | https://github.com/pre-commit/pre-commit | deterministic hook-style gates | validator pattern | pattern-only | production gate and grep/validation checks | no runtime dependency needed |
| Plandex | https://github.com/plandex-ai/plandex | inspect pending diffs before accepting generated edits | diff review discipline | pattern-only | focused diff and scoped writable paths | no generated diff engine needed |
| Aider | https://github.com/Aider-AI/aider | repo-aware edit/test feedback loop | edit/test loop | pattern-only | patch then run targeted validators | no dependency added |
| Hermes Agent Self-Evolution | https://github.com/NousResearch/hermes-agent-self-evolution | evidence, constraints, promotion gates | audit pattern | pattern-only | debug-skill final audit and production evidence | no private history or GEPA dependency |

## Changed Files
- `brightdata/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`
- `brightdata/skills/brightdata-web-search/SKILL.md`
- `brightdata/skills/brightdata-web-scrape/SKILL.md`
- `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`
- `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/task2-skill-edits.md`
- `.codex/work/20260622-brightdata-mcp-first-efficiency/plan.md`
- `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/context-wave-pack.md`

## Residual Risks
- `extract` depends on MCP sampling support and failed in this session.
- `web_data_github_repository_file` returned `Customer is not active` in this session.
- Existing unrelated Bright Data reference edits remain in the working tree and were preserved.
- Reviewer subagent isolation was not used because current tool policy did not authorize spawning subagents without an explicit delegation request.
