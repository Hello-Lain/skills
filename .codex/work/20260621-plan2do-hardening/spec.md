# Spec: plan2do Hardening

## Objective
Improve `plan2do` so primary-agent execution is more efficient and reliable by adding machine-checkable plan execution compilation, completion validation, failure policy, and review rubric.

## Users
- Primary user: the main Codex agent using `$plan2do` to execute `spec2plan` plans.
- Secondary user: local users who need visible proof that a plan was completed or stopped correctly.

## Problem
`plan2do` currently defines strong workflow rules, but completion still relies on manual self-discipline. Compared with `codex2codex`, it lacks a lightweight task IR, execution state checks, artifact validation, failure policy, and review rubric. This reduces repeatability and makes false completion harder to detect.

## Success Criteria
- `plan2do` can compile a `spec2plan` `plan.md` into `execution/tasks.json`.
- `plan2do` can validate a completed plan workspace with one command.
- Failure classes and next actions are documented in a reference file.
- Review expectations for functionality, verification, scope, architecture simplicity, and context hygiene are documented.
- `SKILL.md` and `execution-contract.md` point agents to the new scripts and references.
- New scripts are stdlib-only, deterministic, and validated with `py_compile`.
- The new validator is exercised against a passing fixture and a failing fixture.

## Scope
### In
- Add `plan2do/scripts/compile_execution.py`.
- Add `plan2do/scripts/validate_execution.py`.
- Add `plan2do/references/failure-policy.md`.
- Add `plan2do/references/review-rubric.md`.
- Update `plan2do/SKILL.md`.
- Update `plan2do/references/execution-contract.md`.
- Add execution artifacts under `.codex/work/20260621-plan2do-hardening/artifacts/`.

### Out
- Do not change `codex2codex`.
- Do not make `codex2codex` the default execution path.
- Do not add external dependencies.
- Do not create a broad workflow engine beyond the lightweight scripts.
- Do not touch unrelated dirty files.

## Requirements
### Functional
- `compile_execution.py` accepts a plan path and writes `execution/tasks.json` under the plan workspace by default.
- The compiled JSON includes task number, title, wave, worker role, dependencies, writable scope, verification, output artifact, and status.
- `validate_execution.py` validates a plan workspace and fails when required artifacts, review PASS, final report COMPLETE, or task completion evidence are missing.
- `validate_execution.py` supports a clear failing fixture outcome.
- `failure-policy.md` maps failure classes to actions.
- `review-rubric.md` defines review checks and PASS/FAIL conditions.
- `SKILL.md` instructs agents to compile execution state before non-trivial execution and run final validation before success.
- `execution-contract.md` documents the scripts in Plan Intake and Final Acceptance.

### Non-Functional
- Scripts must use only Python standard library.
- Scripts must be readable and small enough to maintain.
- Validation errors must be actionable.
- Existing artifact and context hygiene rules must remain intact.

## Constraints
- Work in `/data/lcq/.codex/skills`.
- Manual edits use `apply_patch`.
- Preserve unrelated dirty work.
- Keep raw command output out of final responses; store summaries in artifacts.

## Assumptions To Validate
- [ ] A JSON task IR is enough for v1; no YAML dependency is needed.
- [ ] Existing `spec2plan` task shape is stable enough for parser reuse.
- [ ] Review and final report artifacts can be validated with simple text contracts.

## Risks
- The scripts may duplicate some `codex2codex` logic. Mitigation: keep them lightweight and primary-agent focused.
- Validator may be too strict for tiny plans. Mitigation: allow explicit review exemption and clear errors.
- Parser may miss unusual Markdown. Mitigation: target the current `spec2plan` contract and fail closed.

## Acceptance Checks
- `python -m py_compile /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py`
- `python /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/plan.md`
- `python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py <passing-fixture-workspace>` returns `VALID`.
- `python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py <failing-fixture-workspace>` returns nonzero with actionable errors.
- `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do` returns success.

## Open Questions
None.
