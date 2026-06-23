# Skill Production Report

- Skill: `brightdata`
- Change Type: material-update
- Verdict: PASS

## Behavior Lock

- Preserved: Bright Data parent router, setup/CLI/search/scrape child routing, credential hygiene, command/file citation requirements, and fallback recording.
- Changed intentionally: MCP-first precedence is now unambiguous; deferred tool discovery is explicit; current reliable MCP tools are promoted; `extract` is conditional; narrow `web_data_*` readers are removed from v1 routing; research/RAG Discover guidance is reference-only.
- Fallbacks: CLI for reproducible shell/file workflows; scrape markdown/html plus local schema parsing when `extract` sampling fails; setup reference when MCP is not configured.

## Token Budget

- Before: parent and child files were already compact; detailed behavior lived in references.
- After: parent remains lean; new research/RAG detail moved to `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-research-rag.md`.
- Moved to references: lightweight Discover research/RAG workflow, runtime checklist, and material validation details.

## Deterministic Validators

- `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260622-brightdata-mcp-routing-hardening/plan.md --mode light`: PASS.
- `python3 .system/skill-creator/scripts/quick_validate.py brightdata`: PASS.
- `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-mcp-tools`: PASS.
- `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-web-search`: PASS.
- `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-web-scrape`: PASS.

## Scenario Gate

- Scenario: agent needs live Bright Data MCP search, batch search, scrape, structured extraction, and research/RAG discovery.
- RED/control: prior parent route said “MCP only when needed”, prior refs promoted narrow readers and did not split runtime checks from material validation.
- GREEN/retest: parent route is MCP-first per phase; refs include deferred discovery, runtime checklist, conditional `extract`, no v1 narrow reader routing, and research/RAG reference guidance.
- Cleanup: no temp fixtures created; raw MCP output summarized in `artifacts/mcp-smoke.md`.

## Reviewer Gate

- Mode: lite.
- Route: inline.
- Verdict: PASS
- Report: `.codex/work/20260622-brightdata-mcp-routing-hardening/review-implementation.md`.
- Cleanup: not launched.

## Reuse Attribution

| Source | URL | Borrowed idea | Component | Adoption | Target change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- |
| Bright Data MCP docs | `https://docs.brightdata.com/ai/mcp-server/tools` | current MCP tool classes and groups | documentation | adapted | tool reference and validation wording | did not copy broad 60+ catalog |
| Bright Data skills repo | `https://github.com/brightdata/skills` | MCP-first routing and research/RAG patterns | markdown skills | adapted | research/RAG reference and MCP-first route | rejected no-exceptions policy and auto config mutation |
| pre-commit | `https://github.com/pre-commit/pre-commit` | deterministic gate pattern | validation workflow | pattern-only | quick validators and production gate | no dependency needed |
| Hermes Agent Self-Evolution | `https://github.com/NousResearch/hermes-agent-self-evolution` | promotion gates with evidence | audit pattern | pattern-only | material skill-update report | no private history mining |

## Changed Files

- `brightdata/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-research-rag.md`
- `brightdata/skills/brightdata-web-search/SKILL.md`
- `brightdata/skills/brightdata-web-scrape/SKILL.md`

## Residual Risks

- `extract` still fails with `MCP error -32601: sampling/createMessage` in this environment and remains a required follow-up.
