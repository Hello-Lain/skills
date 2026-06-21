# Skill Execution Stability Gates Plan

Mode: light
Risk level: Medium
Confidence: High

## Goal
实现 v1 skill execution stability gates：在 final reviewer 前用本地 readiness gate 捕获缺失 artifact、pending task、无效 production report，并让 production report 支持 draft/final 两阶段。

## Non-Goals
不重写全部 skill contract；不引入 mandatory third-party dependency；不修改 Codex/Paseo agent manager internals；不改历史产物，除活跃 execution workspace 内的执行 artifact。

## Evidence Inspected
- `.codex/work/20260621-skill-execution-stability/spec.md`
- `.codex/work/20260621-skill-execution-stability/manifest.yaml`
- `AGENTS.md`
- `spec2plan/SKILL.md`
- `spec2plan/references/plan-contract.md`
- `spec2plan/references/artifact-contract.md`
- `plan2do/SKILL.md`
- `plan2do/references/execution-contract.md`
- `plan2do/references/review-rubric.md`
- `plan2do/scripts/validate_execution.py`
- `plan2do/scripts/compile_execution.py`
- `skill-tokenless/SKILL.md`
- `skill-tokenless/references/testing.md`
- `skill-tokenless/references/validation.md`
- `skill-tokenless/references/skill-production-gate.md`
- `skill-tokenless/scripts/validate_skill_production.py`
- `reviewer/SKILL.md`
- `reviewer/references/subagent-dispatch.md`
- `reviewer/references/review-report-template.md`
- `reviewer/scripts/validate_review_report.py`
- `edit-orchestration/SKILL.md`
- `edit-orchestration/references/apply-patch.md`
- `.codex/work/20260621-skill-production-gate/artifacts/production-report.md`
- `.codex/work/20260621-skill-production-gate/execution/tasks.json`

## Spec Summary
新增 `plan2do/scripts/pre_review_ready.py`；扩展 `validate_skill_production.py --stage draft|final`；更新 `plan2do`、`spec2plan`、`skill-tokenless`、`reviewer` docs；加入 self-test/fixture；最终跑 readiness、production、plan、execution、reviewer validators，并通过 reviewer gate。

## Domain Language Check
统一使用 `readiness gate`、`production report`、`draft stage`、`final stage`、`reviewer subagent`、`healthy-running`、`abnormal diagnostic policy`。`readiness gate` 是 final reviewer launch 前的本地确定性检查，不替代 final execution validation。

## Current Context
当前 git status 只有 `.codex/work/20260621-skill-execution-stability/` 未跟踪。目标文件均在 `/data/lcq/.codex/skills` 下。实现会触及 skill docs、两个 Python validator、一个新增 readiness script、活跃 workspace artifact。

## Implementation Map
- Files: `plan2do/scripts/pre_review_ready.py` 新增 readiness validator；`skill-tokenless/scripts/validate_skill_production.py` 增加 `--stage`；`plan2do/SKILL.md`、`plan2do/references/execution-contract.md`、`skill-tokenless/references/skill-production-gate.md`、`spec2plan/SKILL.md`、`spec2plan/references/plan-contract.md`、`reviewer/SKILL.md`、`reviewer/references/subagent-dispatch.md` 更新流程文字；`.codex/work/20260621-skill-execution-stability/artifacts/*.md` 记录执行证据。
- Symbols / APIs: `validate_report(path, root, stage)`；`run_self_test()`；new `validate_workspace(workspace, stage, production_report, require_final_report)`；CLI `pre_review_ready.py <workspace> --stage draft|final --self-test`；CLI `validate_skill_production.py <report> --stage draft|final --root <repo>`.
- Tests: script self-tests in `plan2do/scripts/pre_review_ready.py --self-test` and `skill-tokenless/scripts/validate_skill_production.py --self-test`; existing `reviewer/scripts/validate_review_report.py --self-test`; `quick_validate.py` for `skill-tokenless reviewer plan2do spec2plan`.
- Commands: `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-execution-stability/plan.md --mode light`; `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-skill-execution-stability/plan.md`; final acceptance commands listed in Validation Plan.
- Data / migration impact: Not applicable; only local docs, scripts, and generated execution artifacts change.

## Assumptions
- Existing `.codex/work/20260621-skill-production-gate/artifacts/production-report.md` is intended to remain final-compatible after `--stage final`.
- Readiness gate may reuse `validate_skill_production.py` by subprocess instead of importing to avoid import path coupling.
- Reviewer lifecycle behavior can be enforced through docs/prompt validation, not live provider outage simulation.

