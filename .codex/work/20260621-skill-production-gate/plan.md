# Skill Production Gate Implementation Plan

Mode: light
Risk level: High
Confidence: High

## Goal
Implement the confirmed Skill Production Gate spec so material skill creation and updates use deterministic validators, `skill-tokenless`, `reviewer`, and explicit subagent lifecycle rules.

## Non-Goals
- Do not rewrite all installed skills.
- Do not add Plandex, Aider, OpenRewrite, ast-grep, or pre-commit as mandatory dependencies.
- Do not run long live evals, external service checks, secret-bearing checks, or production workflows.
- Do not silently downgrade heavy reviewer subagent wait/provider anomalies to inline review.
- Do not revert unrelated dirty work already present in the repository.

## Evidence Inspected
- `.codex/work/20260621-skill-production-gate/spec.md`
- `.codex/work/20260621-skill-system-audit/artifacts/debug-skill-report.md`
- `.codex/work/20260621-skill-system-audit/artifacts/reviewer-gate.md`
- `/data/lcq/.codex/AGENTS.md`
- `skill-tokenless/SKILL.md`
- `skill-tokenless/references/testing.md`
- `skill-tokenless/references/validation.md`
- `.system/skill-creator/SKILL.md`
- `reviewer/SKILL.md`
- `reviewer/references/subagent-dispatch.md`
- `reviewer/references/review-report-template.md`
- `edit-orchestration/SKILL.md`
- `edit-orchestration/references/apply-patch.md`
- `edit-orchestration/references/route-matrix.md`
- `plan2do/SKILL.md`
- `plan2do/references/execution-contract.md`
- `spec2plan/SKILL.md`
- `spec2plan/references/plan-contract.md`

## Spec Summary
The confirmed spec requires a shared production gate for skills, deterministic validation scripts, GitHub reuse attribution, patch preflight support, `plan2do` and `spec2plan` integration, and a binding reviewer subagent health rule: healthy running subagents keep working; abnormal subagents are diagnosed with exactly 2 polls of 45 seconds each before blocking or narrowing/relaunching; do not use inline fallback for transient wait/provider issues.

## Domain Language Check
- Use "Skill Production Gate" for the shared gate.
- Use "production report" for the gate evidence artifact.
- Use "`reviewer` gate" for the final PASS/REVISE/BLOCK review.
- Use "plan2do review" for the existing PASS/FAIL execution acceptance artifact.
- No term conflict found in inspected skill contracts.

## Current Context
- Current repository has existing dirty changes in `plan2do/references/execution-contract.md` and `plan2do/scripts/validate_execution.py`; preserve and build on current files.
- `reviewer/` is untracked but present and required by this work.
- Previous audit artifacts are under `.codex/work/20260621-skill-system-audit/`.
- This workspace is `.codex/work/20260621-skill-production-gate/`.

## Implementation Map
- Files:
  - `skill-tokenless/SKILL.md`: route material skill work to the production gate.
  - `skill-tokenless/references/skill-production-gate.md`: new gate contract, report schema, reuse matrix rules.
  - `skill-tokenless/references/validation.md`: include production gate validator.
  - `skill-tokenless/references/testing.md`: include scenario gate relation to production reports.
  - `skill-tokenless/scripts/validate_skill_production.py`: new production report validator with self-test.
  - `.system/skill-creator/SKILL.md`: require production gate after `quick_validate.py` for new/material skills.
  - `reviewer/SKILL.md`: forbid inline fallback for heavy subagent wait/provider issues and preserve healthy running subagents.
  - `reviewer/references/subagent-dispatch.md`: encode abnormal-only `2 x 45s` diagnostic policy and cleanup.
  - `edit-orchestration/references/apply-patch.md`: add patch preflight route details.
  - `edit-orchestration/references/route-matrix.md`: route complex patch payloads through preflight helper.
  - `edit-orchestration/scripts/lint_apply_patch_payload.py`: new helper with self-test.
  - `plan2do/SKILL.md`: require production gate evidence for material skill work.
  - `plan2do/references/execution-contract.md`: define execution evidence for skill production tasks.
  - `spec2plan/references/plan-contract.md`: require production-gate tasks for skill plans.
  - `spec2plan/SKILL.md`: mention production-gate planning for skill work.
- Symbols / APIs:
  - `validate_skill_production.py --self-test`
  - `validate_skill_production.py <report.md> --root <repo>`
  - `lint_apply_patch_payload.py --self-test`
  - `lint_apply_patch_payload.py <payload-file>`
