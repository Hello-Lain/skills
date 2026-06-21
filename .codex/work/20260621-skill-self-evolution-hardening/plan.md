# Skill Self-Evolution Hardening Plan

- Mode: light
- Risk level: Medium
- Confidence: High

## Goal
Implement `.codex/work/20260621-skill-self-evolution-hardening/spec.md` end-to-end: harden reviewer path evidence, fix skill-production validator parsing, clarify pre-review readiness, add `debug-skill` trace/deep-audit protocol, then pass production and reviewer gates.

## Non-Goals
- Do not add Hermes, DSPy, GEPA, SessionDB, Darwinian Evolver, or runtime dependencies.
- Do not enable autonomous `debug-skill` edits, commits, deploys, or private session mining.
- Do not rewrite unrelated skills or modify `.codex/work/20260621-reviewer-lite-gate/` evidence.

## Evidence Inspected
- `.codex/work/20260621-skill-self-evolution-hardening/spec.md`
- `.codex/work/20260621-skill-self-evolution-hardening/review.md`
- `.codex/work/20260621-skill-self-evolution-hardening/manifest.yaml`
- `.codex/work/20260621-reviewer-lite-gate/` preserved as prior evidence workspace.
- `reviewer/SKILL.md`
- `reviewer/references/subagent-dispatch.md`
- `reviewer/references/review-report-template.md`
- `reviewer/references/lite-gate-integration.md`
- `spec2plan/SKILL.md`
- `spec2plan/references/plan-contract.md`
- `spec2plan/references/artifact-contract.md`
- `plan2do/SKILL.md`
- `plan2do/references/execution-contract.md`
- `plan2do/references/review-rubric.md`
- `plan2do/references/failure-policy.md`
- `plan2do/scripts/pre_review_ready.py`
- `skill-tokenless/SKILL.md`
- `skill-tokenless/references/testing.md`
- `skill-tokenless/references/validation.md`
- `skill-tokenless/references/skill-production-gate.md`
- `skill-tokenless/scripts/validate_skill_production.py`
- `debug-skill/SKILL.md`
- `debug-skill/references/hermes-reuse.md`
- `debug-skill/references/report-template.md`
- `debug-skill/scripts/skill_audit_core.py`
- `edit-orchestration/references/route-matrix.md`
- `edit-orchestration/references/apply-patch.md`
- CodeGraph index status for `/data/lcq/.codex/skills`

## Spec Summary
The spec requires four fixes: reviewer packets must avoid cwd/root confusion, readiness docs must prevent pending non-review finalization before reviewer launch, production-report validation must parse explicit outcomes instead of command text, and `debug-skill` must separate lightweight trace capture from deep audit while adapting Hermes protocol fields safely.

## Domain Language Check
- Canonical terms: `reviewer`, `spec2plan`, `plan2do`, `skill-tokenless`, `debug-skill`, `Skill Production Gate`, `pre-review readiness`, `draft`, `final`, `trace mode`, `deep audit mode`, `promotion gates`.
- No term conflict found between the spec, skill contracts, and scripts.

## Current Context
- Repo root: `/data/lcq/.codex/skills`.
- Dirty worktree before this plan: existing user edits in `idea-refine/SKILL.md`, `interview-me/SKILL.md`, `plan2do/SKILL.md`, `reviewer/SKILL.md`, `spec2plan/SKILL.md`; untracked `.codex/work/20260621-reviewer-lite-gate/`, `.codex/work/20260621-skill-self-evolution-hardening/`, and `reviewer/references/lite-gate-integration.md`.
- Scope policy: preserve existing dirty files unless a listed task names them in writable scope.
- Execution mode: primary-agent `plan2do`; no `codex2codex` requested.

