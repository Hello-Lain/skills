# Bright Data MCP Routing Hardening Plan

Mode: light
Risk level: Medium
Confidence: High

## Goal

Implement the confirmed Bright Data MCP routing-hardening spec so agents prefer reliable current MCP tools, handle `extract` conditionally, avoid narrow `web_data_*` routing in v1, and gain lightweight Discover research/RAG guidance.

## Non-Goals

- Fixing `extract` sampling support.
- Enabling Pro/platform-data tools.
- Adding browser automation guidance.
- Importing the upstream 60+ MCP tool catalog.
- Auto-editing MCP client/server config, secrets, API tokens, account activation, or user account settings.

## Evidence Inspected

- `.codex/work/20260622-brightdata-mcp-routing-hardening/spec.md`
- `.codex/work/20260622-brightdata-debug-audit/debug-report.md`
- `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`
- `brightdata/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`
- `brightdata/skills/brightdata-web-search/SKILL.md`
- `brightdata/skills/brightdata-web-scrape/SKILL.md`
- `spec2plan/references/plan-contract.md`
- `plan2do/references/execution-contract.md`
- `skill-tokenless/references/skill-production-gate.md`

## Spec Summary

Use MCP-first for reliable current Bright Data MCP capabilities, explicitly discover deferred tools, treat `extract` as conditional on sampling smoke success, remove narrow `web_data_*` from v1 normal routing, split runtime checks from material validation, and add lightweight research/RAG Discover guidance in references.

## Domain Language Check

- Use `Bright Data MCP`, `discover`, `search_engine`, `search_engine_batch`, `scrape_as_markdown`, `scrape_as_html`, `scrape_batch`, `session_stats`, and conditional `extract`.
- Use `structured extraction fallback` for scrape plus local schema parsing when `extract` fails.
- Use `material skill-update validation` for production-gate evidence, not normal runtime workflow.
- Avoid `Pro`, `platform data`, `browser automation`, and upstream `60+ tools` as local v1 capabilities.

## Current Context

The repository root is `/data/lcq/.codex/skills`. The target is a docs-only material skill update under `brightdata/`. Existing dirty Bright Data edits predate this plan and are part of the active workstream; this plan must keep scope within Bright Data routing and supporting artifacts.

## Implementation Map

- Files: `brightdata/SKILL.md` - parent router precedence and removed-scope wording.
- Files: `brightdata/skills/brightdata-mcp-tools/SKILL.md` - workflow and boundary update.
- Files: `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md` - runtime workflow, current tool table, conditional extraction, research/RAG pointer.
- Files: `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md` - tool reference, checklist, validation split.
- Files: `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-research-rag.md` - lightweight Discover research/RAG workflow.
- Files: `brightdata/skills/brightdata-web-search/SKILL.md` and `brightdata/skills/brightdata-web-scrape/SKILL.md` - route text alignment.
- Symbols / APIs: Not applicable because this plan edits markdown skill guidance, not code symbols or APIs.
- Tests: `quick_validate.py` for touched Bright Data skills; `validate_plan_contract.py`; `validate_execution.py`; production report validator; reviewer report validator.
- Commands: exact commands are listed in `Validation Plan`.
- Data / migration impact: Not applicable because this is markdown skill guidance only.

## Assumptions

- `search_engine_batch` can be found via deferred tool discovery in this session.
- `discover`, `search_engine_batch`, `scrape_batch`, and `session_stats` still work in live MCP smoke.
- `extract` still may fail with `sampling/createMessage`, and that does not block v1 if fallback evidence is recorded.
- Quick validators are sufficient deterministic validators for these markdown skills.

## User Inputs Needed

Not applicable. The user confirmed scope and exclusions; account/config mutation for `extract` is a follow-up.

## Proposed Approach

Make a small docs-only patch that clarifies routing precedence, adds runtime availability checks, limits v1 tool claims to reliable current tools, preserves conditional `extract`, introduces reference-only research/RAG Discover guidance, then validate with deterministic and live MCP evidence plus production and reviewer gates.

## Scenario Probes