- Tests:
  - New script self-tests.
  - Existing skill validators.
  - Reviewer report validator self-test.
  - Plan validator and execution validator for this workspace.
- Commands:
  - `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`
  - `python3 edit-orchestration/scripts/lint_apply_patch_payload.py --self-test`
  - `python3 reviewer/scripts/validate_review_report.py --self-test`
  - `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-production-gate/plan.md --mode light`
  - `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-skill-production-gate/plan.md`
  - `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-production-gate`
  - `python3 .system/skill-creator/scripts/quick_validate.py <skill-dir>`
- Data / migration impact: Not applicable; docs and local scripts only.

## Assumptions
- The current `quick_validate.py` basic structural validation remains sufficient as the base skill validator.
- The production gate report schema can be Markdown in v1.
- Optional external tools remain optional to avoid new mandatory dependencies.

## User Inputs Needed
None.

## Proposed Approach
Implement four vertical slices: production gate contract and validator, reviewer lifecycle correction, patch preflight helper, and plan/execution integration. Validate each slice locally, then run final execution validation and reviewer gate.

## Scenario Probes
- Probe 1: A material skill update report missing `Reviewer Gate` fails `validate_skill_production.py`.
- Probe 2: A reviewer heavy subagent wait/provider anomaly no longer permits inline fallback, and healthy running subagents are not canceled or archived.
- Probe 3: An `apply_patch` payload with missing `+` in an add-file hunk fails `lint_apply_patch_payload.py`.
- Probe 4: A skill-change plan contains a production gate task and validates under `spec2plan`.

## Dependency Graph
- Task 1 has no dependencies.
- Task 2 depends on 1.
- Task 3 depends on 1.
- Task 4 depends on 1,2,3.
- Task 5 depends on 1,2,3,4.

## Task Breakdown
### Task 1: Add Skill Production Gate contract and validator

- Description: Create the gate contract, production report schema, validator script, self-test, and connect `skill-tokenless` plus `skill-creator` to the gate.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `skill-tokenless` exposes the production gate; `.system/skill-creator` requires it for new/material skills; `validate_skill_production.py --self-test` passes.
- Verification: `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`; `python3 .system/skill-creator/scripts/quick_validate.py skill-tokenless`; `python3 .system/skill-creator/scripts/quick_validate.py .system/skill-creator`
- Concrete edits: Add `skill-tokenless/references/skill-production-gate.md`; add `skill-tokenless/scripts/validate_skill_production.py`; update `skill-tokenless/SKILL.md`; update `skill-tokenless/references/validation.md`; update `skill-tokenless/references/testing.md`; update `.system/skill-creator/SKILL.md`.
- Interfaces / contracts changed: New production report schema and validator command.
- Test cases: Valid production report passes; missing required section fails; missing reviewer cleanup proof fails; missing reuse matrix source fails.
- Pre-check commands: `python3 .system/skill-creator/scripts/quick_validate.py skill-tokenless`
- Post-check commands: `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`
- Dependencies: none
- Files likely touched: `skill-tokenless/SKILL.md`, `skill-tokenless/references/skill-production-gate.md`, `skill-tokenless/references/validation.md`, `skill-tokenless/references/testing.md`, `skill-tokenless/scripts/validate_skill_production.py`, `.system/skill-creator/SKILL.md`
- Writable scope: `skill-tokenless/SKILL.md`, `skill-tokenless/references/skill-production-gate.md`, `skill-tokenless/references/validation.md`, `skill-tokenless/references/testing.md`, `skill-tokenless/scripts/validate_skill_production.py`, `.system/skill-creator/SKILL.md`, `.codex/work/20260621-skill-production-gate/artifacts/task1-execution.md`, `.codex/work/20260621-skill-production-gate/artifacts/task1-verification.md`
- Output artifact: `.codex/work/20260621-skill-production-gate/artifacts/task1-execution.md`
- Estimated scope: M

### Task 2: Correct reviewer subagent health policy