## User Inputs Needed
None. The confirmed spec contains no open questions.

## Proposed Approach
Implement minimal stdlib scripts and compact doc changes. Keep `validate_execution.py` as final acceptance; add `pre_review_ready.py` as a pre-review completeness gate. Make production reports valid in draft with pending/omitted reviewer verdict, strict in final. Run all deterministic validators before launching final isolated reviewer.

## Scenario Probes
- Missing task artifact fixture: readiness self-test must fail with a concise missing artifact error.
- Pending task fixture: readiness self-test must fail on pending status.
- Missing production report fixture: readiness self-test must fail when `--require-production-report` is active.
- Draft/final transition fixture: production validator self-test must pass draft pending reviewer and fail final pending reviewer.
- Existing report compatibility probe: prior production gate report must validate with `--stage final`.

## Dependency Graph
- Task 1 depends on this plan and current validator behavior.
- Task 2 depends on Task 1 only for naming alignment; script work can be separate but will run after Task 1.
- Task 3 depends on Task 1 and Task 2 interfaces.
- Task 4 depends on Tasks 1-3.
- Task 5 depends on Task 4 readiness passing.

## Task Breakdown
### Task 1: Add pre-review readiness gate

- Description: Create `plan2do/scripts/pre_review_ready.py` with workspace checks for execution state, task artifacts, task statuses, production report stage, final report, and self-test fixtures.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `pre_review_ready.py --self-test` passes; missing artifact, pending task, missing production report, and final report fixtures fail with actionable errors.
- Verification: `python3 plan2do/scripts/pre_review_ready.py --self-test`
- Concrete edits: Add `plan2do/scripts/pre_review_ready.py` using stdlib argparse/json/subprocess/tempfile/pathlib.
- Interfaces / contracts changed: New CLI `python3 plan2do/scripts/pre_review_ready.py <workspace> --stage draft|final --require-production-report --require-final-report`.
- Test cases: Self-test creates temporary workspaces for valid draft, valid final, missing task artifact, pending task, missing production report, and missing final report.
- Pre-check commands: `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-production-gate`
- Post-check commands: `python3 plan2do/scripts/pre_review_ready.py --self-test`
- Dependencies: None.
- Files likely touched: `plan2do/scripts/pre_review_ready.py`
- Writable scope: `plan2do/scripts/pre_review_ready.py`; `.codex/work/20260621-skill-execution-stability/artifacts/task1-execution.md`; `.codex/work/20260621-skill-execution-stability/artifacts/task1-verification.md`
- Output artifact: `.codex/work/20260621-skill-execution-stability/artifacts/task1-execution.md`
- Estimated scope: M

### Task 2: Add draft/final production report validation

- Description: Extend `skill-tokenless/scripts/validate_skill_production.py` with `--stage draft|final`, draft pending reviewer support, final reviewer strictness, and self-test cases.
- Worker role: coding
- Wave: 2
- Acceptance criteria: Self-test covers valid final, valid draft pending, final pending failure, final PASS blocked by reviewer REVISE/BLOCK, missing changed path, and missing reuse row.
- Verification: `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`
- Concrete edits: Update constants, `validate_report`, fixture builder, self-test matrix, and argparse stage option.
- Interfaces / contracts changed: CLI adds `--stage draft|final`; default stage remains `final`.
- Test cases: Self-test matrix inside `validate_skill_production.py`; compatibility check against `.codex/work/20260621-skill-production-gate/artifacts/production-report.md --stage final`.
- Pre-check commands: `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`
- Post-check commands: `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`
- Dependencies: Task 1.
- Files likely touched: `skill-tokenless/scripts/validate_skill_production.py`
- Writable scope: `skill-tokenless/scripts/validate_skill_production.py`; `.codex/work/20260621-skill-execution-stability/artifacts/task2-execution.md`; `.codex/work/20260621-skill-execution-stability/artifacts/task2-verification.md`
- Output artifact: `.codex/work/20260621-skill-execution-stability/artifacts/task2-execution.md`
- Estimated scope: M

### Task 3: Integrate readiness and lifecycle docs

