# Plan: Harden plan2do Execution Validation

Mode: light
Risk level: Medium
Confidence: High

## Goal
Add lightweight machine-checkable execution compilation, final validation, failure policy, and review rubric to `plan2do` so primary-agent plan execution becomes more repeatable and less dependent on manual judgment.

## Non-Goals
- Do not modify `codex2codex`.
- Do not change `plan2do` default mode away from primary-agent execution.
- Do not add external dependencies.
- Do not touch unrelated dirty files.

## Evidence Inspected
- `/data/lcq/.codex/skills/plan2do/SKILL.md`
- `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- `/data/lcq/.codex/skills/codex2codex/SKILL.md`
- `/data/lcq/.codex/skills/codex2codex/scripts/plan_to_tasks.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/validate_execution_complete.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/validate_result_contract.py`
- `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/spec.md`

## Spec Summary
The spec requires adding two stdlib scripts and two reference files, then linking them from `SKILL.md` and `execution-contract.md`. The new scripts must compile a `spec2plan` plan to a JSON execution IR and validate completion artifacts.

## Domain Language Check
- Use `execution/tasks.json` for the primary-agent execution IR.
- Use `COMPLETE` and `INCOMPLETE` final status from `plan2do`.
- Use `Verdict: PASS` and `Verdict: FAIL` for review artifacts.
- Use failure classes from `plan2do` and extend them only in `failure-policy.md`.

## Current Context
`plan2do` currently has `SKILL.md`, `agents/openai.yaml`, and `references/execution-contract.md`. It does not yet have scripts. Existing unrelated dirty files are outside the writable scope and must not be touched.

## Implementation Map
- Files: `/data/lcq/.codex/skills/plan2do/scripts/compile_execution.py`; `/data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`; `/data/lcq/.codex/skills/plan2do/references/failure-policy.md`; `/data/lcq/.codex/skills/plan2do/references/review-rubric.md`; `/data/lcq/.codex/skills/plan2do/SKILL.md`; `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`.
- Symbols / APIs: `compile_plan`, `parse_tasks`, `write_execution_state`, `validate_workspace`, `review_verdict`, CLI `main`.
- Tests: `py_compile`; compile this plan; validate a passing fixture; validate a failing fixture; `quick_validate.py`.
- Commands: `python -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`; `python /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/plan.md`; `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`.
- Data / migration impact: Not applicable because this adds local skill files and generated test artifacts only.

## Assumptions
- The current `spec2plan` task field names remain stable.
- A review artifact named `artifacts/review.md` or a task output review artifact with `Verdict: PASS` is sufficient for v1.
- Tiny plans can set a documented review exemption in final report, but this hardening plan requires review.

## User Inputs Needed
None.

## Proposed Approach
Implement the smallest useful primary-agent execution IR and validator. Keep scripts standalone and stdlib-only. Add reference docs instead of bloating `SKILL.md`. Validate on both success and failure fixtures before final acceptance.

## Scenario Probes
- Valid `plan.md` compiles to `execution/tasks.json`.
- Missing review or missing final report makes validation fail.
- Final report with `Status: COMPLETE`, review `Verdict: PASS`, and complete task artifacts makes validation pass.
- Invalid task artifacts produce actionable errors.
- `SKILL.md` remains concise and points to scripts/references.

## Dependency Graph
- Task 1 creates scripts and references.
- Task 2 updates `SKILL.md` and `execution-contract.md`.
- Task 3 validates scripts and skill metadata.
- Task 4 creates passing/failing fixtures and validates behavior.
- Task 5 reviews quality and applies bounded rework if needed.

## Task Breakdown
### Task 1: Add execution compiler and validator

- Description: Add stdlib-only scripts for compiling a plan to `execution/tasks.json` and validating completion artifacts.
- Worker role: coding
- Wave: 1
- Acceptance criteria: Both scripts exist, parse CLI args, fail closed on missing files, and are readable by `py_compile`.
- Verification: `python -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`
- Concrete edits: Create `/data/lcq/.codex/skills/plan2do/scripts/compile_execution.py` and `/data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`.
- Interfaces / contracts changed: New CLI scripts under `plan2do/scripts/`.
- Test cases: `py_compile`, passing fixture execution, and failing fixture execution in Task 4.
- Pre-check commands: `test ! -e /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py && test ! -e /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`
- Post-check commands: `python -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`
- Dependencies: None.
- Files likely touched: `/data/lcq/.codex/skills/plan2do/scripts/compile_execution.py`; `/data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`
- Writable scope: `/data/lcq/.codex/skills/plan2do/scripts/`
- Output artifact: `.codex/work/20260621-plan2do-hardening/artifacts/task1-scripts.md`
- Estimated scope: M

### Task 2: Add failure and review references

- Description: Add compact references for failure handling and review PASS/FAIL rubric.
- Worker role: coding
- Wave: 2
- Acceptance criteria: References exist and define failure classes, next actions, review checks, and PASS/FAIL conditions.
- Verification: `rg "VERIFY_FAILED|REVIEW_FAILED|SCOPE_VIOLATION|Verdict: PASS|Verdict: FAIL|over-engineering" /data/lcq/.codex/skills/plan2do/references`
- Concrete edits: Create `/data/lcq/.codex/skills/plan2do/references/failure-policy.md` and `/data/lcq/.codex/skills/plan2do/references/review-rubric.md`.
- Interfaces / contracts changed: New references loaded by `plan2do`.
- Test cases: Grep for required failure and review terms.
- Pre-check commands: `test ! -e /data/lcq/.codex/skills/plan2do/references/failure-policy.md && test ! -e /data/lcq/.codex/skills/plan2do/references/review-rubric.md`
- Post-check commands: `rg "VERIFY_FAILED|REVIEW_FAILED|SCOPE_VIOLATION|Verdict: PASS|Verdict: FAIL|over-engineering" /data/lcq/.codex/skills/plan2do/references`
- Dependencies: None.
- Files likely touched: `/data/lcq/.codex/skills/plan2do/references/failure-policy.md`; `/data/lcq/.codex/skills/plan2do/references/review-rubric.md`
- Writable scope: `/data/lcq/.codex/skills/plan2do/references/`
- Output artifact: `.codex/work/20260621-plan2do-hardening/artifacts/task2-references.md`
- Estimated scope: S

### Task 3: Link scripts and references from skill docs

- Description: Update `SKILL.md` and `execution-contract.md` so future agents use compile/validate scripts and references.
- Worker role: coding
- Wave: 3
- Acceptance criteria: `SKILL.md` mentions the scripts and references; `execution-contract.md` requires compile before non-trivial execution and validate before final success.
- Verification: `rg "compile_execution.py|validate_execution.py|failure-policy.md|review-rubric.md|execution/tasks.json" /data/lcq/.codex/skills/plan2do/SKILL.md /data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- Concrete edits: Patch `/data/lcq/.codex/skills/plan2do/SKILL.md` and `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`.
- Interfaces / contracts changed: `plan2do` workflow now includes machine-checkable compile and validate steps.
- Test cases: Grep confirms references.
- Pre-check commands: `test -f /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py && test -f /data/lcq/.codex/skills/plan2do/references/failure-policy.md`
- Post-check commands: `rg "compile_execution.py|validate_execution.py|failure-policy.md|review-rubric.md|execution/tasks.json" /data/lcq/.codex/skills/plan2do/SKILL.md /data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- Dependencies: Tasks 1 and 2.
- Files likely touched: `/data/lcq/.codex/skills/plan2do/SKILL.md`; `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- Writable scope: `/data/lcq/.codex/skills/plan2do/SKILL.md`; `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- Output artifact: `.codex/work/20260621-plan2do-hardening/artifacts/task3-doc-links.md`
- Estimated scope: S

### Task 4: Validate behavior with passing and failing fixtures

- Description: Compile this hardening plan and test `validate_execution.py` against a passing fixture and a failing fixture.
- Worker role: coding
- Wave: 4
- Acceptance criteria: Compile command writes `execution/tasks.json`; passing fixture returns `VALID`; failing fixture returns nonzero with actionable errors.
- Verification: `python /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/plan.md && python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/pass-fixture`
- Concrete edits: Create fixture artifacts under `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/`.
- Interfaces / contracts changed: None.
- Test cases: Passing fixture and failing fixture.
- Pre-check commands: `python -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`
- Post-check commands: `python /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/plan.md && python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/pass-fixture`
- Dependencies: Task 3.
- Files likely touched: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/`
- Writable scope: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/`
- Output artifact: `.codex/work/20260621-plan2do-hardening/artifacts/task4-validation.md`
- Estimated scope: M

### Task 5: Review and final acceptance

- Description: Review the hardening changes against the spec and run final validation.
- Worker role: review
- Wave: 5
- Acceptance criteria: Review artifact has `Verdict: PASS`; final report has `Status: COMPLETE`; all validation commands pass.
- Verification: `rg "Verdict: PASS" /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/review.md && rg "Status: COMPLETE" /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/final-report.md`
- Concrete edits: Write `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/review.md` and `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/final-report.md`.
- Interfaces / contracts changed: None.
- Test cases: Manual review plus final grep.
- Pre-check commands: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`
- Post-check commands: `rg "Verdict: PASS" /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/review.md && rg "Status: COMPLETE" /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/final-report.md`
- Dependencies: Task 4.
- Files likely touched: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/review.md`; `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/final-report.md`
- Writable scope: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/review.md`; `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/`
- Output artifact: `.codex/work/20260621-plan2do-hardening/review.md`
- Estimated scope: S

