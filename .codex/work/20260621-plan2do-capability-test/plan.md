# Plan: plan2do Capability Fixture

Mode: light
Risk level: Low
Confidence: High

## Goal
Validate that `plan2do` can intake a concrete plan, keep context focused, execute a task, catch failed verification, write rework guidance, fix the issue, review quality, and produce final artifacts without polluting active context.

## Non-Goals
- Do not modify real skill implementation files.
- Do not use `codex2codex` workers.
- Do not perform destructive, production, security, schema, dependency, or git-history actions.

## Evidence Inspected
- `/data/lcq/.codex/skills/plan2do/SKILL.md`
- `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- `/data/lcq/.codex/skills/context-engineering/SKILL.md`
- `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`

## Spec Summary
This disposable plan tests the primary-agent `plan2do` path on a safe fixture file. The task is complete only when the fixture contains both `feature=enabled` and `quality=verified`.

## Domain Language Check
Use `plan2do` terms: primary-agent mode, focused context pack, verification, review, rework guidance, final acceptance, and `INCOMPLETE` on failure.

## Current Context
The plan workspace is `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test`. The only writable product file is `fixture/status.txt`.

## Implementation Map
- Files: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt` stores fixture state.
- Symbols / APIs: plain text keys `feature` and `quality`.
- Tests: `grep -qx 'feature=enabled' .../fixture/status.txt && grep -qx 'quality=verified' .../fixture/status.txt`.
- Commands: `grep -qx 'feature=enabled' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt && grep -qx 'quality=verified' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`.
- Data / migration impact: Not applicable because this writes a disposable fixture only.

## Assumptions
- Primary-agent mode is the intended test mode because the user asked whether `plan2do` can self-manage context.
- `codex2codex` live execution is outside this test because the user did not explicitly request that backend.

## User Inputs Needed
None.

## Proposed Approach
Use `plan2do` primary-agent mode. First perform an intentional partial implementation to verify failure detection and rework behavior. Then write rework guidance, fix the fixture, rerun verification, review, and final acceptance.

## Scenario Probes
- Intake accepts a valid `spec2plan` contract plan.
- Focused context artifacts are written before execution and review.
- Verification failure blocks completion.
- Rework guidance precedes the fix.
- Final success is reported only after verification and review pass.

## Dependency Graph
Task 1 has no task dependencies.

## Task Breakdown
### Task 1: Update fixture status

- Description: Update the fixture file so it contains both required status lines.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt` contains one line `feature=enabled` and one line `quality=verified`.
- Verification: `grep -qx 'feature=enabled' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt && grep -qx 'quality=verified' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`
- Concrete edits: Replace `feature=disabled` with `feature=enabled` and add `quality=verified`.
- Interfaces / contracts changed: Fixture text contract requires both keys.
- Test cases: Verification command fails if either required line is missing.
- Pre-check commands: `grep -qx 'feature=disabled' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`
- Post-check commands: `grep -qx 'feature=enabled' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt && grep -qx 'quality=verified' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`
- Dependencies: None.
- Files likely touched: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`
- Writable scope: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`
- Output artifact: `.codex/work/20260621-plan2do-capability-test/artifacts/task1-execution.md`
- Estimated scope: XS

## Step-by-Step Plan
1. Write `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/artifacts/context-task1.md`.
2. Edit `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`.
3. Run `grep -qx 'feature=enabled' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt && grep -qx 'quality=verified' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`.
4. If verification fails, write `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/artifacts/rework-guidance.md` before fixing.
5. Write `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/artifacts/review.md` with `Verdict: PASS` or `Verdict: FAIL`.

## Parallelization
No parallelization. There is one task and one writable file.

## Files / Components Likely Affected
- `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`
- `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/artifacts/*.md`

## Owners / Responsibilities
- coding: edit fixture and run verification.
- review: inspect verification, fixture content, artifact hygiene, and context-governance behavior.
- primary agent: write rework guidance before fix and own final acceptance.

## Validation Plan
Run `python /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/plan.md --mode light`.
Run the task verification command after implementation and after rework.
Review artifacts and final status.

## Rollout Plan
Not applicable because this is a disposable fixture test.

## Monitoring / Observability
Write focused context, execution, verification, review, rework guidance, and final report artifacts under `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/artifacts/`.

## Documentation / ADR Updates
ADR: Not needed. Fixture test only.

## Rollback / Recovery Plan
Reset the fixture to `feature=disabled` only if the user requests cleanup. Do not touch other files.

## Abort Criteria
Abort if any action would touch files outside `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/`.

## Risks
- The test is artificial and cannot prove every real project path. It can prove plan intake, verification, rework, review, artifacts, and context hygiene mechanics.

## Open Questions
None.

## Plan Self-Review
- writable scope is exact and same-wave writes do not overlap.
- coverage includes plan validation, fixture verification, failure injection, rework, and review.
- unknown handling is explicit in `Assumptions` and `Open Questions`.
- rollback and abort criteria are specific for this low-risk fixture.
- Task 1 can be executed by a fresh agent from this plan without raw transcript context.

## Execution Decision
Ready for primary-agent `plan2do` test execution.

## Execution Handoff

- Goal: Test `plan2do` primary-agent execution and context hygiene.
- Current state: Fixture starts as `feature=disabled`.
- Authoritative artifacts: `.codex/work/20260621-plan2do-capability-test/plan.md`
- Decisions: Use primary-agent mode; inject one intentional verification failure; write rework guidance before fix.
- Verification: `grep -qx 'feature=enabled' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt && grep -qx 'quality=verified' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`
- Remaining risks: Fixture is artificial.
- Next action: Validate plan intake, then execute Task 1.
- Suggested skills: plan2do; context-engineering; apply-patch.
- Redactions / omitted raw data: Raw command output omitted from final response; summarized in artifacts.
