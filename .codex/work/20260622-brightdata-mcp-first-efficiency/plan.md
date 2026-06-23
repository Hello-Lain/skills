# Bright Data MCP-first Efficiency Plan

Mode: light
Risk level: Medium
Confidence: High

## Goal
Update the local Bright Data skill group so future Codex/agent sessions use currently available Bright Data MCP tools first for discovery, batch scraping, structured extraction, GitHub single-file reads, and usage tracking when those tools improve speed, reliability, or output structure.

## Non-Goals
- Do not enable, install, or configure new MCP tools.
- Do not modify Bright Data credentials, CP settings, tokens, zones, or environment secrets.
- Do not restore full `web_data_*` platform-data skills, Browser automation, dataset search, GEO, Code, Pro groups, or CP configuration docs in v1.
- Do not replace CLI workflows that require reproducible saved files, local shell pipelines, repository history, tests, or broad multi-file repository operations.
- Do not revert unrelated dirty work already present in the Bright Data skill tree.

## Evidence Inspected
- `.codex/work/20260622-brightdata-mcp-first-efficiency/spec.md`
- `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/context-wave-pack.md`
- `brightdata/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-setup.md`
- `brightdata/skills/brightdata-web-search/SKILL.md`
- `brightdata/skills/brightdata-web-scrape/SKILL.md`
- `brightdata/skills/brightdata-web-search/references/search.md`
- `brightdata/skills/brightdata-web-search/references/discover-api.md`
- `brightdata/skills/brightdata-web-scrape/references/scrape.md`
- `spec2plan/SKILL.md`
- `spec2plan/references/plan-contract.md`
- `plan2do/SKILL.md`
- `plan2do/references/execution-contract.md`
- `skill-tokenless/SKILL.md`
- `skill-tokenless/references/testing.md`
- `skill-tokenless/references/validation.md`
- `skill-tokenless/references/skill-production-gate.md`
- `reviewer/SKILL.md`
- `debug-skill/SKILL.md`
- `edit-orchestration/SKILL.md`
- `context-engineering/SKILL.md`

## Spec Summary
The confirmed spec requires MCP-first Bright Data guidance for currently exposed tools, live validation with about 10-15 public low-risk MCP calls, bounded artifacts, explicit fallback rules, and no new MCP setup or Pro/platform skill restoration.

## Domain Language Check
- Use `MCP-first` for guidance that prefers available `mcp__brightdata` tools before `web.run`, `git clone`, or serial shell loops.
- Use `fallback` for safe routing when MCP output is empty, blocked, malformed, stale, irrelevant, unavailable, or less reproducible.
- Use `validation matrix` for the required live MCP evidence artifact.
- No term conflicts found in inspected Bright Data skill files.

## Current Context
- Workspace: `.codex/work/20260622-brightdata-mcp-first-efficiency/`.
- Existing unrelated dirty edits are present in several Bright Data reference files; preserve them and patch current content only.
- Current session exposes these Bright Data MCP tools: `discover`, `search_engine`, `search_engine_batch`, `scrape_as_markdown`, `scrape_as_html`, `scrape_batch`, `extract`, `web_data_github_repository_file`, `web_data_reuter_news`, and `session_stats`.
- CodeGraph was considered; this is docs-only skill work, so targeted reads and diffs are sufficient.

## Implementation Map
- Files:
  - `brightdata/SKILL.md`: add MCP-first routing rule while preserving CLI preference when MCP is unavailable or less reproducible.
  - `brightdata/skills/brightdata-mcp-tools/SKILL.md`: make workflow load MCP-first references and require live validation evidence for material updates.
  - `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`: expand scope and decision tree for current MCP tools and fallbacks.
  - `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`: replace minimal table with current tool reference, output checks, validation matrix, and fallback rules.
  - `brightdata/skills/brightdata-web-search/SKILL.md`: add MCP redirect when Bright Data MCP tools are available and fit the task.
  - `brightdata/skills/brightdata-web-scrape/SKILL.md`: add MCP redirect when known-URL scraping or extraction benefits from MCP.
  - `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`: record live MCP call results.
  - `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md`: Skill Production Gate evidence.
  - `.codex/work/20260622-brightdata-mcp-first-efficiency/review.md`: final reviewer report.
  - `.codex/work/20260622-brightdata-mcp-first-efficiency/review-debug-skill.md`: debug-skill audit.
  - `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/final-report.md`: plan2do completion report.