- RED/control: current `brightdata/SKILL.md` has conflicting “MCP only when needed” and “MCP-first” language.
- GREEN/retest: edited parent has one MCP-first precedence rule with CLI fallback criteria.
- RED/control: current refs route normal users to `extract` and narrow `web_data_*` too broadly.
- GREEN/retest: edited refs make `extract` conditional and narrow `web_data_*` out of normal v1 routing.

## Dependency Graph

1. Plan validation precedes implementation.
2. Bright Data file edits precede quick validators.
3. Quick validators precede live MCP smoke.
4. Live MCP smoke and diff inspection precede production report draft.
5. Production report draft and final report precede reviewer launch.
6. Reviewer PASS precedes final production report validation.

## Task Breakdown

### Task 1: Harden parent route

- Description: Update parent `brightdata/SKILL.md` to use one MCP-first priority rule and remove narrow reader promotion.
- Worker role: coding
- Wave: 1
- Acceptance criteria: Parent no longer says “MCP only when needed”; reliable MCP tools and CLI fallback criteria are clear.
- Verification: `python3 .system/skill-creator/scripts/quick_validate.py brightdata`
- Concrete edits: Patch `brightdata/SKILL.md`.
- Interfaces / contracts changed: Bright Data parent routing contract.
- Test cases: quick validator and diff inspection.
- Pre-check commands: `git diff --stat -- brightdata/SKILL.md`
- Post-check commands: `python3 .system/skill-creator/scripts/quick_validate.py brightdata`
- Dependencies: confirmed spec.
- Files likely touched: `brightdata/SKILL.md`
- Writable scope: `brightdata/SKILL.md`
- Output artifact: `.codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/task1-execution.md`
- Estimated scope: XS

### Task 2: Harden MCP child and refs

- Description: Update MCP child guidance and refs for deferred discovery, runtime checklist, conditional `extract`, v1 tool set, and validation split.
- Worker role: coding
- Wave: 1
- Acceptance criteria: MCP guidance names reliable tools, gates `extract`, removes narrow `web_data_*` recommendation, and separates runtime from material validation.
- Verification: `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-mcp-tools`
- Concrete edits: Patch MCP child `SKILL.md` and two MCP references.
- Interfaces / contracts changed: Bright Data MCP routing and validation contract.
- Test cases: quick validator, grep checks for narrow reader promotion, diff inspection.
- Pre-check commands: `git diff --stat -- brightdata/skills/brightdata-mcp-tools`
- Post-check commands: `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-mcp-tools`
- Dependencies: Task 1.
- Files likely touched: `brightdata/skills/brightdata-mcp-tools/SKILL.md`, `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`, `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`
- Writable scope: `brightdata/skills/brightdata-mcp-tools/`
- Output artifact: `.codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/task2-execution.md`
- Estimated scope: S

### Task 3: Add research/RAG guidance

- Description: Add lightweight Discover research/RAG guidance and align web-search/web-scrape routing to it.
- Worker role: coding
- Wave: 1
- Acceptance criteria: Research/RAG guidance covers multi-angle Discover, dedupe/rank, quality gates, provenance, and scrape-after-discover without Pro/platform/browser scope.
- Verification: `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-web-search && python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-web-scrape`
- Concrete edits: Add `bright-data-mcp-research-rag.md`; patch `brightdata-web-search/SKILL.md` and `brightdata-web-scrape/SKILL.md`.
- Interfaces / contracts changed: Search and scrape route docs.
- Test cases: quick validators and grep checks for excluded scope.
- Pre-check commands: `git diff --stat -- brightdata/skills/brightdata-web-search brightdata/skills/brightdata-web-scrape`
- Post-check commands: `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-web-search && python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-web-scrape`
- Dependencies: Task 2.
- Files likely touched: `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-research-rag.md`, `brightdata/skills/brightdata-web-search/SKILL.md`, `brightdata/skills/brightdata-web-scrape/SKILL.md`
- Writable scope: listed files only.
- Output artifact: `.codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/task3-execution.md`
- Estimated scope: S

### Task 4: Verify and smoke

