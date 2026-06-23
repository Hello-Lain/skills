# Context Wave 1

- Goal: implement `.codex/work/20260622-brightdata-mcp-routing-hardening/spec.md`.
- Mode: lite, wave-pack required by `context_gate.py --phase implement --plan-tasks 5`.
- Authoritative sources: confirmed spec, debug report, Bright Data local skill files, `skill-tokenless/references/skill-production-gate.md`, `spec2plan/references/plan-contract.md`, `plan2do/references/execution-contract.md`.
- Constraints: no Pro/platform data, no browser automation, no upstream 60+ catalog import, no auto MCP config/account edits, v1 does not require `extract` to work.
- Pre-existing dirty scope: `brightdata/` has prior edits from earlier MCP-first work; preserve unrelated setup/reference changes unless touched by this implementation.
- Planned edits: parent router, MCP child/ref docs, search/scrape child routing text, optional research/RAG reference guidance, artifacts.
- Verification: quick validators, plan validator, execution validator, production gate draft/final, real MCP smoke, reviewer PASS.
