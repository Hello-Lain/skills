# Spec: Skill Execution Stability Gates

## Objective
Build v1 stability gates for the Codex skill production/execution workflow so `spec2plan -> plan2do -> reviewer` can produce high-quality skill changes with fewer reviewer reruns, fewer subagent lifecycle mistakes, and less dependence on main-agent memory.

Primary outcome: before a reviewer subagent is launched, local deterministic checks should catch missing final artifacts, invalid execution state, and incomplete production reports. Production reports should support a safe two-stage lifecycle that avoids self-referential reviewer/report deadlocks.

## Users
- Primary: main Codex agent executing skill creation or material skill updates in `/data/lcq/.codex/skills`.
- Secondary: reviewer subagents performing isolated quality gates.
- Secondary: future agents using `skill-tokenless`, `spec2plan`, `plan2do`, `reviewer`, and `edit-orchestration` to maintain production-grade skills.

## Problem
Recent skill work exposed workflow instability:

- `reviewer` first caught missing final acceptance artifacts that a local readiness script should have caught before subagent launch.
- `skill-tokenless` production reports currently have a self-reference problem: reviewer wants a production report to exist, while the production report wants a reviewer verdict.
- `reviewer` subagents can misinterpret heavy mode and spawn nested reviewer subagents unless the lifecycle rules are enforced in both docs and prompts.
- Final acceptance relies on several separate validators and status files, but no single pre-review gate checks whether the workspace is ready for reviewer.
- Large skill execution workflows can waste tokens by launching reviewer too early and then requiring rework only to create missing artifacts.

## Success Criteria
- A deterministic readiness check exists and fails before reviewer launch when required final artifacts, task status, or production report fields are missing.
- Skill production reports support `draft` and `final` stages:
  - `draft` is valid before final reviewer verdict and can be reviewed.
  - `final` requires reviewer verdict, cleanup proof, and final validation evidence.
- `plan2do` uses the readiness gate before reviewer launch for plans that create or materially update skills.
- `skill-tokenless` documents and validates the two-stage production report lifecycle.
- `reviewer` lifecycle rules prevent nested reviewer subagents and define healthy-running versus abnormal subagent handling.
- Existing validators remain compatible:
  - `quick_validate.py`
  - `validate_review_report.py`
  - `validate_plan_contract.py`
  - `validate_execution.py`
  - `validate_skill_production.py`
- New or updated scripts include self-tests and failing fixtures for missing production report, missing task artifact, pending task status, and draft/final report transitions.
- Final reviewer gate returns `PASS` after focused recheck, or returns actionable `REVISE/BLOCK` with exact missing evidence.

## Scope
### In
- Add a `plan2do` readiness validator, expected name:
  - `plan2do/scripts/pre_review_ready.py`
- Integrate readiness checks into `plan2do` docs and execution contract.
- Extend `skill-tokenless/scripts/validate_skill_production.py` to support `--stage draft|final`.
- Update `skill-tokenless/references/skill-production-gate.md` to define draft/final production report lifecycle.
- Strengthen `reviewer` lifecycle docs and dispatch prompt rules:
  - already-isolated reviewer completes current packet locally;
  - no nested reviewer subagents;
  - healthy-running subagent is not canceled or archived due to elapsed time;
  - abnormal subagent diagnostic policy remains `2 x 45s`.
- Add focused fixtures or self-test cases proving readiness and report-stage behavior.
- Update `spec2plan` guidance so plans for skill work include readiness gate before final reviewer launch.
- Preserve current manual edit policy: use `apply_patch`; do not add mandatory third-party dependencies.

### Out
- Do not rewrite all skill contracts.
- Do not introduce LangGraph, Plandex, Aider, pre-commit, ast-grep, or OpenRewrite as mandatory runtime dependencies.
- Do not simulate real provider/network outages beyond documented or fixture-based status cases.
- Do not change Codex/Paseo agent manager internals.
- Do not remove existing validators or replace reviewer with a purely local validator.
- Do not modify unrelated dirty work or historical artifacts except the active implementation workspace artifacts.

## Requirements
### Functional
- Readiness gate:
  - Accepts a plan workspace path.
  - Checks `execution/tasks.json` exists and is parseable.
  - Checks required task output artifacts exist and are non-empty.
  - Checks task statuses are complete or explicitly blocked only when final status is incomplete.
  - Checks production report exists for material skill work.
  - Checks production report is valid for the requested stage.
  - Checks final report exists before final reviewer or final execution validation when required.
  - Emits concise actionable errors and exits nonzero on failure.
  - Supports `--self-test`.