- Symbols / APIs: `mcp__brightdata.discover`, `mcp__brightdata.search_engine_batch`, `mcp__brightdata.scrape_batch`, `mcp__brightdata.extract`, `mcp__brightdata.web_data_github_repository_file`, `mcp__brightdata.session_stats`, `validate_skill_production.py`, `validate_review_report.py`, `validate_execution.py`.
- Tests: documentation and skill gates only; no code unit tests exist for these markdown skills.
- Commands:
  - `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260622-brightdata-mcp-first-efficiency/plan.md --mode light`
  - `python3 plan2do/scripts/compile_execution.py .codex/work/20260622-brightdata-mcp-first-efficiency/plan.md`
  - `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
  - `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260622-brightdata-mcp-first-efficiency --stage draft --require-production-report --require-final-report`
  - `python3 reviewer/scripts/validate_review_report.py .codex/work/20260622-brightdata-mcp-first-efficiency/review.md`
  - `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`
  - `python3 plan2do/scripts/validate_execution.py .codex/work/20260622-brightdata-mcp-first-efficiency`
- Data / migration impact: Not applicable; local markdown skill guidance and artifacts only.

## Assumptions
- The current MCP registry is representative enough to validate the v1 current-tool guidance.
- Public stable URLs can validate reliability without credentialed access.
- Existing unrelated dirty edits are intentional user work and must remain.

## User Inputs Needed
None.

## Proposed Approach
Plan and execute in five vertical slices: live MCP validation, targeted skill edits, production gate report, independent review, and debug-skill audit with final execution validation.

## Scenario Probes
- A research task with multiple queries should route to `discover` or `search_engine_batch` instead of serial `web.run`.
- A known list of 2-5 public URLs should route to `scrape_batch` instead of repeated single scrapes.
- A one-page field extraction should route to `extract` with a schema prompt instead of manual parsing.
- A GitHub single-file read should route to `web_data_github_repository_file` instead of cloning the repo.
- Empty or blocked MCP output should trigger fallback guidance rather than success claims.

## Dependency Graph
- Task 1 validates available MCP tools and writes evidence.
- Task 2 edits skill guidance using Task 1 evidence.
- Task 3 writes production report and runs draft gates after Task 2.
- Task 4 performs final reviewer gate after Task 3.
- Task 5 performs debug-skill audit and final execution validation after Task 4.

## Task Breakdown
### Task 1: Validate current MCP tools

- Description: Run the live MCP validation matrix against public low-risk targets and write `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`.
- Worker role: coding
- Wave: 1
- Acceptance criteria: Validation artifact records `session_stats` before and after, `discover`, `search_engine_batch`, `scrape_batch`, `extract`, `web_data_github_repository_file`, success checks, failures, fallback decisions, and one observed efficiency or stability signal.
- Verification: Manual check `test -s .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md && grep -E "discover|search_engine_batch|scrape_batch|extract|web_data_github_repository_file|session_stats" .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`.
- Concrete edits: Create only the validation artifact from real MCP outputs.
- Interfaces / contracts changed: None.
- Test cases: Public query, two-query batch search, two or three URL batch scrape, one JSON extraction, one GitHub blob file read, usage stats before and after.
- Pre-check commands: `git status --short`.
- Post-check commands: `test -s .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md && grep -E "fallback|efficiency|stability" .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`.
- Dependencies: None.
- Files likely touched: `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`.
- Writable scope: `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`.
- Output artifact: `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`.
- Estimated scope: S

### Task 2: Patch Bright Data MCP-first guidance

- Description: Update scoped Bright Data skill files with MCP-first routing, current tool choice, output checks, and fallback boundaries grounded in Task 1 evidence.
- Worker role: coding
- Wave: 2
- Acceptance criteria: Scoped files mention current MCP-first routing, tool choice, output checks, fallback rules, validation matrix, v1 exclusions, and search/scrape child redirects without removing unrelated existing guidance.
- Verification: Manual grep `grep -R "MCP-first\\|session_stats\\|web_data_github_repository_file\\|scrape_batch\\|fallback" brightdata/SKILL.md brightdata/skills/brightdata-mcp-tools brightdata/skills/brightdata-web-search/SKILL.md brightdata/skills/brightdata-web-scrape/SKILL.md`.
- Concrete edits: Patch `brightdata/SKILL.md`, `brightdata/skills/brightdata-mcp-tools/SKILL.md`, `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`, `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`, `brightdata/skills/brightdata-web-search/SKILL.md`, and `brightdata/skills/brightdata-web-scrape/SKILL.md`.
- Interfaces / contracts changed: Bright Data skill routing contract changes from MCP-minimal to MCP-first when tools are available and useful.
- Test cases: Readability check of child route flow, fallback check for empty MCP output, exclusion check for Pro/platform/browser/dataset skills.
- Pre-check commands: `git diff -- brightdata/SKILL.md brightdata/skills/brightdata-mcp-tools/SKILL.md brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md brightdata/skills/brightdata-web-search/SKILL.md brightdata/skills/brightdata-web-scrape/SKILL.md`.
- Post-check commands: `grep -R "MCP-first\\|session_stats\\|web_data_github_repository_file\\|scrape_batch\\|fallback" brightdata/SKILL.md brightdata/skills/brightdata-mcp-tools brightdata/skills/brightdata-web-search/SKILL.md brightdata/skills/brightdata-web-scrape/SKILL.md`.
- Dependencies: Task 1.
- Files likely touched: `brightdata/SKILL.md`, `brightdata/skills/brightdata-mcp-tools/SKILL.md`, `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`, `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`, `brightdata/skills/brightdata-web-search/SKILL.md`, `brightdata/skills/brightdata-web-scrape/SKILL.md`.
- Writable scope: `brightdata/SKILL.md`; `brightdata/skills/brightdata-mcp-tools/SKILL.md`; `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`; `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`; `brightdata/skills/brightdata-web-search/SKILL.md`; `brightdata/skills/brightdata-web-scrape/SKILL.md`.
- Output artifact: `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/task2-skill-edits.md`.
- Estimated scope: M

### Task 3: Run Skill Production Gate draft

- Description: Write and validate `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md` for the material Bright Data skill workflow update.
- Worker role: coding
- Wave: 3
- Acceptance criteria: Production report cites behavior lock, RED evidence from prior underuse, GREEN evidence from live MCP validation and grep checks, changed files, preserved gates, risks, reviewer status, and draft validator pass.
- Verification: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`.
- Concrete edits: Create production report and update execution task state for completed non-review tasks.
- Interfaces / contracts changed: None beyond Task 2 documentation already changed.
- Test cases: Draft production report validator and pre-review readiness check.
- Pre-check commands: `test -s .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`.
- Post-check commands: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft && python3 plan2do/scripts/pre_review_ready.py .codex/work/20260622-brightdata-mcp-first-efficiency --stage draft --require-production-report --require-final-report`.
- Dependencies: Task 2.
- Files likely touched: `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md`, `.codex/work/20260622-brightdata-mcp-first-efficiency/execution/tasks.json`.
- Writable scope: `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md`; `.codex/work/20260622-brightdata-mcp-first-efficiency/execution/tasks.json`.
- Output artifact: `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md`.
- Estimated scope: S

### Task 4: Run final reviewer gate

- Description: Perform reviewer gate on the skill update, write `.codex/work/20260622-brightdata-mcp-first-efficiency/review.md`, and consume PASS, REVISE, or BLOCK.
- Worker role: review
- Wave: 4
- Acceptance criteria: Review report follows reviewer v2 template, validates with `validate_review_report.py`, and contains top-level `Verdict: PASS` before final completion.
- Verification: `python3 reviewer/scripts/validate_review_report.py .codex/work/20260622-brightdata-mcp-first-efficiency/review.md`.
- Concrete edits: Create review report; if reviewer returns REVISE, apply bounded rework inside Task 2 writable scope and rerun affected gates.
- Interfaces / contracts changed: None.
- Test cases: Reviewer checks source alignment, MCP validation evidence, skill-tokenless gate evidence, scoped diff, fallback coverage, and exclusion coverage.
- Pre-check commands: `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260622-brightdata-mcp-first-efficiency --stage draft --require-production-report --require-final-report`.
- Post-check commands: `python3 reviewer/scripts/validate_review_report.py .codex/work/20260622-brightdata-mcp-first-efficiency/review.md && grep -q "Verdict: PASS" .codex/work/20260622-brightdata-mcp-first-efficiency/review.md`.
- Dependencies: Task 3.
- Files likely touched: `.codex/work/20260622-brightdata-mcp-first-efficiency/review.md`.
- Writable scope: `.codex/work/20260622-brightdata-mcp-first-efficiency/review.md`.
- Output artifact: `.codex/work/20260622-brightdata-mcp-first-efficiency/review.md`.
- Estimated scope: S

### Task 5: Run debug-skill audit and final validation

- Description: Audit whether the used skills helped or hurt this execution, update final production gate status, validate execution, and write final report.
- Worker role: review
- Wave: 5
- Acceptance criteria: Debug-skill review names evidence, workflow compliance incidents if any, user-visible impact, suggested skill fixes, final production gate passes, execution validator passes, and final report states `Status: COMPLETE`.
- Verification: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final && python3 plan2do/scripts/validate_execution.py .codex/work/20260622-brightdata-mcp-first-efficiency`.
- Concrete edits: Create debug-skill review report, update production report reviewer status, mark task statuses complete, and write final report.
- Interfaces / contracts changed: None.
- Test cases: Final production report validation, execution validation, final artifact existence checks.
- Pre-check commands: `grep -q "Verdict: PASS" .codex/work/20260622-brightdata-mcp-first-efficiency/review.md`.
- Post-check commands: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final && python3 plan2do/scripts/validate_execution.py .codex/work/20260622-brightdata-mcp-first-efficiency`.
- Dependencies: Task 4.
- Files likely touched: `.codex/work/20260622-brightdata-mcp-first-efficiency/review-debug-skill.md`, `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md`, `.codex/work/20260622-brightdata-mcp-first-efficiency/execution/tasks.json`, `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/final-report.md`.
- Writable scope: `.codex/work/20260622-brightdata-mcp-first-efficiency/review-debug-skill.md`; `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md`; `.codex/work/20260622-brightdata-mcp-first-efficiency/execution/tasks.json`; `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/final-report.md`.
- Output artifact: `.codex/work/20260622-brightdata-mcp-first-efficiency/review-debug-skill.md`.
- Estimated scope: S

## Step-by-Step Plan
1. Run `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260622-brightdata-mcp-first-efficiency/plan.md --mode light`.
2. Run `python3 plan2do/scripts/compile_execution.py .codex/work/20260622-brightdata-mcp-first-efficiency/plan.md`.
3. Call `mcp__brightdata.session_stats` and record the output in `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`.
4. Call `mcp__brightdata.discover` for one public Bright Data MCP docs query and record relevance/output checks.
5. Call `mcp__brightdata.search_engine_batch` for two independent public queries and record batch efficiency.
6. Call `mcp__brightdata.scrape_batch` for two stable public URLs and record content checks.
7. Call `mcp__brightdata.extract` on one stable public page with a schema prompt and record field checks.
8. Call `mcp__brightdata.web_data_github_repository_file` for a public GitHub blob URL and record structured read checks.
9. Call `mcp__brightdata.session_stats` again and record usage delta.
10. Patch `brightdata/SKILL.md` with the MCP-first routing rule.
11. Patch `brightdata/skills/brightdata-mcp-tools/SKILL.md` with workflow and validation gates.
12. Patch `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md` with the decision tree and fallbacks.
13. Patch `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md` with current tool table and validation matrix.
14. Patch `brightdata/skills/brightdata-web-search/SKILL.md` and `brightdata/skills/brightdata-web-scrape/SKILL.md` with MCP redirect guidance.
15. Run the Task 2 grep check and write `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/task2-skill-edits.md`.
16. Write `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md`.
17. Run `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`.
18. Run `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260622-brightdata-mcp-first-efficiency --stage draft --require-production-report --require-final-report`.
19. Write `.codex/work/20260622-brightdata-mcp-first-efficiency/review.md` using reviewer evidence, then run `python3 reviewer/scripts/validate_review_report.py .codex/work/20260622-brightdata-mcp-first-efficiency/review.md`.
20. Write `.codex/work/20260622-brightdata-mcp-first-efficiency/review-debug-skill.md` using debug-skill evidence.
21. Update `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md` to final reviewer status and run final production validator.
22. Mark `.codex/work/20260622-brightdata-mcp-first-efficiency/execution/tasks.json` tasks complete.
23. Write `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/final-report.md` with `Status: COMPLETE`.
24. Run `python3 plan2do/scripts/validate_execution.py .codex/work/20260622-brightdata-mcp-first-efficiency`.

## Parallelization
- Task 1 must run first because it supplies evidence.
- Task 2 depends on Task 1 and writes the skill files.
- Task 3 depends on Task 2.
- Task 4 depends on Task 3.
- Task 5 depends on Task 4.
- No same-wave writable scopes overlap.

## Files / Components Likely Affected
- `brightdata/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`
- `brightdata/skills/brightdata-web-search/SKILL.md`
- `brightdata/skills/brightdata-web-scrape/SKILL.md`
- `.codex/work/20260622-brightdata-mcp-first-efficiency/`

## Owners / Responsibilities
- Main agent: run MCP validation, patch skill docs, run production gates, write artifacts, preserve unrelated dirty work.
- Reviewer: independently review source alignment, validation evidence, fallback coverage, and scope control.
- User: no input required unless validation or review returns `BLOCK`.

## Validation Plan
- MCP validation matrix proves live tool reliability and efficiency signals.
- Grep checks prove new routing language exists.
- Skill Production Gate draft and final validators prove material skill update gate compliance.
- Reviewer report validator proves review artifact shape.
- Execution validator proves task artifacts, final report, review PASS, and verification evidence exist.

## Rollout Plan
- Local rollout only in `/data/lcq/.codex/skills`.
- Updated skills affect future agent behavior after files are saved.
- No remote release, plugin install, or MCP config change.

## Monitoring / Observability
- `session_stats` records MCP usage before and after validation.
- `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md` records per-tool reliability and fallback decisions.
- `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/production-report.md` records skill update gate evidence.
- `git status --short` and focused diffs monitor unintended file changes.

## Documentation / ADR Updates
ADR: Not needed. The authoritative docs are the updated Bright Data skill files and workspace artifacts.

## Rollback / Recovery Plan
- If an MCP call fails, record the failure and fallback decision in `mcp-validation.md`; do not silently remove the tool from guidance.
- If a patch conflicts with unrelated dirty work, stop and re-read the exact file before retrying.
- If a validator fails, patch the smallest artifact or skill text needed and rerun once.
- If reviewer returns `REVISE`, write rework guidance, fix within Task 2 writable scope, rerun affected gates, and revalidate review.
- If reviewer returns `BLOCK`, stop and report the blocker.

## Abort Criteria
- Required live MCP validation cannot run at all.
- Production gate validator cannot pass after two focused repair cycles.
- Reviewer returns `BLOCK` with missing evidence that cannot be supplied locally.
- Required edits would overwrite unrelated user changes.
- Execution validator cannot pass after two focused repair cycles.

## Risks
- MCP calls may consume credits; mitigation is the fixed small validation matrix and `session_stats`.
- Some public pages may return empty or low-quality output; mitigation is fallback recording and stable low-risk targets.
- Skill guidance can become verbose; mitigation is short `SKILL.md` routing and detail in references.
- Existing dirty files may contain user work; mitigation is focused diff inspection and scoped patches.

## Open Questions
None.

## Plan Self-Review
- Writable scope is explicit and same-wave overlap is absent.
- Coverage includes live MCP validation, grep checks, production gate, reviewer gate, debug-skill audit, and execution validation.
- Unknowns are listed as assumptions or risks rather than hidden in tasks.
- Rollback and abort criteria identify concrete validators, review outcomes, and dirty-work conflicts.
- Task 1 can be executed by a fresh agent using the plan path, MCP tool names, and artifact path without raw transcript context.

## Execution Decision
- Decision: execute now with `plan2do` primary-agent mode because the user explicitly requested `spec2plan -> plan2do -> reviewer -> debug-skill` plus `skill-tokenless`, `context-engineering`, and `edit-orchestration`.
- Review: final reviewer gate and debug-skill audit are mandatory.
- Implementation mode: primary-agent.

## Execution Handoff
- Goal: Implement Bright Data MCP-first efficiency guidance with live MCP validation and skill production gates.
- Current state: Spec and plan saved under `.codex/work/20260622-brightdata-mcp-first-efficiency/`; context wave pack saved.
- Authoritative artifacts: `.codex/work/20260622-brightdata-mcp-first-efficiency/spec.md`, `.codex/work/20260622-brightdata-mcp-first-efficiency/plan.md`, `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/context-wave-pack.md`.
- Decisions: Use light planning, primary-agent execution, live MCP validation, material skill production gate, final reviewer report, and debug-skill audit.
- Verification: Run MCP matrix, grep checks, `validate_plan_contract.py`, `compile_execution.py`, `validate_skill_production.py`, `pre_review_ready.py`, `validate_review_report.py`, and `validate_execution.py`.
- Remaining risks: Existing unrelated dirty Bright Data reference edits; preserve current user work.
- Next action: Run plan validator, compile execution state, then execute Task 1 MCP validation.
- Suggested skills: `plan2do`, `edit-orchestration`, `skill-tokenless`, `reviewer`, `debug-skill`, `context-engineering`.
- Redactions / omitted raw data: Raw MCP outputs summarized in artifacts; secrets and credentials must remain omitted.