## Implementation Map
- Files: `reviewer/references/subagent-dispatch.md` for path packet/check requirements; `spec2plan/references/plan-contract.md` for plan author readiness warning; `plan2do/references/execution-contract.md` for executor readiness contract; `skill-tokenless/scripts/validate_skill_production.py` for explicit validator outcome parsing; `debug-skill/SKILL.md`, `debug-skill/references/hermes-reuse.md`, `debug-skill/references/report-template.md`, `debug-skill/scripts/skill_audit_core.py` for trace/deep-audit protocol; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/*` for execution evidence.
- Symbols / APIs: `validate_report`, `run_self_test`, helper parser for deterministic validator outcomes, `validate_workspace`, `SkillAuditExample`, `SkillAuditDataset`, `ConstraintResult`, `FitnessScore`, `CandidateScore`, `build_report_skeleton`, new trace skeleton helper.
- Tests: `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`, `python3 plan2do/scripts/pre_review_ready.py --self-test`, `python3 debug-skill/scripts/skill_audit_core.py --self-test`, `python3 reviewer/scripts/validate_review_report.py <review-report>`, `python3 .system/skill-creator/scripts/quick_validate.py <skill-dir>`, `git diff --check -- reviewer spec2plan plan2do skill-tokenless debug-skill .codex/work/20260621-skill-self-evolution-hardening`.
- Commands: `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-self-evolution-hardening/plan.md --mode light`, `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-skill-self-evolution-hardening/plan.md`, `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-self-evolution-hardening --stage draft --require-production-report --require-final-report`, `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`, `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`, `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-self-evolution-hardening`.
- Data / migration impact: Not applicable; no app data, schemas, credentials, or migrations touched.

## Assumptions
- `pre_review_ready.py` already blocks pending non-review tasks; execution will verify with `python3 plan2do/scripts/pre_review_ready.py --self-test`.
- Reviewer path hardening can be validated through dispatch contract text plus a scenario artifact because reviewer dispatch has no dedicated executable fixture script.
- Existing dirty `SKILL.md` files outside this plan are user work and remain untouched unless the task scope explicitly names them.

## User Inputs Needed
- None; the spec review passed and the user requested implementation with named skills.

## Proposed Approach
Use light `spec2plan` because the spec is reviewed, scope is bounded to named files, and execution is requested in the same turn. Execute in primary-agent `plan2do` order: docs contracts first, validator/script fixes second, debug protocol third, production/readiness artifacts fourth, final reviewer gate last.

## Scenario Probes
- Reviewer path probe: create `.codex/work/20260621-skill-self-evolution-hardening/artifacts/reviewer-path-scenario.md` showing a packet with cwd-relative path, absolute path, `pwd`, and existence-check evidence before any missing-artifact finding.
- Pre-review readiness probe: run `python3 plan2do/scripts/pre_review_ready.py --self-test`; confirm its pending non-review fixture fails draft readiness while a pending review task is allowed.
- Validator parsing probe: run `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`; include a case where a command string contains `BLOCK` and the explicit outcome is `PASS`.
- Debug trace probe: run `python3 debug-skill/scripts/skill_audit_core.py --self-test`; generate a trace skeleton artifact with trigger, loaded skills, decisions, actions, failures, recovery, validators, outcome, and optimization hints.

## Dependency Graph
- Task 1 -> Task 5: reviewer path contract and scenario feed production report evidence.
- Task 2 -> Task 5: readiness contract and self-test evidence feed production report.
- Task 3 -> Task 5: production validator must pass before production report can validate.
- Task 4 -> Task 5: debug protocol and helper self-test feed production report.
- Tasks 1-4 -> Task 5 -> Task 6: all non-review work must complete before draft readiness and final reviewer launch.

## Task Breakdown
### Task 1: Harden reviewer path dispatch

- Description: Update reviewer dispatch guidance and write a scenario artifact proving local artifacts are checked with cwd-relative and absolute path evidence before a missing-artifact finding.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `reviewer/references/subagent-dispatch.md` requires coordinator cwd, cwd-relative path, absolute path, existence evidence, `pwd`, and checked path citation in missing-artifact findings; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/reviewer-path-scenario.md` records the scenario.
- Verification: `rg -n "cwd-relative|absolute|pwd|existence|missing" reviewer/references/subagent-dispatch.md .codex/work/20260621-skill-self-evolution-hardening/artifacts/reviewer-path-scenario.md`
- Concrete edits: Patch `reviewer/references/subagent-dispatch.md`; add `.codex/work/20260621-skill-self-evolution-hardening/artifacts/reviewer-path-scenario.md`.
- Interfaces / contracts changed: Reviewer subagent packet contract now carries cwd/path evidence for local artifacts.
- Test cases: Manual scenario artifact covers false missing-artifact prevention with both path forms.
- Pre-check commands: `sed -n '1,130p' reviewer/references/subagent-dispatch.md`
- Post-check commands: `rg -n "cwd-relative|absolute|pwd|existence|missing" reviewer/references/subagent-dispatch.md .codex/work/20260621-skill-self-evolution-hardening/artifacts/reviewer-path-scenario.md`
- Dependencies: None.
- Files likely touched: `reviewer/references/subagent-dispatch.md`, `.codex/work/20260621-skill-self-evolution-hardening/artifacts/reviewer-path-scenario.md`
- Writable scope: `reviewer/references/subagent-dispatch.md`; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/reviewer-path-scenario.md`
- Output artifact: `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task1-reviewer-path-hardening.md`
- Estimated scope: S

### Task 2: Clarify pre-review readiness contracts

- Description: Update planning and execution contracts so draft readiness allows pending review tasks only, and coordinator final acceptance after reviewer is not modeled as a pending non-review task before reviewer launch.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `spec2plan/references/plan-contract.md` warns plan authors against pending non-review finalization tasks before draft readiness; `plan2do/references/execution-contract.md` states coordinator finalization after reviewer is acceptance work, not a pending non-review task before reviewer launch; self-test demonstrates pending non-review tasks block draft readiness.
- Verification: `python3 plan2do/scripts/pre_review_ready.py --self-test`
- Concrete edits: Patch `spec2plan/references/plan-contract.md` and `plan2do/references/execution-contract.md` only.
- Interfaces / contracts changed: Planning and execution contracts for skill-production reviewer readiness.
- Test cases: Existing `pre_review_ready.py --self-test` pending non-review task case.
- Pre-check commands: `sed -n '1,180p' spec2plan/references/plan-contract.md && sed -n '1,190p' plan2do/references/execution-contract.md`
- Post-check commands: `python3 plan2do/scripts/pre_review_ready.py --self-test`
- Dependencies: None.
- Files likely touched: `spec2plan/references/plan-contract.md`, `plan2do/references/execution-contract.md`
- Writable scope: `spec2plan/references/plan-contract.md`; `plan2do/references/execution-contract.md`
- Output artifact: `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task2-readiness-modeling.md`
- Estimated scope: S

### Task 3: Fix production validator outcome parsing

- Description: Change `skill-tokenless` production-report validator to parse deterministic validator outcomes from explicit result positions and add self-test regressions for command strings containing status tokens.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `validate_report` treats ``rg -n "PASS|REVISE|BLOCK" ...`: PASS`` as PASS; an explicit `: BLOCK` outcome still blocks a PASS production report; self-test passes.
- Verification: `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`
- Concrete edits: Patch `skill-tokenless/scripts/validate_skill_production.py` with a structural outcome parser and self-test cases.
- Interfaces / contracts changed: Deterministic Validators section parsing in Skill Production Gate report validation.
- Test cases: False-positive command-token case and explicit `: BLOCK` negative case.
- Pre-check commands: `sed -n '1,260p' skill-tokenless/scripts/validate_skill_production.py`
- Post-check commands: `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`
- Dependencies: None.
- Files likely touched: `skill-tokenless/scripts/validate_skill_production.py`
- Writable scope: `skill-tokenless/scripts/validate_skill_production.py`
- Output artifact: `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task3-production-validator.md`
- Estimated scope: S

### Task 4: Add debug-skill trace and audit protocol

- Description: Document lightweight trace mode and deep audit mode, add Hermes-inspired protocol fields, and expose a deterministic trace skeleton helper.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `debug-skill/SKILL.md` names trace mode and deep audit mode; `debug-skill/references/report-template.md` and `debug-skill/references/hermes-reuse.md` include trace fields, constraint gates, fitness dimensions, candidate improvements, promotion gates, redaction, and human approval; `skill_audit_core.py --self-test` covers the trace skeleton.
- Verification: `python3 debug-skill/scripts/skill_audit_core.py --self-test`
- Concrete edits: Patch `debug-skill/SKILL.md`, `debug-skill/references/report-template.md`, `debug-skill/references/hermes-reuse.md`, and `debug-skill/scripts/skill_audit_core.py`.
- Interfaces / contracts changed: `debug-skill` audit contract and helper CLI add trace/deep-audit split; no auto-modification behavior added.
- Test cases: Helper self-test asserts trace skeleton contains required trace and approval fields.
- Pre-check commands: `sed -n '1,140p' debug-skill/SKILL.md && sed -n '1,140p' debug-skill/references/report-template.md && sed -n '1,120p' debug-skill/references/hermes-reuse.md && python3 debug-skill/scripts/skill_audit_core.py --self-test`
- Post-check commands: `python3 debug-skill/scripts/skill_audit_core.py --self-test`
- Dependencies: None.
- Files likely touched: `debug-skill/SKILL.md`, `debug-skill/references/report-template.md`, `debug-skill/references/hermes-reuse.md`, `debug-skill/scripts/skill_audit_core.py`
- Writable scope: `debug-skill/SKILL.md`; `debug-skill/references/report-template.md`; `debug-skill/references/hermes-reuse.md`; `debug-skill/scripts/skill_audit_core.py`
- Output artifact: `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task4-debug-skill-protocol.md`
- Estimated scope: M

### Task 5: Validate and draft production gate

- Description: Run focused validators, write execution artifacts, write draft final report, and validate the Skill Production Gate draft before reviewer launch.
- Worker role: coding
- Wave: 3
- Acceptance criteria: changed skill directories pass `quick_validate.py`; changed script self-tests pass; `git diff --check` passes; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md` validates with `--stage draft`; draft pre-review readiness passes with only review task pending.
- Verification: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft && python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-self-evolution-hardening --stage draft --require-production-report --require-final-report`
- Concrete edits: Add task execution artifacts, verification artifact, `artifacts/production-report.md`, and `artifacts/final-report.md` draft under `.codex/work/20260621-skill-self-evolution-hardening/`.
- Interfaces / contracts changed: No code contract; production readiness artifacts become reviewer input.
- Test cases: `quick_validate.py`, script self-tests, production report draft validation, draft readiness validation.
- Pre-check commands: `git status --short`
- Post-check commands: `python3 .system/skill-creator/scripts/quick_validate.py reviewer && python3 .system/skill-creator/scripts/quick_validate.py debug-skill && python3 .system/skill-creator/scripts/quick_validate.py spec2plan && python3 .system/skill-creator/scripts/quick_validate.py plan2do && python3 .system/skill-creator/scripts/quick_validate.py skill-tokenless && python3 skill-tokenless/scripts/validate_skill_production.py --self-test && python3 plan2do/scripts/pre_review_ready.py --self-test && python3 debug-skill/scripts/skill_audit_core.py --self-test && git diff --check -- reviewer spec2plan plan2do skill-tokenless debug-skill .codex/work/20260621-skill-self-evolution-hardening && python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft && python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-self-evolution-hardening --stage draft --require-production-report --require-final-report`
- Dependencies: Task 1, Task 2, Task 3, Task 4.
- Files likely touched: `.codex/work/20260621-skill-self-evolution-hardening/artifacts/context-wave1.md`, `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task1-reviewer-path-hardening.md`, `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task2-readiness-modeling.md`, `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task3-production-validator.md`, `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task4-debug-skill-protocol.md`, `.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md`, `.codex/work/20260621-skill-self-evolution-hardening/artifacts/final-report.md`
- Writable scope: `.codex/work/20260621-skill-self-evolution-hardening/artifacts/context-wave1.md`; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task1-reviewer-path-hardening.md`; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task2-readiness-modeling.md`; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task3-production-validator.md`; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task4-debug-skill-protocol.md`; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md`; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/final-report.md`
- Output artifact: `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task5-production-gate-draft.md`
- Estimated scope: M

### Task 6: Final reviewer and acceptance gate

- Description: Run reviewer gate, save a machine-valid review report, update production/final reports, then validate final execution state.
- Worker role: review
- Wave: 4
- Acceptance criteria: reviewer report validates with `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-skill-self-evolution-hardening/review-final.md`; reviewer verdict is `PASS`; production report validates with `--stage final`; final pre-review readiness and execution validation pass.
- Verification: `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-skill-self-evolution-hardening/review-final.md && python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final && python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-self-evolution-hardening --stage final --require-production-report --require-final-report && python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-self-evolution-hardening`
- Concrete edits: Add `.codex/work/20260621-skill-self-evolution-hardening/review-final.md`; update `.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md`, `.codex/work/20260621-skill-self-evolution-hardening/artifacts/final-report.md`, and execution status.
- Interfaces / contracts changed: No code contract; final acceptance artifacts close the plan.
- Test cases: Reviewer report validation, Skill Production Gate final validation, pre-review final validation, execution validation.
- Pre-check commands: `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-self-evolution-hardening --stage draft --require-production-report --require-final-report`
- Post-check commands: `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-skill-self-evolution-hardening/review-final.md && python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final && python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-self-evolution-hardening --stage final --require-production-report --require-final-report && python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-self-evolution-hardening`
- Dependencies: Task 5.
- Files likely touched: `.codex/work/20260621-skill-self-evolution-hardening/review-final.md`, `.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md`, `.codex/work/20260621-skill-self-evolution-hardening/artifacts/final-report.md`, `.codex/work/20260621-skill-self-evolution-hardening/execution/tasks.json`
- Writable scope: `.codex/work/20260621-skill-self-evolution-hardening/review-final.md`; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md`; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/final-report.md`; `.codex/work/20260621-skill-self-evolution-hardening/execution/tasks.json`
- Output artifact: `.codex/work/20260621-skill-self-evolution-hardening/review-final.md`
- Estimated scope: M

## Step-by-Step Plan
1. Run `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-self-evolution-hardening/plan.md --mode light` and patch `.codex/work/20260621-skill-self-evolution-hardening/plan.md` until valid.
2. Run `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-skill-self-evolution-hardening/plan.md` to create `.codex/work/20260621-skill-self-evolution-hardening/execution/tasks.json`.
3. Write `.codex/work/20260621-skill-self-evolution-hardening/artifacts/context-wave1.md` with user goal, plan path, source contracts, dirty-tree constraints, and writable scopes.
4. Patch `reviewer/references/subagent-dispatch.md` with cwd-relative, absolute path, `pwd`, existence check, and checked-path citation requirements.
5. Add `.codex/work/20260621-skill-self-evolution-hardening/artifacts/reviewer-path-scenario.md` with the false-missing-artifact prevention scenario.
6. Write `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task1-reviewer-path-hardening.md` with changed file, scenario result, and `rg` verification outcome.
7. Patch `spec2plan/references/plan-contract.md` with the draft-readiness rule that only review tasks may remain pending before reviewer launch.
8. Patch `plan2do/references/execution-contract.md` with the coordinator-finalization rule for reviewer completion and final acceptance.
9. Run `python3 plan2do/scripts/pre_review_ready.py --self-test` and record the output in `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task2-readiness-modeling.md`.
10. Patch `skill-tokenless/scripts/validate_skill_production.py` with explicit deterministic validator outcome parsing and two self-test cases.
11. Run `python3 skill-tokenless/scripts/validate_skill_production.py --self-test` and record the output in `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task3-production-validator.md`.
12. Patch `debug-skill/SKILL.md` to route between `trace` and `deep audit` modes while preserving no-auto-modification.
13. Patch `debug-skill/references/report-template.md` and `debug-skill/references/hermes-reuse.md` with trace fields, constraints, fitness, candidates, promotion gates, redaction, and human approval fields.
14. Patch `debug-skill/scripts/skill_audit_core.py` with `build_trace_skeleton`, CLI support, and self-test assertions.
15. Run `python3 debug-skill/scripts/skill_audit_core.py --self-test` and write `.codex/work/20260621-skill-self-evolution-hardening/artifacts/debug-skill-trace-probe.md`.
16. Write task artifacts `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task4-debug-skill-protocol.md` and `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task5-production-gate-draft.md`.
17. Run quick validators: `python3 .system/skill-creator/scripts/quick_validate.py reviewer`, `debug-skill`, `spec2plan`, `plan2do`, and `skill-tokenless`.
18. Run `git diff --check -- reviewer spec2plan plan2do skill-tokenless debug-skill .codex/work/20260621-skill-self-evolution-hardening`.
19. Write `.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md` with draft Reviewer Gate `PENDING` and reuse attribution.
20. Write `.codex/work/20260621-skill-self-evolution-hardening/artifacts/final-report.md` draft with `Status: INCOMPLETE` and verification lines.
21. Mark Tasks 1-5 complete in `.codex/work/20260621-skill-self-evolution-hardening/execution/tasks.json`; leave Task 6 pending review.
22. Run `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`.
23. Run `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-self-evolution-hardening --stage draft --require-production-report --require-final-report`.
24. Launch or perform reviewer gate for `.codex/work/20260621-skill-self-evolution-hardening/review-final.md` using `reviewer` report template and source evidence.
25. Run `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-skill-self-evolution-hardening/review-final.md`.
26. Update `.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md` with reviewer verdict and cleanup status.
27. Update `.codex/work/20260621-skill-self-evolution-hardening/artifacts/final-report.md` to `Status: COMPLETE` when final validators pass.
28. Mark Task 6 complete in `.codex/work/20260621-skill-self-evolution-hardening/execution/tasks.json`.
29. Run final checks: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`, `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-self-evolution-hardening --stage final --require-production-report --require-final-report`, and `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-self-evolution-hardening`.

## Parallelization
- Wave 1 tasks can run in parallel because Task 1 writes `reviewer/references/subagent-dispatch.md` and scenario artifacts while Task 2 writes `spec2plan/references/plan-contract.md` and `plan2do/references/execution-contract.md`.
- Wave 2 tasks can run in parallel after Wave 1 because Task 3 writes only `skill-tokenless/scripts/validate_skill_production.py` and Task 4 writes only `debug-skill/*`.
- Wave 3 must run after Tasks 1-4 because production report evidence depends on all non-review work.
- Wave 4 must run after draft readiness because final reviewer gate requires complete non-review evidence.

## Files / Components Likely Affected
- `reviewer/references/subagent-dispatch.md`
- `spec2plan/references/plan-contract.md`
- `plan2do/references/execution-contract.md`
- `skill-tokenless/scripts/validate_skill_production.py`
- `debug-skill/SKILL.md`
- `debug-skill/references/hermes-reuse.md`
- `debug-skill/references/report-template.md`
- `debug-skill/scripts/skill_audit_core.py`
- `.codex/work/20260621-skill-self-evolution-hardening/plan.md`
- `.codex/work/20260621-skill-self-evolution-hardening/execution/tasks.json`
- `.codex/work/20260621-skill-self-evolution-hardening/artifacts/`
- `.codex/work/20260621-skill-self-evolution-hardening/review-final.md`

## Owners / Responsibilities
- Primary agent: execute Tasks 1-5, maintain artifacts, run validators, preserve user dirty work, and coordinate final acceptance.
- Reviewer: perform final evidence-based review in Task 6 and return `PASS`, `REVISE`, or `BLOCK`.
- User: only needed if reviewer returns a product/safety decision that cannot be resolved from source evidence.

## Validation Plan
- Plan validation: `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-self-evolution-hardening/plan.md --mode light`.
- Execution compile: `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-skill-self-evolution-hardening/plan.md`.
- Script self-tests: `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`, `python3 plan2do/scripts/pre_review_ready.py --self-test`, `python3 debug-skill/scripts/skill_audit_core.py --self-test`.
- Skill validators: `python3 .system/skill-creator/scripts/quick_validate.py reviewer`, `debug-skill`, `spec2plan`, `plan2do`, `skill-tokenless`.
- Diff check: `git diff --check -- reviewer spec2plan plan2do skill-tokenless debug-skill .codex/work/20260621-skill-self-evolution-hardening`.
- Production gate: draft and final `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage <draft|final>`.
- Reviewer report: `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-skill-self-evolution-hardening/review-final.md`.
- Execution final: `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-self-evolution-hardening --stage final --require-production-report --require-final-report` and `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-self-evolution-hardening`.

## Rollout Plan
- Local-only skill repository update under `/data/lcq/.codex/skills`.
- No runtime deployment, package release, git commit, branch change, or external service call.
- Final handoff reports changed files, validators, reviewer verdict, and residual risks.

## Monitoring / Observability
- Machine-visible evidence lives in `.codex/work/20260621-skill-self-evolution-hardening/artifacts/`.
- `execution/tasks.json` tracks task status.
- `production-report.md`, `review-final.md`, and `final-report.md` provide gate status.

## Documentation / ADR Updates
- ADR: Not needed.
- Skill contract docs are the durable documentation: `reviewer/references/subagent-dispatch.md`, `spec2plan/references/plan-contract.md`, `plan2do/references/execution-contract.md`, `debug-skill/SKILL.md`, and debug references.

## Rollback / Recovery Plan
- Revert this plan's modified target files only: `reviewer/references/subagent-dispatch.md`, `spec2plan/references/plan-contract.md`, `plan2do/references/execution-contract.md`, `skill-tokenless/scripts/validate_skill_production.py`, `debug-skill/SKILL.md`, `debug-skill/references/hermes-reuse.md`, `debug-skill/references/report-template.md`, `debug-skill/scripts/skill_audit_core.py`, and `.codex/work/20260621-skill-self-evolution-hardening/*` generated after `plan.md`.
- Preserve unrelated pre-existing dirty files listed in Current Context.
- If validation fails, write `.codex/work/20260621-skill-self-evolution-hardening/artifacts/rework-guidance.md`, apply the smallest scoped fix, rerun the failing command plus cheap adjacent checks.

## Abort Criteria
- `apply_patch` misses twice on the same file after raw re-read.
- A validator fails twice for the same cause after scoped rework.
- Final reviewer returns `BLOCK`.
- Required evidence conflicts between spec, plan, current source, and validator behavior.
- A requested fix would require secrets, private history mining, destructive git history changes, or external dependencies.

## Risks
- Reviewer path guidance could increase packet verbosity; mitigation is limited fields only for local artifacts.
- Docs-only readiness wording might be ignored by future agents; mitigation is explicit contract language plus `pre_review_ready.py --self-test` evidence.
- Validator parsing could become too strict; mitigation is positive PASS, explicit BLOCK, and SKIPPED-style outcome tests.
- Debug-skill Hermes terminology could invite auto-edits; mitigation is repeated recommendation-only and explicit approval language.

## Open Questions
- None blocking; fixture form and helper surface are determined by smallest reliable implementation inside task writable scopes.

## Plan Self-Review
- Every task has exact writable scope and same-wave writes do not overlap.
- Every behavior change has coverage through self-test, scenario artifact, quick validation, or manual verification command.
- Every unknown is recorded in Assumptions or Open Questions, not hidden in task text.
- Rollback, abort criteria, and monitoring are specific enough for Medium risk.
- A fresh agent can execute Task 1 from this plan using the listed source paths, commands, and output artifact.

## Execution Decision
- Proceed with primary-agent execution under `plan2do`.
- Run `reviewer` as the final gate after draft readiness passes.
- Include Skill Production Gate draft and final validation because material skill/script workflow changes are in scope.

## Execution Handoff

- Goal: Harden reviewer path evidence, readiness contracts, production-report validation, and `debug-skill` self-evolution protocol from `.codex/work/20260621-skill-self-evolution-hardening/spec.md`.
- Current state: Spec and lite spec review exist; plan is ready for validation and execution after `validate_plan_contract.py` passes.
- Authoritative artifacts: `.codex/work/20260621-skill-self-evolution-hardening/spec.md`, `.codex/work/20260621-skill-self-evolution-hardening/review.md`, `.codex/work/20260621-skill-self-evolution-hardening/plan.md`, named skill contracts, and current target files.
- Decisions: Use light `spec2plan`, primary-agent `plan2do`, final `reviewer` gate, and mandatory Skill Production Gate.
- Verification: Run plan validator, execution compiler, script self-tests, `quick_validate.py`, `git diff --check`, production gate draft/final validation, reviewer report validator, pre-review readiness draft/final, and execution validation.
- Remaining risks: Reviewer path proof is scenario-based because no reviewer dispatch fixture runner exists; future private-history mining remains out of scope.
- Next action: Run `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-self-evolution-hardening/plan.md --mode light`.
- Suggested skills: `plan2do`, `reviewer`, `debug-skill`, `skill-tokenless`, `context-engineering`, `edit-orchestration`, `codegraph-project-reader`.
- Redactions / omitted raw data: Raw command logs, raw diffs, and subagent transcripts will be summarized under `.codex/work/20260621-skill-self-evolution-hardening/artifacts/`.
