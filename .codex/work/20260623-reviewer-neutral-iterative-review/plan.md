# Reviewer Neutral Iterative Review Plan

Mode: light
Risk level: Medium
Confidence: High

## Goal
Implement the confirmed spec by updating reviewer skill documentation so reviewer uses neutral, evidence-first framing and a bounded issue-discovery loop before final verdicts.

## Non-Goals
- Do not copy `introspector` wholesale into `reviewer`.
- Do not change reviewer top-level verdicts or replace the v2 report format.
- Do not require infinite loops, unbounded context loading, or heavy-by-default review.
- Do not edit reviewer validator scripts unless documentation compatibility checks fail.

## Evidence Inspected
- `.codex/work/20260623-reviewer-neutral-iterative-review/spec.md`
- `.codex/work/20260623-reviewer-neutral-iterative-review/manifest.yaml`
- `reviewer/SKILL.md`
- `reviewer/references/review-report-template.md`
- `reviewer/references/review-rubrics.md`
- `reviewer/scripts/validate_review_report.py`
- `introspector/SKILL.md`
- `introspector/references/workflow.md`
- `introspector/references/report-schema.md`
- `spec2plan/references/plan-contract.md`
- `spec2plan/references/artifact-contract.md`
- `plan2do/references/execution-contract.md`
- `skill-tokenless/references/skill-production-gate.md`
- `structural-edit/references/route-matrix.md`
- `structural-edit/references/fallback-policy.md`

## Spec Summary
The spec requires `reviewer` to absorb neutral, evidence-first review principles from `introspector` and to stop treating the first obvious finding as sufficient review coverage. A `PASS` must state convergence, and `REVISE` or `BLOCK` must include all known critical and major findings discovered in the bounded pass.

## Upstream Coverage
- Source artifacts: `.codex/work/20260623-reviewer-neutral-iterative-review/spec.md`
- Carried forward: user, why now, success criteria, v1 docs-only constraint, lite/heavy compatibility, report compatibility, bounded loop, convergence basis, no wholesale introspector copy, no infinite loop.
- Added planning detail: exact files, edit scope, validation commands, production report path, reviewer report path, task order, rollback, and final acceptance gates.
- Dropped / deferred upstream details: validator script edits remain deferred because the spec constrains v1 to documentation/reference behavior unless compatibility checks fail.

## Domain Language Check
Use existing reviewer terms: `Review Mode`, `Review Route`, `PASS`, `REVISE`, `BLOCK`, `Review Basis`, `Rubric`, `Recheck Plan`, `Residual Risks`, `lite`, `heavy`, `blocked`. Use introspector concepts only as principles: root objective, framing audit, direct evidence, inference, uncertainty, falsifier, bounded loop.

## Current Context
The repository root is `/data/lcq/.codex/skills`. The topic workspace already contains a confirmed `spec.md`, `manifest.yaml`, and a passing spec lite review artifact. `reviewer/SKILL.md` currently has evidence, routing, adversarial mode, recheck loop, and validator guidance, but no first-pass convergence loop that forbids stopping after the first obvious issue.