## Step-by-Step Plan
1. Create `/data/lcq/.codex/skills/plan2do/scripts/compile_execution.py` and `/data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`.
2. Run `python -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`.
3. Create `/data/lcq/.codex/skills/plan2do/references/failure-policy.md` and `/data/lcq/.codex/skills/plan2do/references/review-rubric.md`.
4. Patch `/data/lcq/.codex/skills/plan2do/SKILL.md` and `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`.
5. Run `python /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/plan.md`.
6. Create pass/fail fixture workspaces under `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/`.
7. Run `python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/pass-fixture`.
8. Run `python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/fail-fixture` and confirm it returns nonzero.
9. Run `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`.
10. Write `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/review.md` and `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/final-report.md`.

## Parallelization
Wave 1 and Wave 2 can run in parallel because scripts and references have disjoint writable scopes. Wave 3 depends on both. Wave 4 depends on Wave 3. Wave 5 depends on Wave 4.

## Files / Components Likely Affected
- `/data/lcq/.codex/skills/plan2do/scripts/compile_execution.py`
- `/data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`
- `/data/lcq/.codex/skills/plan2do/references/failure-policy.md`
- `/data/lcq/.codex/skills/plan2do/references/review-rubric.md`
- `/data/lcq/.codex/skills/plan2do/SKILL.md`
- `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/`
- `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/review.md`

