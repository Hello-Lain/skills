# Plan Contract Fail-Fast Implementation Plan

Mode: light
Risk level: Medium
Confidence: High

## Goal
Implement the confirmed spec at `.codex/work/20260621-plan-contract-fail-fast/spec.md` so invalid review-role output artifacts fail during `spec2plan` validation or `plan2do` compilation instead of late final acceptance.

## Non-Goals
- Do not add CUE, JSON Schema, Pydantic, DSPy, GEPA, OpenAI, or other mandatory dependencies.
- Do not redesign the Markdown plan format.
- Do not auto-rewrite invalid plans.
- Do not modify unrelated skills outside `spec2plan/`, `plan2do/`, and the current work artifacts.
- Do not make context artifact absence a hard failure in v1; document explicit exemption behavior instead.

## Evidence Inspected
- `.codex/work/20260621-plan-contract-fail-fast/spec.md`
- `.codex/work/20260621-plan-contract-fail-fast/manifest.yaml`
- `/data/lcq/.codex/skills/spec2plan/SKILL.md`
- `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- `/data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py`
- `/data/lcq/.codex/skills/plan2do/SKILL.md`
- `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- `/data/lcq/.codex/skills/plan2do/references/failure-policy.md`
- `/data/lcq/.codex/skills/plan2do/references/review-rubric.md`
- `/data/lcq/.codex/skills/plan2do/scripts/compile_execution.py`
- `/data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`
- CodeGraph exploration for `validate_plan_contract.task_errors`, `_output_artifact_errors`, and `compile_execution.compile_plan`
- `git -C /data/lcq/.codex/skills diff -- spec2plan/SKILL.md spec2plan/references/plan-contract.md spec2plan/scripts/validate_plan_contract.py plan2do/SKILL.md plan2do/references/execution-contract.md plan2do/scripts/compile_execution.py plan2do/scripts/validate_execution.py`

## Spec Summary
Add Python semantic checks, inspired by actionlint-style pre-execution lint, to prevent review artifact and final report contract drift between `spec2plan` and `plan2do`. Keep v1 lightweight and local.

## Domain Language Check
- Use existing terms: `Worker role`, `Output artifact`, `review artifact`, `final report`, `Verdict: PASS`, `Verdict: FAIL`, `compile_execution.py`, `validate_plan_contract.py`, `validate_execution.py`, `execution/tasks.json`.
- Preserve plan contract terms: `Task Breakdown`, `Writable scope`, `Verification`, `Acceptance criteria`, `Execution Handoff`.
- Use source reuse terms only as provenance: `actionlint-style semantic lint`, `schema-first v2`, `cross-field constraint`.

## Current Context
The workspace has unrelated modified and untracked files. Current target files show existing hardening changes in `spec2plan/SKILL.md`, `spec2plan/references/plan-contract.md`, and `spec2plan/scripts/validate_plan_contract.py`. `plan2do/` is untracked in git status, but its scripts exist on disk and are the active skill implementation. This plan must preserve existing changes and apply only scoped additions.