- Description: Update skill docs/contracts so skill-work plans include readiness before final reviewer, production report lifecycle is two-stage, reviewer dispatch forbids nested reviewers, and healthy-running subagents are preserved.
- Worker role: coding
- Wave: 3
- Acceptance criteria: Docs name exact commands for draft/final production validation and pre-review readiness; reviewer dispatch prompt states already-isolated/no nested; plan2do quality gates mention readiness before reviewer launch.
- Verification: `for d in skill-tokenless reviewer plan2do spec2plan; do python3 .system/skill-creator/scripts/quick_validate.py "$d"; done`
- Concrete edits: Patch compact bullets in `plan2do/SKILL.md`, `plan2do/references/execution-contract.md`, `skill-tokenless/references/skill-production-gate.md`, `spec2plan/SKILL.md`, `spec2plan/references/plan-contract.md`, `reviewer/SKILL.md`, and `reviewer/references/subagent-dispatch.md`.
- Interfaces / contracts changed: Docs add readiness gate contract and draft/final production report lifecycle.
- Test cases: Quick validation for all touched skills plus grep checks for `pre_review_ready.py`, `--stage draft`, `--stage final`, and `Do not spawn nested reviewer subagents`.
- Pre-check commands: `git diff -- skill-tokenless reviewer plan2do spec2plan`
- Post-check commands: `for d in skill-tokenless reviewer plan2do spec2plan; do python3 .system/skill-creator/scripts/quick_validate.py "$d"; done`
- Dependencies: Task 1 and Task 2.
- Files likely touched: `plan2do/SKILL.md`; `plan2do/references/execution-contract.md`; `skill-tokenless/references/skill-production-gate.md`; `spec2plan/SKILL.md`; `spec2plan/references/plan-contract.md`; `reviewer/SKILL.md`; `reviewer/references/subagent-dispatch.md`
- Writable scope: `plan2do/SKILL.md`; `plan2do/references/execution-contract.md`; `skill-tokenless/references/skill-production-gate.md`; `spec2plan/SKILL.md`; `spec2plan/references/plan-contract.md`; `reviewer/SKILL.md`; `reviewer/references/subagent-dispatch.md`; `.codex/work/20260621-skill-execution-stability/artifacts/task3-execution.md`; `.codex/work/20260621-skill-execution-stability/artifacts/task3-verification.md`
- Output artifact: `.codex/work/20260621-skill-execution-stability/artifacts/task3-execution.md`
- Estimated scope: M

### Task 4: Run deterministic gates and draft production report

- Description: Compile execution state, run deterministic acceptance commands, write task verification artifacts, write a draft production report before reviewer, and mark non-review execution statuses complete.
- Worker role: coding
- Wave: 4
- Acceptance criteria: All planned deterministic checks pass; `production-report.md --stage draft` validates; `pre_review_ready.py .codex/work/20260621-skill-execution-stability --stage draft` passes before final reviewer launch.
- Verification: `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-execution-stability --stage draft --require-production-report --require-final-report`
- Concrete edits: Write `.codex/work/20260621-skill-execution-stability/artifacts/production-report.md`, task verification artifacts, `artifacts/final-report.md`, and update `.codex/work/20260621-skill-execution-stability/execution/tasks.json` statuses.
- Interfaces / contracts changed: Execution artifacts record production gate result and readiness gate evidence.
- Test cases: Acceptance command list from spec plus execution validation.
- Pre-check commands: `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-skill-execution-stability/plan.md`
- Post-check commands: `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-execution-stability --stage draft --require-production-report --require-final-report`
- Dependencies: Task 3.
- Files likely touched: `.codex/work/20260621-skill-execution-stability/execution/tasks.json`; `.codex/work/20260621-skill-execution-stability/artifacts/production-report.md`; `.codex/work/20260621-skill-execution-stability/artifacts/final-report.md`; `.codex/work/20260621-skill-execution-stability/artifacts/task4-execution.md`; `.codex/work/20260621-skill-execution-stability/artifacts/task4-verification.md`
- Writable scope: `.codex/work/20260621-skill-execution-stability/execution/tasks.json`; `.codex/work/20260621-skill-execution-stability/artifacts/production-report.md`; `.codex/work/20260621-skill-execution-stability/artifacts/final-report.md`; `.codex/work/20260621-skill-execution-stability/artifacts/task4-execution.md`; `.codex/work/20260621-skill-execution-stability/artifacts/task4-verification.md`
- Output artifact: `.codex/work/20260621-skill-execution-stability/artifacts/task4-execution.md`
- Estimated scope: M