- Description: Update reviewer docs so heavy or mandatory-isolation subagents are polled only after abnormal signals; healthy running subagents continue, and transient wait/provider issues never downgrade to inline review.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `reviewer` docs state the binding abnormal-only diagnostic policy; healthy running subagents are not canceled or archived; confirmed abnormal state leads to `BLOCK` or narrower relaunch with cleanup; reviewer validation still passes.
- Verification: `python3 reviewer/scripts/validate_review_report.py --self-test`; `python3 .system/skill-creator/scripts/quick_validate.py reviewer`
- Concrete edits: Update `reviewer/SKILL.md` and `reviewer/references/subagent-dispatch.md`.
- Interfaces / contracts changed: Reviewer subagent lifecycle policy.
- Test cases: Text search confirms `2` polls and `45` seconds apply only to abnormal diagnosis; text search confirms no inline fallback from transient wait/provider issues and no cancel/archive for healthy running subagents.
- Pre-check commands: `python3 reviewer/scripts/validate_review_report.py --self-test`
- Post-check commands: `python3 reviewer/scripts/validate_review_report.py --self-test`
- Dependencies: 1
- Files likely touched: `reviewer/SKILL.md`, `reviewer/references/subagent-dispatch.md`
- Writable scope: `reviewer/SKILL.md`, `reviewer/references/subagent-dispatch.md`, `.codex/work/20260621-skill-production-gate/artifacts/task2-execution.md`, `.codex/work/20260621-skill-production-gate/artifacts/task2-verification.md`
- Output artifact: `.codex/work/20260621-skill-production-gate/artifacts/task2-execution.md`
- Estimated scope: S

### Task 3: Add apply_patch payload preflight helper

- Description: Add deterministic preflight guidance and a script that catches common malformed `apply_patch` payloads before complex patches are submitted.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `edit-orchestration` docs mention preflight helper; helper self-test catches malformed add-file and missing patch boundary cases.
- Verification: `python3 edit-orchestration/scripts/lint_apply_patch_payload.py --self-test`; `python3 .system/skill-creator/scripts/quick_validate.py edit-orchestration`
- Concrete edits: Add `edit-orchestration/scripts/lint_apply_patch_payload.py`; update `edit-orchestration/references/apply-patch.md`; update `edit-orchestration/references/route-matrix.md`.
- Interfaces / contracts changed: New optional preflight script command.
- Test cases: Valid add/update payload passes; add-file line without `+` fails; missing `*** End Patch` fails; JSON wrapper fails.
- Pre-check commands: `python3 edit-orchestration/scripts/self_check_edit_tools.py --tool ast-grep --json`
- Post-check commands: `python3 edit-orchestration/scripts/lint_apply_patch_payload.py --self-test`
- Dependencies: 1
- Files likely touched: `edit-orchestration/references/apply-patch.md`, `edit-orchestration/references/route-matrix.md`, `edit-orchestration/scripts/lint_apply_patch_payload.py`
- Writable scope: `edit-orchestration/references/apply-patch.md`, `edit-orchestration/references/route-matrix.md`, `edit-orchestration/scripts/lint_apply_patch_payload.py`, `.codex/work/20260621-skill-production-gate/artifacts/task3-execution.md`, `.codex/work/20260621-skill-production-gate/artifacts/task3-verification.md`
- Output artifact: `.codex/work/20260621-skill-production-gate/artifacts/task3-execution.md`
- Estimated scope: S

### Task 4: Integrate production gate into plan and execution contracts

- Description: Update `spec2plan` and `plan2do` so skill plans and skill execution require production-gate evidence for new/material skill work.
- Worker role: coding
- Wave: 3
- Acceptance criteria: `spec2plan` plan contract requires production-gate tasks for skill work; `plan2do` execution contract requires production reports before final acceptance of material skill work.
- Verification: `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-production-gate/plan.md --mode light`; `python3 .system/skill-creator/scripts/quick_validate.py plan2do`; `python3 .system/skill-creator/scripts/quick_validate.py spec2plan`
- Concrete edits: Update `spec2plan/SKILL.md`; update `spec2plan/references/plan-contract.md`; update `plan2do/SKILL.md`; update `plan2do/references/execution-contract.md`.
- Interfaces / contracts changed: Plan contract and execution acceptance for material skill work.
- Test cases: This plan validates and compiles; execution final report includes production report path.
- Pre-check commands: `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-production-gate/plan.md --mode light`
- Post-check commands: `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-production-gate/plan.md --mode light`
- Dependencies: 1,2,3
- Files likely touched: `spec2plan/SKILL.md`, `spec2plan/references/plan-contract.md`, `plan2do/SKILL.md`, `plan2do/references/execution-contract.md`
- Writable scope: `spec2plan/SKILL.md`, `spec2plan/references/plan-contract.md`, `plan2do/SKILL.md`, `plan2do/references/execution-contract.md`, `.codex/work/20260621-skill-production-gate/artifacts/task4-execution.md`, `.codex/work/20260621-skill-production-gate/artifacts/task4-verification.md`
- Output artifact: `.codex/work/20260621-skill-production-gate/artifacts/task4-execution.md`
- Estimated scope: S