## Implementation Map
- Files: `spec2plan/scripts/validate_plan_contract.py` for semantic plan validation; `plan2do/scripts/compile_execution.py` for compile-time fail-fast; `plan2do/scripts/validate_execution.py` for alignment only if needed; `.codex/work/20260621-plan-contract-fail-fast/artifacts/` for fixtures and execution records; `.codex/work/20260621-plan-contract-fail-fast/review.md` for review verdict; `.codex/work/20260621-plan-contract-fail-fast/manifest.yaml` for canonical plan lineage.
- Symbols / APIs: `task_errors`, `_task_fields`, `_scope_paths`, `_output_artifact_errors`, `compile_plan`, `_paths`, `_clean`, `_resolve_path`, `validate_workspace`.
- Tests: fixture plans under `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/`; commands invoking `validate_plan_contract.py`, `compile_execution.py`, `py_compile`, and final `validate_execution.py`.
- Commands: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md --mode light`; `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md`; focused fixture commands named in Task 3; `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast`.
- Data / migration impact: Not applicable; no persistent data store, schema, auth, release, or migration surface is touched.

## Assumptions
- The exact escape hatch for a non-`review*.md` review artifact is explicit task text containing standalone verdict requirement wording such as `standalone Verdict: PASS or Verdict: FAIL`.
- Context artifact absence should remain visible in plan2do artifacts, but not block v1 completion because the current spec leaves hard-failure behavior open.
- Existing `spec2plan` hardening changes are intentional and must be preserved.

## User Inputs Needed
No input needed before execution. The user explicitly asked to use `spec2plan` and `plan2do` to land the confirmed spec.

## Proposed Approach
Use a small shared semantic rule implemented independently in both active Python entrypoints: `spec2plan` rejects invalid review-role output artifacts while validating Markdown plans, and `plan2do` rejects the same invalid shape while compiling tasks. Add local fixture plans to prove one invalid plan fails early and one valid plan still passes. Document context artifact behavior as an explicit v1 exemption in execution artifacts rather than expanding scope.

## Scenario Probes
- Invalid review task: `Worker role: review` with `Output artifact: .codex/work/<topic>/artifacts/final-report.md` and no standalone verdict requirement should fail in both scripts.
- Valid review task: `Worker role: review` with `Output artifact: .codex/work/<topic>/review.md` should pass.
- Escape hatch: `Worker role: review` with a non-review output artifact and explicit standalone `Verdict: PASS or Verdict: FAIL` requirement should pass compile if preserved in the task fields.
- Current work plan should remain valid under the new semantic rule.

## Dependency Graph
Task 1 -> Task 2 -> Task 3 -> Task 4 -> Task 5

Task 1 writes regression fixtures first. Task 2 updates `spec2plan` validation. Task 3 updates `plan2do` compilation and runs focused checks. Task 4 updates docs/artifacts and runs full validation. Task 5 reviews and finalizes execution.

## Task Breakdown

### Task 1: Add fail-fast regression fixtures

- Description: Create fixture plans that reproduce the invalid review artifact shape and a valid review artifact shape.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `bad-review-artifact-plan.md` exists and contains a review task outputting `artifacts/final-report.md`; `valid-review-artifact-plan.md` exists and contains a review task outputting `review.md`; task artifact records fixture intent.
- Verification: `test -f /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md && test -f /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md`
- Concrete edits: Create `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md`; create `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md`; create `.codex/work/20260621-plan-contract-fail-fast/artifacts/task1-execution.md`.
- Interfaces / contracts changed: No command; fixtures are local test inputs only.
- Test cases: Invalid review task fixture; valid review task fixture.
- Pre-check commands: `test -d /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast`
- Post-check commands: `test -f /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md && test -f /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md`
- Dependencies: None.
- Files likely touched: `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/task1-execution.md`
- Writable scope: `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/task1-execution.md`
- Output artifact: `.codex/work/20260621-plan-contract-fail-fast/artifacts/task1-execution.md`
- Estimated scope: S

### Task 2: Add spec2plan semantic validation

- Description: Extend `validate_plan_contract.py` so review-role tasks fail when their output artifact is not a review artifact and task text lacks an explicit standalone verdict requirement.
- Worker role: coding
- Wave: 2
- Acceptance criteria: Bad fixture fails `validate_plan_contract.py` with task number, `Output artifact`, and repair guidance; valid fixture passes; current canonical plan passes.
- Verification: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md --mode light && python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md --mode light`
- Concrete edits: Patch `spec2plan/scripts/validate_plan_contract.py` to add review artifact helpers and call them from `task_errors`; write `.codex/work/20260621-plan-contract-fail-fast/artifacts/task2-execution.md`.
- Interfaces / contracts changed: `validate_plan_contract.py` gains a cross-field semantic error for review-role output artifact mismatch.
- Test cases: Bad fixture expected failure; valid fixture expected pass; current plan expected pass.
- Pre-check commands: `python3 -m py_compile /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py`
- Post-check commands: `python3 -m py_compile /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py && python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md --mode light && python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md --mode light`
- Dependencies: Task 1.
- Files likely touched: `spec2plan/scripts/validate_plan_contract.py`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/task2-execution.md`
- Writable scope: `spec2plan/scripts/validate_plan_contract.py`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/task2-execution.md`
- Output artifact: `.codex/work/20260621-plan-contract-fail-fast/artifacts/task2-execution.md`
- Estimated scope: S