### Task 5: Final reviewer gate and final production report

- Description: Launch isolated reviewer only after draft readiness passes, save reviewer report, archive completed reviewer subagent, apply bounded rework if verdict is REVISE, update production report to final, then run final execution validation.
- Worker role: review
- Wave: 5
- Acceptance criteria: Reviewer report is valid v2 shape; top-level verdict is PASS or actionable rework is completed; reviewer subagent cleanup is recorded; final `validate_execution.py` passes.
- Verification: `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-skill-execution-stability/review.md && python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-execution-stability`
- Concrete edits: Save `.codex/work/20260621-skill-execution-stability/review.md`; update `artifacts/production-report.md` reviewer gate to final `PASS|REVISE|BLOCK`; validate `--stage final`; update `artifacts/final-report.md` with final review and validation outcomes.
- Interfaces / contracts changed: Standalone review artifact contains `Verdict: PASS` or `Verdict: FAIL` for plan2do final validation, plus reviewer v2 report fields for reviewer validator.
- Test cases: `reviewer/scripts/validate_review_report.py` validates saved report; `plan2do/scripts/validate_execution.py` validates workspace.
- Pre-check commands: `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-execution-stability --stage draft --require-production-report --require-final-report`
- Post-check commands: `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-skill-execution-stability/review.md && python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-execution-stability`
- Dependencies: Task 4.
- Files likely touched: `.codex/work/20260621-skill-execution-stability/review.md`; `.codex/work/20260621-skill-execution-stability/artifacts/production-report.md`; `.codex/work/20260621-skill-execution-stability/artifacts/final-report.md`; `.codex/work/20260621-skill-execution-stability/artifacts/task5-execution.md`; `.codex/work/20260621-skill-execution-stability/artifacts/task5-verification.md`
- Writable scope: `.codex/work/20260621-skill-execution-stability/review.md`; `.codex/work/20260621-skill-execution-stability/artifacts/production-report.md`; `.codex/work/20260621-skill-execution-stability/artifacts/final-report.md`; `.codex/work/20260621-skill-execution-stability/artifacts/task5-execution.md`; `.codex/work/20260621-skill-execution-stability/artifacts/task5-verification.md`
- Output artifact: `.codex/work/20260621-skill-execution-stability/review.md`
- Estimated scope: S

## Step-by-Step Plan
1. Run `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-execution-stability/plan.md --mode light`.
2. Run `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-skill-execution-stability/plan.md`.
3. Add `plan2do/scripts/pre_review_ready.py` and run `python3 plan2do/scripts/pre_review_ready.py --self-test`.
4. Patch `skill-tokenless/scripts/validate_skill_production.py` and run `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`.
5. Patch docs in `plan2do/`, `skill-tokenless/`, `spec2plan/`, and `reviewer/`.
6. Run `for d in skill-tokenless reviewer plan2do spec2plan; do python3 .system/skill-creator/scripts/quick_validate.py "$d"; done`.
7. Run `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-production-gate --stage final`.
8. Write `.codex/work/20260621-skill-execution-stability/artifacts/production-report.md` and validate it with `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-execution-stability/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`.
9. Run `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-execution-stability --stage draft --require-production-report --require-final-report`.
10. Launch reviewer subagent with packet from `reviewer/references/subagent-dispatch.md`, save `.codex/work/20260621-skill-execution-stability/review.md`, then archive completed subagent.
11. Update `.codex/work/20260621-skill-execution-stability/artifacts/production-report.md` and run `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-execution-stability/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`.
12. Run `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-skill-execution-stability/review.md`.
13. Run `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-execution-stability`.

## Parallelization
No same-wave implementation parallelism. Tasks are serial because Task 3 docs depend on Task 1 and Task 2 CLI contracts, and Task 5 must wait for Task 4 readiness evidence. Review task is isolated after readiness.

## Files / Components Likely Affected
- `plan2do/scripts/pre_review_ready.py`
- `skill-tokenless/scripts/validate_skill_production.py`
- `plan2do/SKILL.md`
- `plan2do/references/execution-contract.md`
- `skill-tokenless/references/skill-production-gate.md`
- `spec2plan/SKILL.md`
- `spec2plan/references/plan-contract.md`
- `reviewer/SKILL.md`
- `reviewer/references/subagent-dispatch.md`
- `.codex/work/20260621-skill-execution-stability/plan.md`
- `.codex/work/20260621-skill-execution-stability/execution/tasks.json`
- `.codex/work/20260621-skill-execution-stability/artifacts/*.md`
- `.codex/work/20260621-skill-execution-stability/review.md`