- Description: Run deterministic validators, deferred tool discovery, live MCP smoke, structured extraction fallback, and diff inspection.
- Worker role: coding
- Wave: 2
- Acceptance criteria: Validators pass; smoke artifact records successful reliable tools and `extract` status; diff matches spec exclusions.
- Verification: commands in `Validation Plan`.
- Concrete edits: Write verification artifact only.
- Interfaces / contracts changed: Not applicable because this task validates changes.
- Test cases: live MCP public-target smoke and local schema parse check.
- Pre-check commands: `tool_search` for `search_engine_batch`; `mcp__brightdata.session_stats`
- Post-check commands: validators and git diff inspection.
- Dependencies: Tasks 1, 2, 3.
- Files likely touched: `.codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/mcp-smoke.md`, `.codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/task4-verification.md`
- Writable scope: plan workspace artifacts only.
- Output artifact: `.codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/task4-verification.md`
- Estimated scope: S

### Task 5: Production gate and review

- Description: Write execution/final/production artifacts, validate production gate, run reviewer, apply bounded rework if needed, and validate final production report.
- Worker role: review
- Wave: 3
- Acceptance criteria: Production report draft and final validate; reviewer report is PASS; execution validator passes.
- Verification: `validate_skill_production.py`, `pre_review_ready.py`, `validate_review_report.py`, `validate_execution.py`.
- Concrete edits: Write production report, review report, final report, execution tasks JSON.
- Interfaces / contracts changed: Not applicable because this task gates completed edits.
- Test cases: production gate and reviewer validators.
- Pre-check commands: `python3 skill-tokenless/scripts/validate_skill_production.py ... --stage draft`
- Post-check commands: `python3 skill-tokenless/scripts/validate_skill_production.py ... --stage final`
- Dependencies: Task 4.
- Files likely touched: `.codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/production-report.md`, `.codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/final-report.md`, `.codex/work/20260622-brightdata-mcp-routing-hardening/review-implementation.md`, `.codex/work/20260622-brightdata-mcp-routing-hardening/execution/tasks.json`
- Writable scope: plan workspace artifacts only.
- Output artifact: `.codex/work/20260622-brightdata-mcp-routing-hardening/review-implementation.md`
- Estimated scope: S

## Step-by-Step Plan

1. Validate this `plan.md` with the plan contract validator.
2. Patch `brightdata/SKILL.md`.
3. Patch `brightdata/skills/brightdata-mcp-tools/SKILL.md`, `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`, and `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`.
4. Add `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-research-rag.md` and patch `brightdata/skills/brightdata-web-search/SKILL.md` plus `brightdata/skills/brightdata-web-scrape/SKILL.md`.
5. Run `python3 .system/skill-creator/scripts/quick_validate.py brightdata` and child skill validators.
6. Run `tool_search` for `search_engine_batch` and MCP smoke calls `session_stats`, `discover`, `search_engine_batch`, `scrape_batch`, and `extract`.
7. Inspect `git diff -- brightdata`.
8. Write `.codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/final-report.md` and `.codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/production-report.md`.
9. Validate production draft with `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft` and readiness with `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260622-brightdata-mcp-routing-hardening --stage draft --require-production-report --require-final-report`.
10. Write reviewer gate artifact `.codex/work/20260622-brightdata-mcp-routing-hardening/review-implementation.md`.
11. Validate reviewer, execution state, and production final with exact commands from `Validation Plan`.

## Parallelization

Primary-agent execution only. Tasks 1 through 3 touch related docs and should run sequentially to avoid conflicting wording.

## Files / Components Likely Affected

- `brightdata/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/SKILL.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`
- `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-research-rag.md`
- `brightdata/skills/brightdata-web-search/SKILL.md`
- `brightdata/skills/brightdata-web-scrape/SKILL.md`
- `.codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/`
- `.codex/work/20260622-brightdata-mcp-routing-hardening/execution/`

## Owners / Responsibilities

- Primary agent: implement docs, run validators, run real MCP smoke, write artifacts, perform reviewer gate.
- User: no input needed for v1; follow-up input may be needed to fix `extract` sampling/client/server support.