- Production report lifecycle:
  - `draft` stage allows reviewer verdict to be `pending` or omitted only when reviewer has not run yet.
  - `final` stage requires reviewer verdict `PASS`, `REVISE`, or `BLOCK`.
  - `final` stage blocks `PASS` production reports if reviewer verdict is `REVISE` or `BLOCK`.
  - Both stages require Behavior Lock, Token Budget, Deterministic Validators, Scenario Gate, Reviewer Gate, Reuse Attribution, Changed Files, and Residual Risks.
  - Both stages validate local changed-file paths unless explicitly marked unavailable.
- Reviewer lifecycle:
  - Coordinator launches reviewer only after readiness gate passes or after recording a deliberate partial-review reason.
  - Reviewer subagent prompt says it is already the isolated reviewer and must not spawn nested reviewers.
  - Any nested reviewer attempt is treated as abnormal/rule violation and can be canceled/archived.
  - Healthy-running reviewer subagents continue; elapsed time alone is not a cancel/archive reason.
- Integration:
  - `plan2do` Quality Gates mention readiness gate before final reviewer launch.
  - `spec2plan` skill-work plans include a task or step for readiness validation before reviewer.
  - `skill-tokenless` production gate references the readiness check and two-stage report validation.

### Non-Functional
- Keep always-loaded `SKILL.md` changes compact; put detailed schemas and examples in references.
- Use Python stdlib only for new scripts unless a dependency already exists.
- Error output must be short enough for main-agent context.
- Scripts must be deterministic and usable without network.
- Preserve backward compatibility where possible: existing reports without explicit stage should default to final or have a clear migration error.

## Constraints
- Workspace root: `/data/lcq/.codex/skills`.
- Manual edits must use `apply_patch`.
- Existing dirty/untracked work must be preserved.
- No mandatory third-party runtime dependencies.
- Reviewer subagents must be archived after report collection and must not be canceled solely for healthy running time.
- Current date/workspace convention: `.codex/work/<yyyyMMdd>-<topic-slug>/`.

## Assumptions To Validate
- [ ] `plan2do/scripts/pre_review_ready.py` can share some validation logic with `validate_execution.py` without duplicating too much code. Validate with code inspection and self-test.
- [ ] `validate_skill_production.py --stage draft|final` can remain compatible with existing production reports. Validate against `.codex/work/20260621-skill-production-gate/artifacts/production-report.md`.
- [ ] A readiness gate before reviewer reduces one full reviewer rerun in workflows like `.codex/work/20260621-skill-production-gate/`. Validate with a fixture representing the earlier missing-artifacts state.
- [ ] Reviewer no-nested behavior is sufficiently enforced through docs and dispatch prompt text. Validate with report/fixture checks, not real runaway subagent spawning.

## Risks
- Over-gating small skill edits can waste time.
  - Mitigation: require readiness gate only for new skills, material skill updates, validator/script changes, workflow/safety changes, or metadata changes.
- Draft/final production report stages can confuse agents.
  - Mitigation: add explicit examples and validator errors that say which stage to use.
- Readiness validator may duplicate `validate_execution.py`.
  - Mitigation: keep readiness focused on pre-review completeness; keep final execution validator as final acceptance.
- Reviewer subagent lifecycle cannot be fully tested without live agent-manager behavior.
  - Mitigation: document lifecycle states and validate prompt/report text; rely on coordinator policy for real cancellation/archival.

## Acceptance Checks
- `python3 plan2do/scripts/pre_review_ready.py --self-test`
- `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-production-gate --stage final`
- `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`
- `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-production-gate/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`
- `python3 reviewer/scripts/validate_review_report.py --self-test`
- `python3 spec2plan/scripts/validate_plan_contract.py <new-plan.md> --mode light`
- `python3 plan2do/scripts/validate_execution.py <new-workspace>`
- `for d in skill-tokenless reviewer plan2do spec2plan; do python3 .system/skill-creator/scripts/quick_validate.py "$d"; done`
- Reviewer gate on the implementation result returns `PASS` or produces actionable rework that is completed within the bounded rework policy.

## Open Questions
- None for v1.
