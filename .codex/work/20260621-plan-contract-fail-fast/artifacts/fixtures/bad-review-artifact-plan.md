# Bad Review Artifact Fixture

Mode: light
Risk level: Low
Confidence: High

## Goal
Provide a bad fixture where a review task writes `artifacts/final-report.md` without explicitly requiring a standalone verdict in that artifact.

## Non-Goals
Not applicable; fixture only.

## Evidence Inspected
- `.codex/work/20260621-plan-contract-fail-fast/spec.md`

## Spec Summary
This fixture should fail semantic review artifact validation after the fail-fast rule is implemented.

## Domain Language Check
Use `Worker role`, `Output artifact`, `review`, and `final-report.md`.

## Current Context
Local fixture plan for validator testing.

## Implementation Map
- Files: `.codex/work/20260621-plan-contract-fail-fast/artifacts/example.md`
- Symbols / APIs: `validate_plan_contract.py`
- Tests: `bad-review-artifact-plan.md`
- Commands: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md --mode light`
- Data / migration impact: Not applicable; fixture only.

## Assumptions
This fixture is intentionally invalid only because Task 1 is a review task outputting `artifacts/final-report.md`.

## User Inputs Needed
No input needed.

## Proposed Approach
Use one review task with an output artifact that looks like a final report.

## Scenario Probes
The validator should report Task 1 and `Output artifact` once the semantic rule exists.

## Dependency Graph
Task 1 has no dependencies.

## Task Breakdown

### Task 1: Review with final report output

- Description: Review a local fixture and write a final report artifact.
- Worker role: review
- Wave: 1
- Acceptance criteria: Review is complete.
- Verification: `python3 -m py_compile /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py`
- Concrete edits: Write `.codex/work/20260621-plan-contract-fail-fast/artifacts/final-report.md`.
- Interfaces / contracts changed: No command; fixture only.
- Test cases: Semantic rule should reject this task.
- Pre-check commands: `test -f /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py`
- Post-check commands: `python3 -m py_compile /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py`
- Dependencies: None.
- Files likely touched: `.codex/work/20260621-plan-contract-fail-fast/artifacts/final-report.md`
- Writable scope: `.codex/work/20260621-plan-contract-fail-fast/artifacts/final-report.md`
- Output artifact: `.codex/work/20260621-plan-contract-fail-fast/artifacts/final-report.md`
- Estimated scope: XS

## Step-by-Step Plan
1. Run `python3 -m py_compile /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py`.
2. Write `.codex/work/20260621-plan-contract-fail-fast/artifacts/final-report.md`.

## Parallelization
No parallel work; one task only.

## Files / Components Likely Affected
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/final-report.md`

## Owners / Responsibilities
- Main agent: fixture validation.

## Validation Plan
- Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md --mode light`.

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
Abort if this fixture cannot isolate the intended invalid review artifact condition.

## Risks
Fixture could fail unrelated plan checks; mitigate by keeping required sections complete.

## Open Questions
No blocker questions.

## Plan Self-Review
- Writable scope is exact and non-overlapping.
- Coverage is provided by a semantic invalid fixture.
- Unknown behavior is named in assumptions.
- Rollback is deleting only this fixture.
- Task 1 is executable from this plan.

## Execution Decision
Use this fixture only for validation.

## Execution Handoff

- Goal: Test invalid review artifact fail-fast behavior.
- Current state: Fixture is intentionally semantically invalid.
- Authoritative artifacts: `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md`
- Decisions: Keep only one invalid condition.
- Verification: Run the plan validator and compiler against this fixture.
- Remaining risks: Fixture may expose unrelated validation errors.
- Next action: Expect validation failure after semantic rule implementation.
- Suggested skills: `test-driven-development`
- Redactions / omitted raw data: None.