## Validation Plan

- `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260622-brightdata-mcp-routing-hardening/plan.md --mode light`
- `python3 .system/skill-creator/scripts/quick_validate.py brightdata`
- `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-mcp-tools`
- `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-web-search`
- `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-web-scrape`
- `tool_search` for `search_engine_batch`
- MCP smoke: `session_stats`, `discover`, `search_engine_batch`, `scrape_batch`, `extract` status check, scrape plus local schema parsing fallback.
- `git diff -- brightdata`
- `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
- `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260622-brightdata-mcp-routing-hardening --stage draft --require-production-report --require-final-report`
- `python3 reviewer/scripts/validate_review_report.py .codex/work/20260622-brightdata-mcp-routing-hardening/review-implementation.md`
- `python3 plan2do/scripts/validate_execution.py .codex/work/20260622-brightdata-mcp-routing-hardening`
- `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260622-brightdata-mcp-routing-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`

## Rollout Plan

Not applicable. This is a local skill documentation update; rollout is immediate once files are saved and validators pass.

## Monitoring / Observability

Use `session_stats` during MCP smoke and record counts in `artifacts/mcp-smoke.md`. Future tasks should use the runtime checklist and `session_stats` for validation-heavy or multi-call MCP work.

## Documentation / ADR Updates

ADR: Not needed. This is a skill guidance update documented in the skill files and plan artifacts.

## Rollback / Recovery Plan

Use git diff to identify scoped changes. If validation fails, patch only touched Bright Data docs or plan artifacts. If live MCP smoke fails for reliable tools, record blocker and do not mark COMPLETE. No data migration or destructive operation exists.

## Abort Criteria

- Quick validators fail and cannot be fixed within two focused rework cycles.
- Reliable MCP tools `discover`, `search_engine_batch`, `scrape_batch`, or `session_stats` are unavailable with no safe fallback evidence.
- Reviewer returns BLOCK.
- Production report final validation fails after bounded rework.
- Diff restores excluded Pro/platform/browser/60+ catalog scope.

## Risks

- Existing dirty Bright Data files may include unrelated prior edits; mitigate with targeted patches and diff inspection.
- Live MCP availability can change; mitigate by recording exact tool results and fallback status.
- `extract` may remain broken; mitigate by preserving it as conditional and documenting follow-up.

## Open Questions

None for v1 implementation.

## Plan Self-Review

- The plan is reversible and docs-only.
- Tasks have concrete files, commands, acceptance criteria, and artifacts.
- Production gate is included because this is a material skill workflow update.
- Excluded scope is explicit.
- Writable scope: confined to listed Bright Data docs and the plan workspace artifacts.
- Coverage: tasks cover parent routing, MCP refs, research/RAG guidance, validators, smoke, production gate, and review.
- Unknown: `extract` repair remains a documented follow-up, not v1 acceptance.
- Rollback: scoped markdown diffs can be reverted from `git diff -- brightdata`.
- Task 1: parent route change is independently verifiable with quick validation and diff inspection.

## Execution Decision

Proceed with primary-agent execution.

## Execution Handoff

- Goal: implement Bright Data MCP routing hardening from the confirmed spec.
- Current state: plan validated before execution, then primary-agent `plan2do` executes.
- Authoritative artifacts: `.codex/work/20260622-brightdata-mcp-routing-hardening/spec.md`, `.codex/work/20260622-brightdata-mcp-routing-hardening/plan.md`
- Decisions: v1 keeps `extract` conditional, excludes Pro/platform/browser/60+ catalog, and adds lightweight research/RAG reference guidance.
- Remaining risks: `extract` unresolved by design; live MCP availability must be rechecked.
- Next action: execute Task 1 with `plan2do` primary-agent flow.
- Suggested skills: `plan2do`, `edit-orchestration`, `skill-tokenless`, `reviewer`, `debugging-and-error-recovery` if validation fails.
- Redactions / omitted raw data: raw MCP outputs and large diffs stay in artifacts or command logs, not final response.
