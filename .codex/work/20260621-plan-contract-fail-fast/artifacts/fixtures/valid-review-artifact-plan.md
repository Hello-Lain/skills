# Valid Review Artifact Fixture

Mode: light
Risk level: Low
Confidence: High

## Goal
Provide a valid fixture where a review task writes `.codex/work/20260621-plan-contract-fail-fast/review.md`.

## Non-Goals
Not applicable; fixture only.

## Evidence Inspected
- `.codex/work/20260621-plan-contract-fail-fast/spec.md`

## Spec Summary
This fixture should pass plan validation and compile into a task state.

## Domain Language Check
Use `Worker role`, `Output artifact`, `review`, and `review.md`.

## Current Context
Local fixture plan for validator testing.

## Implementation Map
- Files: `.codex/work/20260621-plan-contract-fail-fast/review.md`
- Symbols / APIs: `validate_plan_contract.py`, `compile_execution.py`
- Tests: `valid-review-artifact-plan.md`
- Commands: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md --mode light`
- Data / migration impact: Not applicable; fixture only.

## Assumptions
Review-role tasks should output a review artifact by default.

## User Inputs Needed
No input needed.

## Proposed Approach
Use one review task with `review.md` as the output artifact.

## Scenario Probes
The validator and compiler should accept this fixture.

## Dependency Graph
Task 1 has no dependencies.

## Task Breakdown

### Task 1: Review with review artifact output

- Description: Review a local fixture and write a review artifact.
- Worker role: review
- Wave: 1
- Acceptance criteria: Review artifact contains `Verdict: PASS`.
- Verification: `python3 -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py`
- Concrete edits: Write `.codex/work/20260621-plan-contract-fail-fast/review.md`.
- Interfaces / contracts changed: No command; fixture only.
- Test cases: Semantic rule should accept this task.
- Pre-check commands: `test -f /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py`
- Post-check commands: `python3 -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py`
- Dependencies: None.
- Files likely touched: `.codex/work/20260621-plan-contract-fail-fast/review.md`
- Writable scope: `.codex/work/20260621-plan-contract-fail-fast/review.md`
- Output artifact: `.codex/work/20260621-plan-contract-fail-fast/review.md`
- Estimated scope: XS

## Step-by-Step Plan
1. Run `python3 -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py`.
2. Write `.codex/work/20260621-plan-contract-fail-fast/review.md`.

## Parallelization
No parallel work; one task only.

## Files / Components Likely Affected
- `.codex/work/20260621-plan-contract-fail-fast/review.md`

## Owners / Responsibilities
- Main agent: fixture validation.

## Validation Plan
- Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md --mode light`.

## Rollout Plan
Not applicable; fixture only.

## Monitoring / Observability
Not applicable; fixture only.

## Documentation / ADR Updates
ADR: Not needed

No documentation changes.

## Rollback / Recovery Plan
Delete only this fixture file if it is malformed.

## Abort Criteria
Abort if this fixture cannot isolate the intended valid review artifact condition.

## Risks
Fixture could fail unrelated plan checks; mitigate by keeping required sections complete.

## Open Questions
No blocker questions.

## Plan Self-Review
- Writable scope is exact and non-overlapping.
- Coverage is provided by a semantic valid fixture.
- Unknown behavior is named in assumptions.
- Rollback is deleting only this fixture.
- Task 1 is executable from this plan.

## Execution Decision
Use this fixture only for validation.

## Execution Handoff

- Goal: Test valid review artifact behavior.
- Current state: Fixture should be valid.
- Authoritative artifacts: `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md`
- Decisions: Keep one valid review condition.
- Verification: Run the plan validator and compiler against this fixture.
- Remaining risks: Fixture may expose unrelated validation errors.
- Next action: Expect validation pass after semantic rule implementation.
- Suggested skills: `test-driven-development`
- Redactions / omitted raw data: None.