### Task 3: Add plan2do compile-time fail-fast

- Description: Extend `compile_execution.py` so the same invalid review-role output artifact shape fails before `execution/tasks.json` is written.
- Worker role: coding
- Wave: 3
- Acceptance criteria: Bad fixture fails `compile_execution.py` before creating a task state; valid fixture compiles to a temporary output; error mentions task number, `Output artifact`, and repair guidance.
- Verification: `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md --output /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/valid-fixture-tasks.json`
- Concrete edits: Patch `plan2do/scripts/compile_execution.py` to add equivalent review artifact semantic check before task append; write `.codex/work/20260621-plan-contract-fail-fast/artifacts/task3-execution.md`.
- Interfaces / contracts changed: `compile_execution.py` gains fail-fast semantic errors for invalid review-role output artifacts.
- Test cases: Bad fixture expected failure; valid fixture expected compile success.
- Pre-check commands: `python3 -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py`
- Post-check commands: `python3 -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py && python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md --output /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/valid-fixture-tasks.json`
- Dependencies: Task 2.
- Files likely touched: `plan2do/scripts/compile_execution.py`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/task3-execution.md`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/valid-fixture-tasks.json`
- Writable scope: `plan2do/scripts/compile_execution.py`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/task3-execution.md`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/valid-fixture-tasks.json`
- Output artifact: `.codex/work/20260621-plan-contract-fail-fast/artifacts/task3-execution.md`
- Estimated scope: S

### Task 4: Validate integrated plan execution

- Description: Compile this plan, run targeted failure and success commands, compile Python files, and document context artifact v1 exemption.
- Worker role: coding
- Wave: 4
- Acceptance criteria: This plan validates; this plan compiles into `execution/tasks.json`; bad fixture fails both fail-fast scripts; valid fixture passes both scripts; task artifact records command outcomes.
- Verification: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md --mode light && python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md`
- Concrete edits: Write `.codex/work/20260621-plan-contract-fail-fast/artifacts/task4-verification.md`; update `.codex/work/20260621-plan-contract-fail-fast/manifest.yaml` stage and plan lineage if not already updated.
- Interfaces / contracts changed: `manifest.yaml` marks `plan.md` as canonical plan.
- Test cases: Current plan validation; current plan compilation; bad fixture fail-fast; valid fixture pass.
- Pre-check commands: `test -f /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md`
- Post-check commands: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md --mode light && python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md`
- Dependencies: Task 3.
- Files likely touched: `.codex/work/20260621-plan-contract-fail-fast/artifacts/task4-verification.md`; `.codex/work/20260621-plan-contract-fail-fast/manifest.yaml`; `.codex/work/20260621-plan-contract-fail-fast/execution/tasks.json`
- Writable scope: `.codex/work/20260621-plan-contract-fail-fast/artifacts/task4-verification.md`; `.codex/work/20260621-plan-contract-fail-fast/manifest.yaml`; `.codex/work/20260621-plan-contract-fail-fast/execution/tasks.json`
- Output artifact: `.codex/work/20260621-plan-contract-fail-fast/artifacts/task4-verification.md`
- Estimated scope: S

### Task 5: Review and final acceptance