## Owners / Responsibilities
- Primary agent: implement scripts/docs, run deterministic validators, maintain execution artifacts, preserve dirty work.
- Reviewer subagent: read-only final quality gate after readiness passes, no nested reviewer, save synthesized report.
- User: no input required unless reviewer returns BLOCK needing product decision.

## Validation Plan
- `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-execution-stability/plan.md --mode light`
- `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-skill-execution-stability/plan.md`
- `python3 plan2do/scripts/pre_review_ready.py --self-test`
- `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-production-gate --stage final`
- `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`
- `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-production-gate/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`
- `python3 reviewer/scripts/validate_review_report.py --self-test`
- `for d in skill-tokenless reviewer plan2do spec2plan; do python3 .system/skill-creator/scripts/quick_validate.py "$d"; done`
- `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-execution-stability/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
- `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-skill-execution-stability --stage draft --require-production-report --require-final-report`
- `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-execution-stability/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`
- `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-skill-execution-stability/review.md`
- `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-execution-stability`

## Rollout Plan
Local-only rollout under `/data/lcq/.codex/skills`. Existing workflows gain optional readiness command through docs and scripts. No runtime daemon restart.

## Monitoring / Observability
Validator stdout/stderr and execution artifacts under `.codex/work/20260621-skill-execution-stability/artifacts/` provide evidence. Final reviewer report records cleanup and residual risks.

## Documentation / ADR Updates
ADR: Not needed. This is workflow/script hardening inside existing skill contracts. Docs updated in skill references listed above.

## Rollback / Recovery Plan
Revert only this change set by restoring touched scripts/docs from git or deleting the new active workspace artifacts. If a validator regression appears, use self-test failures to isolate the script, then patch within the same writable scope.

## Abort Criteria
Abort if `pre_review_ready.py --self-test` cannot pass after two focused repair cycles, if `validate_skill_production.py --self-test` cannot pass after two focused repair cycles, if final reviewer returns BLOCK for missing source evidence, or if dirty work appears in touched script/doc paths from another actor.

## Risks
- Readiness duplicates final execution checks; mitigate by keeping it pre-review focused.
- Draft/final terminology can confuse agents; mitigate through validator errors and compact docs.
- Reviewer lifecycle cannot be live-fault tested; mitigate with prompt text and final reviewer gate.

## Open Questions
None.

## Plan Self-Review
- Writable scope: each task has exact scope; same-wave implementation writes do not overlap because waves are serial.
- Coverage: script behavior has self-tests plus compatibility checks against `20260621-skill-production-gate`.
- Unknown: no hidden unknown remains outside Assumptions or Open Questions.
- Rollback: restore touched files from git and remove active workspace artifacts.
- Task 1: fresh agent can start by reading this plan, then adding `plan2do/scripts/pre_review_ready.py`.

## Execution Decision
Proceed with primary-agent `plan2do` execution. Use `reviewer` subagent only after readiness passes. Do not use codex2codex because the user requested `spec2plan + plan2do + reviewer`, not codex2codex.

## Execution Handoff

- Goal: Implement Skill Execution Stability Gates v1.
- Current state: Spec saved at `.codex/work/20260621-skill-execution-stability/spec.md`; plan saved at `.codex/work/20260621-skill-execution-stability/plan.md`.
- Authoritative artifacts: `.codex/work/20260621-skill-execution-stability/spec.md`; `.codex/work/20260621-skill-execution-stability/plan.md`; `plan2do/references/execution-contract.md`; `skill-tokenless/references/skill-production-gate.md`; `reviewer/references/subagent-dispatch.md`.
- Decisions: Use stdlib scripts only; readiness before reviewer; production report defaults to final stage; reviewer remains isolated and no nested reviewer.
- Verification: Run commands in Validation Plan.
- Remaining risks: Live provider interruption for reviewer cannot be fixture-tested; coordinator policy handles abnormal-only polling.
- Next action: Run `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-execution-stability/plan.md --mode light`.
- Suggested skills: `plan2do`, `edit-orchestration`, `skill-tokenless`, `reviewer`.
- Redactions / omitted raw data: Raw command logs and subagent transcript streams stay out of final answer; artifact paths record summaries.