## Implementation Map
- Files: `reviewer/SKILL.md` will receive the neutral evidence-first contract and bounded issue-discovery workflow.
- Files: `reviewer/references/review-report-template.md` may receive one concise rule clarifying convergence in existing sections if needed.
- Files: `.codex/work/20260623-reviewer-neutral-iterative-review/manifest.yaml` will update stage and canonical plan lock.
- Files: `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md` will record Skill Production Gate evidence.
- Files: `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/final-report.md` will record plan2do completion evidence.
- Files: `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/review-final.md` will record final reviewer gate.
- Symbols / APIs: Markdown-only skill workflow contract; no Python APIs or schemas changed.
- Tests: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`; `python3 reviewer/scripts/validate_review_report.py --self-test`; `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`; `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260623-reviewer-neutral-iterative-review --stage draft --require-production-report --require-final-report`; `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`; `python3 plan2do/scripts/validate_execution.py .codex/work/20260623-reviewer-neutral-iterative-review`.
- Commands: `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260623-reviewer-neutral-iterative-review/plan.md --mode light`; `python3 plan2do/scripts/compile_execution.py .codex/work/20260623-reviewer-neutral-iterative-review/plan.md`.
- Data / migration impact: Not applicable because no runtime data, config state, or schema changes are planned.

## Assumptions
- `reviewer/references/review-report-template.md` can express convergence through `Review Basis`, `Recheck Plan`, and `Residual Risks` without adding a new machine-validated field.
- Markdown text fallback via `apply_patch` is acceptable because edits are small, uniquely anchored, prose-like, and lower risk than introducing a Markdown AST toolchain for this targeted change.
- Final reviewer heavy isolation is unavailable in the current explicit-delegation policy unless subagent tooling is exposed; inline heavy is acceptable with fallback reason if no reviewer subagent tool is available.

## User Inputs Needed
None. The user explicitly approved the spec and requested implementation.

## Proposed Approach
Patch `reviewer/SKILL.md` with a compact neutral review contract and first-pass discovery loop. Use the existing report template sections for convergence instead of adding a schema field. Validate reviewer syntax, report validator self-test, production gate draft/final, execution readiness, and final execution state.

## Scenario Probes
- Probe 1: A reviewer sees one major issue in a plan. Expected behavior after patch: it records that issue, continues scanning remaining relevant risk surfaces, then reports all known critical/major issues.
- Probe 2: A reviewer wants to return `PASS` on a small spec. Expected behavior after patch: it states the main surfaces checked and route-limited uncertainty in `Residual Risks` or `Recheck Plan`.
- Probe 3: A reviewer lacks evidence to judge hidden callers or source authority. Expected behavior after patch: it escalates route or returns `BLOCK`, not fake certainty.

## Dependency Graph
- Task 1 must run before Task 2 because source edits require context and behavior lock.
- Task 2 must run before Task 3 because production evidence depends on changed files.
- Task 3 must run before Task 4 because final reviewer needs draft production readiness.
- Task 4 must run before final acceptance because production gate final requires reviewer verdict.

## Task Breakdown
### Task 1: Prepare execution context

- Description: Create execution checklist and wave context artifact for the reviewer documentation update.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `execution/tasks.json` exists and `artifacts/context-wave1.md` records authoritative sources and constraints.
- Verification: `test -s .codex/work/20260623-reviewer-neutral-iterative-review/execution/tasks.json && test -s .codex/work/20260623-reviewer-neutral-iterative-review/artifacts/context-wave1.md`
- Concrete edits: Create execution artifacts only.
- Interfaces / contracts changed: None.
- Test cases: Not applicable for artifact setup.
- Pre-check commands: `python3 plan2do/scripts/compile_execution.py .codex/work/20260623-reviewer-neutral-iterative-review/plan.md`
- Post-check commands: `test -s .codex/work/20260623-reviewer-neutral-iterative-review/execution/tasks.json`
- Dependencies: None.
- Files likely touched: `.codex/work/20260623-reviewer-neutral-iterative-review/execution/tasks.json`, `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/context-wave1.md`
- Writable scope: `.codex/work/20260623-reviewer-neutral-iterative-review/**`
- Output artifact: `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/task1-execution.md`
- Estimated scope: XS

### Task 2: Patch reviewer workflow docs

- Description: Update reviewer documentation to require neutral framing, bounded issue discovery, and convergence before final verdict.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `reviewer/SKILL.md` says an obvious first finding is not enough to stop, requires continued critical/major discovery, separates direct evidence from inference, and requires PASS convergence in existing report sections.
- Verification: `rg "first obvious|Issue Discovery|convergence|direct evidence|inference" reviewer/SKILL.md reviewer/references/review-report-template.md`
- Concrete edits: Patch `reviewer/SKILL.md`; patch `reviewer/references/review-report-template.md` only if existing sections need convergence wording.
- Interfaces / contracts changed: Reviewer workflow behavior changes; top-level report schema remains compatible.
- Test cases: Manual scenario probes from `Scenario Probes`.
- Pre-check commands: `git diff -- reviewer/SKILL.md reviewer/references/review-report-template.md`
- Post-check commands: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`
- Dependencies: Task 1.
- Files likely touched: `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`
- Writable scope: `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`, `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/**`
- Output artifact: `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/task2-execution.md`
- Estimated scope: S

### Task 3: Run deterministic gates and production draft

- Description: Run reviewer validators and write draft Skill Production Gate report for the material workflow change.
- Worker role: coding
- Wave: 3
- Acceptance criteria: quick validate passes, reviewer report validator self-test passes, draft production report validates, and final-report placeholder exists for draft readiness.
- Verification: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
- Concrete edits: Write `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md` and `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/final-report.md`.
- Interfaces / contracts changed: None beyond recorded skill workflow change.
- Test cases: RED/control and GREEN scenario probe recorded in production report.
- Pre-check commands: `python3 reviewer/scripts/validate_review_report.py --self-test`
- Post-check commands: `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260623-reviewer-neutral-iterative-review --stage draft --require-production-report --require-final-report`
- Dependencies: Task 2.
- Files likely touched: `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md`, `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/final-report.md`
- Writable scope: `.codex/work/20260623-reviewer-neutral-iterative-review/**`
- Output artifact: `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/task3-verification.md`
- Estimated scope: S

### Task 4: Final review and acceptance

- Description: Run reviewer gate, finalize production report, validate execution state, and update manifest stage.
- Worker role: review
- Wave: 4
- Acceptance criteria: final reviewer report is `PASS`, production report validates as final, execution validates, and manifest records canonical plan.
- Verification: `python3 plan2do/scripts/validate_execution.py .codex/work/20260623-reviewer-neutral-iterative-review`
- Concrete edits: Write `artifacts/review-final.md`, update `artifacts/production-report.md`, update `artifacts/final-report.md`, and update `manifest.yaml`.
- Interfaces / contracts changed: None beyond finalized reviewer skill docs.
- Test cases: Reviewer gate checks source alignment, convergence wording, route compatibility, and report schema compatibility.
- Pre-check commands: `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260623-reviewer-neutral-iterative-review --stage draft --require-production-report --require-final-report`
- Post-check commands: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`
- Dependencies: Task 3.
- Files likely touched: `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/review-final.md`, `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md`, `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/final-report.md`, `.codex/work/20260623-reviewer-neutral-iterative-review/manifest.yaml`
- Writable scope: `.codex/work/20260623-reviewer-neutral-iterative-review/**`
- Output artifact: `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/review-final.md`
- Estimated scope: S

## Step-by-Step Plan
1. Run `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260623-reviewer-neutral-iterative-review/plan.md --mode light`.
2. Run `python3 plan2do/scripts/compile_execution.py .codex/work/20260623-reviewer-neutral-iterative-review/plan.md`.
3. Write `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/context-wave1.md` from the plan, spec, and reviewer skill sources.
4. Re-read `reviewer/SKILL.md` and `reviewer/references/review-report-template.md`.
5. Patch `reviewer/SKILL.md` near Core rule, Workflow, Verdicts, and Recheck Loop with neutral framing and bounded discovery guidance.
6. Patch `reviewer/references/review-report-template.md` only if `Residual Risks` wording needs convergence clarity.
7. Run `rg "first obvious|Issue Discovery|convergence|direct evidence|inference" reviewer/SKILL.md reviewer/references/review-report-template.md`.
8. Run `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`.
9. Run `python3 reviewer/scripts/validate_review_report.py --self-test`.
10. Write `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md` draft.
11. Write `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/final-report.md` draft with verification evidence.
12. Run `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`.
13. Run `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260623-reviewer-neutral-iterative-review --stage draft --require-production-report --require-final-report`.
14. Write `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/review-final.md` using reviewer v2 shape.
15. Run `python3 reviewer/scripts/validate_review_report.py .codex/work/20260623-reviewer-neutral-iterative-review/artifacts/review-final.md`.
16. Update `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md` with reviewer `PASS`.
17. Run `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`.
18. Mark execution tasks complete in `.codex/work/20260623-reviewer-neutral-iterative-review/execution/tasks.json` after artifacts exist.
19. Run `python3 plan2do/scripts/validate_execution.py .codex/work/20260623-reviewer-neutral-iterative-review`.
20. Update `.codex/work/20260623-reviewer-neutral-iterative-review/manifest.yaml` to stage `plan` with `canonical.plan: plan.md`.

## Parallelization
No implementation tasks should run in parallel because Task 2 changes reviewer workflow text and Task 3/4 depend on exact diffs. Read-only review of the final artifact can be isolated if reviewer subagent tooling is available.

## Files / Components Likely Affected
- `reviewer/SKILL.md`
- `reviewer/references/review-report-template.md`
- `.codex/work/20260623-reviewer-neutral-iterative-review/manifest.yaml`
- `.codex/work/20260623-reviewer-neutral-iterative-review/plan.md`
- `.codex/work/20260623-reviewer-neutral-iterative-review/execution/tasks.json`
- `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/context-wave1.md`
- `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/task1-execution.md`
- `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/task2-execution.md`
- `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/task3-verification.md`
- `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md`
- `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/review-final.md`
- `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/final-report.md`

## Owners / Responsibilities
- Primary agent: execute plan, edit docs, run deterministic validators, write artifacts, and perform final acceptance.
- Reviewer gate: independently check final documentation behavior and production evidence through reviewer report shape.
- User: no input required unless verification or review finds a scope decision outside the approved spec.

## Validation Plan
- `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260623-reviewer-neutral-iterative-review/plan.md --mode light`
- `python3 plan2do/scripts/compile_execution.py .codex/work/20260623-reviewer-neutral-iterative-review/plan.md`
- `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`
- `python3 reviewer/scripts/validate_review_report.py --self-test`
- `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
- `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260623-reviewer-neutral-iterative-review --stage draft --require-production-report --require-final-report`
- `python3 reviewer/scripts/validate_review_report.py .codex/work/20260623-reviewer-neutral-iterative-review/artifacts/review-final.md`
- `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-reviewer-neutral-iterative-review/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`
- `python3 plan2do/scripts/validate_execution.py .codex/work/20260623-reviewer-neutral-iterative-review`

## Rollout Plan
The rollout is immediate in-place skill documentation. Existing reviewer behavior changes for future invocations after file update. No runtime restart or deployment is required.

## Monitoring / Observability
Observe future reviewer outputs for convergence statements in `Residual Risks` or `Recheck Plan`, complete critical/major findings beyond the first issue, and explicit escalation to heavy or `BLOCK` when evidence is insufficient.

## Documentation / ADR Updates
ADR: Not needed. The change is localized skill workflow documentation and production artifacts capture the rationale.

## Rollback / Recovery Plan
If validation or review fails, patch only `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`, and workspace artifacts. To roll back the behavior change manually, revert the specific diff hunks in those reviewer Markdown files; keep workspace artifacts as execution history unless the user requests cleanup.

## Abort Criteria
- Abort if `quick_validate.py` fails after one repair attempt.
- Abort if reviewer report validator self-test fails after one repair attempt.
- Abort if the production report cannot validate draft or final after one repair attempt.
- Abort if final reviewer gate returns `BLOCK`.
- Abort if implementing the spec requires changing validator scripts, because that exceeds the approved v1 constraint.

## Risks
- Risk: guidance becomes too broad and forces heavy review everywhere. Mitigation: keep route preflight and bounded route limits explicit.
- Risk: convergence wording changes report schema. Mitigation: use existing `Residual Risks` and `Recheck Plan`.
- Risk: text becomes duplicative with introspector. Mitigation: import principles only, not verdict taxonomy or full workflow.
- Risk: reviewer still misses issues if wording is vague. Mitigation: add concrete issue-discovery loop and explicit first-obvious-finding prohibition.

## Open Questions
None blocking. The spec's open questions are resolved in this plan by keeping convergence in existing report sections and editing `reviewer/SKILL.md` first.

## Plan Self-Review
- Every task has exact writable scope and non-overlapping same-wave writes: yes.
- Every behavior change has regression or smoke coverage: yes, quick validation, reviewer self-test, scenario probe, production gate, and final review are specified.
- Every unknown is in `Assumptions` or `Open Questions`: yes.
- Rollback, abort criteria, and monitoring are specific enough for the risk level: yes.
- A fresh agent can execute Task 1 from this plan without raw transcript context: yes.

## Execution Decision
Proceed with primary-agent execution after plan validation. Do not use codex2codex because the user requested skills generally but did not request worker isolation.

## Execution Handoff

- Goal: update reviewer skill docs to require neutral evidence-first review and bounded issue discovery before final verdict.
- Current state: confirmed spec exists and this plan defines implementation, validation, production gate, and final reviewer gate.
- Authoritative artifacts: `.codex/work/20260623-reviewer-neutral-iterative-review/spec.md`, `.codex/work/20260623-reviewer-neutral-iterative-review/plan.md`, `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`, `skill-tokenless/references/skill-production-gate.md`.
- Decisions: keep report schema compatible, use existing `Residual Risks` and `Recheck Plan` for convergence, do not edit validator scripts.
- Verification: run all commands listed in `Validation Plan`.
- Remaining risks: final wording may need one bounded repair if reviewer gate finds ambiguity.
- Next action: run plan validator and execute Task 1.
- Suggested skills: `plan2do`, `structural-edit`, `skill-tokenless`, `reviewer`, `context-engineering`.
- Redactions / omitted raw data: no secrets or private raw logs included.