- Description: Review scoped changes for functional completeness, regression coverage, simplicity, and artifact integrity; write final report.
- Worker role: review
- Wave: 5
- Acceptance criteria: `.codex/work/20260621-plan-contract-fail-fast/review.md` contains `Verdict: PASS`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/final-report.md` records mode, status, files, commands, review, rework cycles, and risks; final execution validator passes.
- Verification: `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast`
- Concrete edits: Write `.codex/work/20260621-plan-contract-fail-fast/review.md`; write `.codex/work/20260621-plan-contract-fail-fast/artifacts/final-report.md`; update `.codex/work/20260621-plan-contract-fail-fast/execution/tasks.json` statuses after task artifacts and verification evidence exist.
- Interfaces / contracts changed: No command; review confirms prior task changes.
- Test cases: Review rubric PASS conditions; final execution validator.
- Pre-check commands: `test -f /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/task4-verification.md`
- Post-check commands: `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast`
- Dependencies: Task 4.
- Files likely touched: `.codex/work/20260621-plan-contract-fail-fast/review.md`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/final-report.md`; `.codex/work/20260621-plan-contract-fail-fast/execution/tasks.json`
- Writable scope: `.codex/work/20260621-plan-contract-fail-fast/review.md`; `.codex/work/20260621-plan-contract-fail-fast/artifacts/final-report.md`; `.codex/work/20260621-plan-contract-fail-fast/execution/tasks.json`
- Output artifact: `.codex/work/20260621-plan-contract-fail-fast/review.md`
- Estimated scope: S

## Step-by-Step Plan
1. Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md --mode light`.
2. Create `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md`.
3. Create `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md`.
4. Write `.codex/work/20260621-plan-contract-fail-fast/artifacts/task1-execution.md`.
5. Patch `spec2plan/scripts/validate_plan_contract.py` near `task_errors` and `_output_artifact_errors`.
6. Run `python3 -m py_compile /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py`.
7. Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md --mode light` and confirm nonzero failure.
8. Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md --mode light`.
9. Write `.codex/work/20260621-plan-contract-fail-fast/artifacts/task2-execution.md`.
10. Patch `plan2do/scripts/compile_execution.py` near `compile_plan`.
11. Run `python3 -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py`.
12. Run `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md` and confirm nonzero failure.
13. Run `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md --output /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/valid-fixture-tasks.json`.
14. Write `.codex/work/20260621-plan-contract-fail-fast/artifacts/task3-execution.md`.
15. Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md --mode light`.
16. Run `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md`.
17. Write `.codex/work/20260621-plan-contract-fail-fast/artifacts/task4-verification.md`.
18. Write `.codex/work/20260621-plan-contract-fail-fast/review.md` with `Verdict: PASS` or `Verdict: FAIL`.
19. Write `.codex/work/20260621-plan-contract-fail-fast/artifacts/final-report.md`.
20. Run `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast`.

## Parallelization
No parallel implementation waves are planned. Task 2 depends on fixtures from Task 1, Task 3 depends on the same rule semantics from Task 2, Task 4 integrates both scripts, and Task 5 reviews all outputs. Same-wave write overlap does not occur.

## Files / Components Likely Affected
- `spec2plan/scripts/validate_plan_contract.py`
- `plan2do/scripts/compile_execution.py`
- `.codex/work/20260621-plan-contract-fail-fast/manifest.yaml`
- `.codex/work/20260621-plan-contract-fail-fast/plan.md`
- `.codex/work/20260621-plan-contract-fail-fast/execution/tasks.json`
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md`
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md`
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/valid-fixture-tasks.json`
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/task1-execution.md`
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/task2-execution.md`
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/task3-execution.md`
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/task4-verification.md`
- `.codex/work/20260621-plan-contract-fail-fast/review.md`
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/final-report.md`

## Owners / Responsibilities
- Main agent: generate plan, execute scoped code changes, run checks, review, final acceptance.
- `spec2plan`: source plan validation and canonical plan contract.
- `plan2do`: execution compilation, review/final validation, and task artifact discipline.
- `context-engineering`: lite context governance with source rehydration before edits and final acceptance.
- `edit-orchestration`: fast-path patching and diff gate.
- `test-driven-development`: fixture-first fail-fast checks.