## Owners / Responsibilities
- coding: implement scripts, references, docs, fixtures, and validation.
- review: verify quality, scope, simplicity, and acceptance.
- primary agent: use `plan2do` final acceptance and write rework guidance before fixes if review fails.

## Validation Plan
- `python /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/plan.md --mode light`
- `python -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`
- `python /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/plan.md`
- `python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/pass-fixture`
- `python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/artifacts/fail-fixture` must fail.
- `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`

## Rollout Plan
Keep changes local in `plan2do`. Use the new compile/validate scripts on future `plan2do` executions before final success.

## Monitoring / Observability
Record context packs, task execution summaries, validation results, review, rework guidance if any, and final report under `.codex/work/20260621-plan2do-hardening/artifacts/`.

## Documentation / ADR Updates
ADR: Not needed. The skill-local references and scripts document the new behavior.

## Rollback / Recovery Plan
Remove only the new files under `/data/lcq/.codex/skills/plan2do/scripts/`, the two new reference files, and the related doc link patches if validation cannot pass. Preserve unrelated dirty files.

## Abort Criteria
- Abort if any edit would touch files outside declared writable scope.
- Abort if scripts need non-stdlib dependencies.
- Abort if `quick_validate.py` fails after one focused rework cycle.
- Abort if validator cannot produce actionable errors for the failing fixture.

## Risks
- Parser may be too narrow for unusual plan Markdown. Mitigation: fail closed with actionable errors.
- Validator may be too strict for tiny plans. Mitigation: allow explicit review exemption in final report while requiring artifacts.
- Duplication with `codex2codex` may grow. Mitigation: keep scripts primary-agent focused and simple.

## Open Questions
None.

## Plan Self-Review
- writable scope is exact and same-wave implementation tasks do not overlap.
- coverage includes compile, passing fixture, failing fixture, skill validation, and review.
- unknown handling is explicit in `Assumptions` and `Open Questions`.
- rollback and abort criteria are specific for this medium-risk local skill hardening.
- Task 1 can be executed by a fresh agent from this plan without raw transcript context.

## Execution Decision
Ready to execute with `plan2do` primary-agent mode.

## Execution Handoff

- Goal: Harden `plan2do` with lightweight machine-checkable execution compilation and completion validation.
- Current state: Spec and plan are saved under `.codex/work/20260621-plan2do-hardening/`.
- Authoritative artifacts: `.codex/work/20260621-plan2do-hardening/spec.md`; `.codex/work/20260621-plan2do-hardening/plan.md`
- Decisions: Use primary-agent `plan2do` mode; do not use `codex2codex` unless explicitly requested.
- Verification: Run the commands in `Validation Plan`.
- Remaining risks: Parser narrowness and validator strictness.
- Next action: Execute Task 1 and Task 2.
- Suggested skills: plan2do; context-engineering; apply-patch; skill-creator.
- Redactions / omitted raw data: Raw command output and diffs should be summarized in artifacts.
