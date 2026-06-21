# Spec: Plan Contract Fail-Fast

## Objective
Improve `spec2plan` and `plan2do` so agents get fast, actionable failures for invalid plan/task contracts before late execution acceptance. The primary users are the main Codex agent and future subagents executing local skill or code-change plans.

## Users
- Primary: Codex main agent executing `spec2plan -> plan2do` for local skill or code changes.
- Secondary: Codex subagents that receive plans or compiled task checklists and need deterministic handoff semantics.

## Problem
The recent `debug-skill` implementation exposed contract drift between `spec2plan` and `plan2do`: a review-role task used `artifacts/final-report.md` as its output artifact. `spec2plan` validation accepted the plan, but `plan2do` final validation later failed because review-role artifacts must contain a standalone `Verdict: PASS` or `Verdict: FAIL`. This late failure created avoidable rework and made the boundary between review artifacts and final reports unclear.

## Success Criteria
- Bad plan fixtures fail during `spec2plan` validation or `plan2do` compilation, not during final acceptance.
- Good plan fixtures still pass without false positives.
- Error messages identify the exact task number, field, broken rule, and expected repair.
- Existing validation commands for `spec2plan`, `plan2do`, and touched helper scripts pass.
- The implementation avoids new mandatory heavyweight dependencies.
- The new checks reduce late-stage review/final-report contract failures while preserving fast normal execution.

## Scope
### In
- Add high-value semantic checks to `spec2plan/scripts/validate_plan_contract.py`.
- Add fail-fast checks to `plan2do/scripts/compile_execution.py`.
- Keep `plan2do/scripts/validate_execution.py` as the final acceptance gate and align its behavior with earlier checks.
- Add or update lightweight regression fixtures/tests for invalid and valid plan/task contracts.
- Cover at least these v1 rules:
  - `Worker role: review` should output a review artifact such as `.codex/work/<date-topic>/review*.md`, or the task must explicitly state that its output artifact contains a standalone `Verdict: PASS|FAIL`.
  - Final reports and review artifacts should not be confused by default.
  - Non-trivial `plan2do` executions should either produce `context-task<N>.md` artifacts or record an explicit reviewable exemption.
- Preserve Markdown plan format and existing command-line workflows.

### Out
- Do not introduce CUE, JSON Schema, Pydantic, or another mandatory dependency in v1.
- Do not redesign the entire plan Markdown format.
- Do not automatically rewrite invalid plans.
- Do not modify unrelated skills.
- Do not implement broad schema/policy infrastructure unless a later v2 explicitly requests it.

## Requirements
### Functional
- `spec2plan` must reject review-role tasks whose `Output artifact` conflicts with the documented review artifact contract unless the task explicitly requires a standalone verdict in that artifact.
- `plan2do` compilation must reject the same invalid review-role artifact shape before task execution starts.
- Both failure paths must emit concise, actionable diagnostics.
- Valid review tasks with proper `review*.md` outputs must continue to pass.
- Valid final report tasks that are not review-role tasks must continue to pass.
- Existing final validation must continue preventing false completion.
- Context artifact requirements must be either enforced earlier or made explicitly exemptable and visible in artifacts/final reports.

### Non-Functional
- Keep validation fast enough for normal agent workflow; checks should be local Python parsing without network or new package installs.
- Keep implementation boring and easy to remove or migrate.
- Structure rule logic so future v2 schema tools can reuse or replace it without duplicating behavior.

## Constraints
- v1 must use Python semantic checks and existing scripts.
- v1 must not add required CUE, JSON Schema, Pydantic, DSPy, GEPA, or OpenAI dependencies.
- Plans remain Markdown source-of-truth.
- Preserve current `spec2plan -> plan2do` user flow and artifact locations under `.codex/work/<yyyyMMdd>-<topic>/`.
- Reuse mature project ideas where relevant:
  - `actionlint`: static semantic lint before execution.
  - `check-jsonschema`: schema-first CLI validation as a possible v2 direction.
  - `CUE`: cross-field constraint model as a possible v2 direction.
  - `pydantic`: typed shared model idea as an optional future Python-native direction.

## Assumptions To Validate
- [ ] Review-role artifact failures are the highest-value first contract drift to fix - validate with regression fixtures based on the `debug-skill` plan.
- [ ] Python semantic checks are sufficient for v1 - validate by implementing the rule without new dependencies and running fixtures.
- [ ] Context artifact enforcement can be added without excessive false positives - validate against existing completed plan workspaces or mark as explicit exemption if ambiguous.

## Risks
- False positives could block legitimate final-report review patterns - mitigate with an explicit verdict-in-artifact escape hatch and tests.
- Duplicated rules across `spec2plan` and `plan2do` could drift again - mitigate by extracting shared helper functions if the change touches more than one script.
- Context artifact rules may be underspecified - mitigate by making missing context artifacts a warning or explicit exemption in v1 if hard enforcement is too noisy.
- Overbuilding schema infrastructure would reduce efficiency - mitigate by deferring CUE/JSON Schema/Pydantic to v2.

## Acceptance Checks
- Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py <valid-plan.md> --mode light` and confirm `VALID`.
- Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py <bad-review-artifact-plan.md> --mode light` and confirm it fails with task number, field, and repair guidance.
- Run `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py <bad-review-artifact-plan.md>` and confirm it fails before writing or using execution state.
- Run `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py <valid-plan.md>` and confirm it still writes `execution/tasks.json`.
- Run focused Python compile or script self-tests for touched files.
- If fixtures are added, run their test command and record outcomes in the plan execution artifacts.

## Open Questions
- Should missing `context-task<N>.md` be a hard failure in v1, or a warning/exemption until existing plan workspaces are audited?
- Should the shared rule logic live in a new common helper module, or be duplicated minimally first and extracted only if the implementation grows?