## Validation Plan
- Validate plan: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md --mode light`
- Compile plan: `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md`
- Compile scripts: `python3 -m py_compile /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py && python3 -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py && python3 -m py_compile /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`
- Bad fixture validation: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md --mode light` should fail.
- Bad fixture compilation: `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md` should fail.
- Valid fixture validation: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md --mode light`
- Valid fixture compilation: `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md --output /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/valid-fixture-tasks.json`
- Final execution validation: `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast`

## Rollout Plan
Local-only rollout. Updated validators take effect immediately from `/data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py` and `/data/lcq/.codex/skills/plan2do/scripts/compile_execution.py` after verification passes. No deployment, release, package publish, or git commit is part of this plan.

## Monitoring / Observability
Not applicable for runtime monitoring; this is a local skill validation change. Observability is through fixture command output, task artifacts, review verdict, final report, and final execution validator output.

## Documentation / ADR Updates
ADR: Not needed

No separate documentation file is required for v1. The rule is encoded in script diagnostics and task artifacts. Future v2 schema tooling remains documented in the confirmed spec.

## Rollback / Recovery Plan
- If fixture creation is wrong, patch only `.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/*.md` and rerun fixture commands.
- If `spec2plan` validation overrejects, patch only `spec2plan/scripts/validate_plan_contract.py` and rerun bad/valid fixture checks plus current plan validation.
- If `plan2do` compilation overrejects, patch only `plan2do/scripts/compile_execution.py` and rerun bad/valid fixture checks plus current plan compilation.
- If final execution validation fails, write `.codex/work/20260621-plan-contract-fail-fast/artifacts/rework-guidance.md`, perform one scoped fix, and rerun the failing check.
- To roll back after completion, revert only the changes in `spec2plan/scripts/validate_plan_contract.py`, `plan2do/scripts/compile_execution.py`, and this topic workspace artifacts created during execution.

## Abort Criteria
- Abort if target scripts changed unexpectedly in a way that invalidates the identified insertion points.
- Abort if valid fixture cannot be made to pass without weakening the bad fixture failure.
- Abort if a required validation command fails twice with the same error after scoped rework.
- Abort if implementation requires adding a mandatory dependency.
- Abort if changes outside the writable scope become necessary.

## Risks
- False positive risk: a legitimate review task may intentionally output a final report. Mitigation: allow an explicit standalone verdict requirement escape hatch.
- Rule drift risk: similar logic exists in both scripts. Mitigation: keep the helper small and identical in behavior; extract shared code only if future rules grow.
- Context artifact ambiguity: v1 does not hard-fail missing `context-task<N>.md`. Mitigation: document exemption and leave strict enforcement for a later confirmed change.
- Dirty worktree risk: existing modifications may be user work. Mitigation: patch only scoped files and inspect diffs.

## Open Questions
No blocker questions remain for v1 execution. Context artifact hard-failure remains a later policy decision.

## Plan Self-Review
- Every task has exact writable scope and same-wave writes do not overlap.
- Every behavior change has regression or smoke coverage through bad and valid fixtures.
- Every unknown is listed under `Assumptions` or `Open Questions`, not hidden in task text.
- Rollback, abort criteria, and monitoring are specific enough for this medium-risk validator change.
- A fresh agent can execute Task 1 from this plan using the exact fixture paths without raw transcript context.

## Execution Decision
Proceed with primary-agent `plan2do` execution after this plan passes `validate_plan_contract.py --mode light`.

## Execution Handoff

- Goal: Add fail-fast review artifact contract checks to `spec2plan` and `plan2do`.
- Current state: Confirmed spec exists at `.codex/work/20260621-plan-contract-fail-fast/spec.md`; `plan.md` is the canonical implementation plan after validation.
- Authoritative artifacts: `.codex/work/20260621-plan-contract-fail-fast/spec.md`; `.codex/work/20260621-plan-contract-fail-fast/plan.md`; `spec2plan/scripts/validate_plan_contract.py`; `plan2do/scripts/compile_execution.py`; `plan2do/scripts/validate_execution.py`.
- Decisions: Use light mode; implement Python semantic checks; no new mandatory dependencies; context artifact absence is not hard failure in v1.
- Verification: Run plan validation, plan compilation, Python compile checks, bad fixture failure checks, valid fixture pass checks, review PASS, and execution validation.
- Remaining risks: Existing dirty worktree requires scoped patching; duplicated rule logic may need v2 shared schema extraction.
- Next action: Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md --mode light`.
- Suggested skills: `plan2do`, `context-engineering`, `edit-orchestration`, `test-driven-development`.
- Redactions / omitted raw data: Raw full git diff and long command output are omitted from the plan body; paths and exact commands are cited.