### Task 5: Final validation and review gate

- Description: Run full validation, write production report, run reviewer gate, update execution statuses, and produce final report.
- Worker role: review
- Wave: 4
- Acceptance criteria: All planned commands pass; production report validates; reviewer gate returns `PASS`; execution validator returns `VALID`.
- Verification: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-production-gate/artifacts/production-report.md --root /data/lcq/.codex/skills`; `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-skill-production-gate/review.md --root /data/lcq/.codex/skills`; `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-production-gate`
- Concrete edits: Write `.codex/work/20260621-skill-production-gate/artifacts/production-report.md`; write `.codex/work/20260621-skill-production-gate/review.md`; write final execution report.
- Interfaces / contracts changed: None.
- Test cases: Production report schema validation; reviewer report schema validation; execution validation.
- Pre-check commands: `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-skill-production-gate/plan.md`
- Post-check commands: `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-production-gate`
- Dependencies: 1,2,3,4
- Files likely touched: `.codex/work/20260621-skill-production-gate/artifacts/production-report.md`, `.codex/work/20260621-skill-production-gate/review.md`, `.codex/work/20260621-skill-production-gate/artifacts/final-report.md`, `.codex/work/20260621-skill-production-gate/execution/tasks.json`
- Writable scope: `.codex/work/20260621-skill-production-gate/artifacts/production-report.md`, `.codex/work/20260621-skill-production-gate/review.md`, `.codex/work/20260621-skill-production-gate/artifacts/task5-execution.md`, `.codex/work/20260621-skill-production-gate/artifacts/task5-verification.md`, `.codex/work/20260621-skill-production-gate/artifacts/final-report.md`, `.codex/work/20260621-skill-production-gate/execution/tasks.json`
- Output artifact: `.codex/work/20260621-skill-production-gate/review.md`
- Estimated scope: S

## Step-by-Step Plan
1. Save this plan at `.codex/work/20260621-skill-production-gate/plan.md`.
2. Run `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-production-gate/plan.md --mode light`.
3. Run `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-skill-production-gate/plan.md`.
4. Add `skill-tokenless/references/skill-production-gate.md` and `skill-tokenless/scripts/validate_skill_production.py`.
5. Patch `skill-tokenless/SKILL.md`, `skill-tokenless/references/validation.md`, `skill-tokenless/references/testing.md`, and `.system/skill-creator/SKILL.md`.
6. Run `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`.
7. Patch `reviewer/SKILL.md` and `reviewer/references/subagent-dispatch.md` for the abnormal-only `2 x 45s` health policy.
8. Run `python3 reviewer/scripts/validate_review_report.py --self-test`.
9. Add `edit-orchestration/scripts/lint_apply_patch_payload.py`.
10. Patch `edit-orchestration/references/apply-patch.md` and `edit-orchestration/references/route-matrix.md`.
11. Run `python3 edit-orchestration/scripts/lint_apply_patch_payload.py --self-test`.
12. Patch `spec2plan/SKILL.md`, `spec2plan/references/plan-contract.md`, `plan2do/SKILL.md`, and `plan2do/references/execution-contract.md`.
13. Run `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-production-gate/plan.md --mode light`.
14. Run `python3 .system/skill-creator/scripts/quick_validate.py` for each changed skill directory.
15. Write `.codex/work/20260621-skill-production-gate/artifacts/production-report.md`.
16. Run `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-production-gate/artifacts/production-report.md --root /data/lcq/.codex/skills`.
17. Dispatch `reviewer` subagent for final review; poll `2 x 45s` only if it appears abnormal. If healthy and still running, continue waiting. If still abnormal, return `BLOCK` or relaunch with a narrower packet after cleanup.
18. Validate `.codex/work/20260621-skill-production-gate/review.md` with `python3 reviewer/scripts/validate_review_report.py`.
19. Update `.codex/work/20260621-skill-production-gate/execution/tasks.json` statuses to `complete` after artifacts and verification exist.
20. Run `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-production-gate`.
21. Write `.codex/work/20260621-skill-production-gate/artifacts/final-report.md`.

## Parallelization
- Wave 1: Task 1 only because it defines the shared contract.
- Wave 2: Task 2 and Task 3 can run after Task 1 because they write disjoint paths.
- Wave 3: Task 4 runs after Tasks 1, 2, and 3 because it references their contracts.
- Wave 4: Task 5 runs after all implementation tasks.

## Files / Components Likely Affected
- `skill-tokenless/`
- `.system/skill-creator/SKILL.md`
- `reviewer/`
- `edit-orchestration/`
- `plan2do/`
- `spec2plan/`
- `.codex/work/20260621-skill-production-gate/`

## Owners / Responsibilities
- Main agent: implement docs/scripts, run validators, preserve dirty work, coordinate reviewer.
- Reviewer subagent: read-only final quality gate, writes synthesized report only.
- User: no input required unless reviewer returns `BLOCK` requiring product/scope decision.

## Validation Plan
- Run all commands listed in task post-checks.
- Validate every changed skill with `quick_validate.py`.
- Validate production report with `validate_skill_production.py`.
- Validate reviewer report with `validate_review_report.py`.
- Validate plan and execution with `validate_plan_contract.py`, `compile_execution.py`, and `validate_execution.py`.

## Rollout Plan
- Local rollout only: update skill docs/scripts in the current workspace.
- No external service rollout.
- New behavior applies to future skill creation/material update work after files are saved.

## Monitoring / Observability
- Use task artifacts under `.codex/work/20260621-skill-production-gate/artifacts/`.
- Use production report as the gate receipt.
- Use reviewer report as independent quality receipt.
- Use `git status --short` and focused diffs to detect unintended files.

## Documentation / ADR Updates
ADR: Not needed. This is a local skill workflow contract; the authoritative docs are the changed `SKILL.md` and `references/` files.

## Rollback / Recovery Plan
- Revert only this plan's edits if explicitly requested; do not revert unrelated dirty changes.
- If a script self-test fails, patch the smallest failing script section and rerun the self-test once.
- If reviewer returns `REVISE`, write rework guidance and fix the cited issue within the plan writable scope.
- If subagent review remains abnormal after `2 x 45s` diagnostic polling, report `BLOCK` or relaunch with a narrower packet after cleanup. If it is healthy and still running, continue waiting.

## Abort Criteria
- Any validator cannot pass after two focused repair cycles.
- Reviewer returns `BLOCK` with missing evidence that cannot be supplied locally.
- A required edit would overwrite unrelated user changes.
- A required tool is unavailable and no safe local fallback exists.

## Risks
- Validator schema may be too strict. Mitigation: self-test includes valid and invalid reports.
- Documentation changes can bloat always-loaded files. Mitigation: move long schema to references.
- Subagent wait policy can slow final review. Mitigation: poll only abnormal subagents; use two 45-second diagnostic polls and no hidden fallback.
- Existing dirty `plan2do` files may conflict. Mitigation: read current files and patch current content only.

## Open Questions
None.

## Plan Self-Review
- Every task has exact writable scope and non-overlapping same-wave writes: yes.
- Every behavior change has regression or smoke coverage: yes, through script self-tests, validators, and grep/text checks.
- Every unknown is in `Assumptions` or `Open Questions`, not hidden in task text: yes.
- Rollback, abort criteria, and monitoring are specific enough for the risk level: yes.
- A fresh agent can execute Task 1 from this plan without raw transcript context: yes.

## Execution Decision
- Decision: execute now with `plan2do` primary-agent mode because the user explicitly requested `spec2plan + plan2do + reviewer` landing.
- Review: final reviewer gate is mandatory.
- Implementation mode: primary-agent.

## Execution Handoff
- Goal: Implement Skill Production Gate v1 for material skill work.
- Current state: Spec saved at `.codex/work/20260621-skill-production-gate/spec.md`; plan saved at `.codex/work/20260621-skill-production-gate/plan.md`.
- Authoritative artifacts: `.codex/work/20260621-skill-production-gate/spec.md`, `.codex/work/20260621-skill-system-audit/artifacts/debug-skill-report.md`.
- Decisions: Use light planning, primary-agent execution, final reviewer subagent, abnormal-only `2 x 45s` no-downgrade health policy.
- Verification: Run plan, script, skill, production report, reviewer report, and execution validators.
- Remaining risks: Existing dirty work in `plan2do` files; preserve current edits.
- Next action: Run plan validator, compile execution state, then execute Task 1.
- Suggested skills: `plan2do`, `edit-orchestration`, `reviewer`, `skill-tokenless`, `context-engineering`.
- Redactions / omitted raw data: Raw prior transcripts and external clone contents omitted; source paths and URLs retained.
