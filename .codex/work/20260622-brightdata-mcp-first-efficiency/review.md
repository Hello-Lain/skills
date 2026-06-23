# Review: Bright Data MCP-first efficiency

- Artifact Type: material skill update
- Confidence: High
- Review Mode: heavy
- Review Route: inline
- Verdict: PASS

## Review Basis
- Goal: Update Bright Data skills so future agents use currently available MCP tools first when they improve speed, reliability, or structured output quality.
- Artifact: `brightdata/` skill diff plus `.codex/work/20260622-brightdata-mcp-first-efficiency/` evidence artifacts.
- Sources: `.codex/work/20260622-brightdata-mcp-first-efficiency/spec.md`, `.codex/work/20260622-brightdata-mcp-first-efficiency/plan.md`, `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`, `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md`, `brightdata/SKILL.md`, `brightdata/skills/brightdata-mcp-tools/SKILL.md`, `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`, `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`, `brightdata/skills/brightdata-web-search/SKILL.md`, `brightdata/skills/brightdata-web-scrape/SKILL.md`, `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`.
- Constraints: no credential/config changes; no new MCP tools; preserve unrelated dirty work; live MCP validation required; material skill production gate required.
- Validators: `python3 reviewer/scripts/validate_review_report.py --self-test`: PASS; `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`: PASS; `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260622-brightdata-mcp-first-efficiency --stage draft --require-production-report --require-final-report`: PASS; `git diff --check -- <scoped Bright Data files>`: PASS.
- Cleanup: not launched; inline route used because current tool policy does not authorize spawning subagents unless the user explicitly requests sub-agent delegation.

## Rubric
- Source alignment: changed guidance must match confirmed spec scope and explicit exclusions.
- Evidence: live MCP matrix must exist and inform guidance, including failures and fallbacks.
- Safety: no secrets, tokens, CP config, or credential instructions may be added.
- Scope control: only scoped Bright Data skill files and workspace artifacts should be modified for this feature.
- Production readiness: material skill update must have draft production gate evidence and validators.
- Usability: future agents must see clear MCP-first route, output checks, and fallback rules without bloating always-loaded files.

## Mode Decision
- Route: heavy
- Reason: material workflow update that changes skill routing and validation expectations.
- Packet: confirmed spec, plan, MCP validation artifact, production report, scoped diff, and relevant skill/reviewer contracts.
- Raw transcript handling: omitted; summarized in artifacts.

## Alignment Result
- Result: PASS
- Reason: The diff implements MCP-first routing for discovery, batch scraping, extraction, narrow readers, and session stats while preserving CLI fallback and explicit v1 exclusions.

## Quality Result
- Result: PASS
- Reason: Live MCP validation evidence supports the guidance and documents two important failure modes: `extract` sampling support and inactive GitHub reader access.

## Findings
Findings: None

## Recheck Plan
- Re-run production gate final validation after this review is consumed.
- Re-run `python3 plan2do/scripts/validate_execution.py .codex/work/20260622-brightdata-mcp-first-efficiency` after final artifacts and task statuses are complete.
- Inspect future MCP reliability if `extract` sampling or account activation changes.

## Residual Risks
- `extract` failed in this session because MCP sampling support was unavailable; guidance includes fallback but does not make extraction reliable.
- `web_data_github_repository_file` failed with `Customer is not active`; guidance includes fallback but cannot activate the account.
- Existing unrelated Bright Data reference edits remain in the worktree and were intentionally preserved.
