# Reviewer Lite Gate Integration Plan

Mode: light
Risk level: Medium
Confidence: High

## Goal
Implement the confirmed spec in `.codex/work/20260621-reviewer-lite-gate/spec.md` by making `reviewer` the shared lightweight review gate for target skill artifacts, updating four consumer skills to delegate artifact review through the shared interface, and recording debug-skill trace notes for optimization candidates.

## Non-Goals
- Do not modify every skill in `/data/lcq/.codex/skills`.
- Do not replace user confirmation, validators, execution checks, or production gates with reviewer lite.
- Do not change runtime scripts unless a validator proves a script mismatch.
- Do not launch `codex2codex`; the user requested primary execution through `plan2do`.

## Evidence Inspected
- `.codex/work/20260621-reviewer-lite-gate/spec.md`
- `.codex/work/20260621-reviewer-lite-gate/manifest.yaml`
- `reviewer/SKILL.md`
- `reviewer/references/review-report-template.md`
- `idea-refine/SKILL.md`
- `interview-me/SKILL.md`
- `spec2plan/SKILL.md`
- `spec2plan/references/plan-contract.md`
- `spec2plan/references/artifact-contract.md`
- `plan2do/SKILL.md`
- `debug-skill/SKILL.md`
- `debug-skill/references/report-template.md`
- `skill-tokenless/SKILL.md`
- `skill-tokenless/references/skill-production-gate.md`
- `spec2plan/scripts/validate_plan_contract.py`
- `plan2do/scripts/compile_execution.py`
- `reviewer/scripts/validate_review_report.py`
- `skill-tokenless/scripts/validate_skill_production.py`
- Command: `git status --short`
- Command: `find . -maxdepth 3 \( -name 'quick_validate.py' -o -name 'validate_*' -o -name '*validate*.py' -o -name 'compile_execution.py' -o -name 'pre_review_ready.py' \) -type f | sort`

## Spec Summary
`reviewer` must own shared review semantics. Consumer skills must pass compact packets to `reviewer-lite`, handle `PASS`, `REVISE`, and `BLOCK`, self-repair for at most three `REVISE` cycles, stop immediately on `BLOCK`, and preserve their own domain hard gates.

## Domain Language Check
- Canonical term: `reviewer-lite gate`.
- Canonical verdicts: `PASS`, `REVISE`, `BLOCK`.
- Canonical cycle limit: three total self-repair cycles for `REVISE`.
- Term conflict: current `reviewer/SKILL.md` says recheck stops after two unresolved cycles; implementation must preserve default reviewer behavior and add consumer-facing override only for the user-requested lite-gate integration contract.

## Current Context
- Worktree currently has untracked `.codex/work/20260621-reviewer-lite-gate/`.
- Target changes are documentation/workflow edits in Markdown skill files and one reviewer reference file.
- Material skill workflow changes require Skill Production Gate evidence, draft and final production reports, deterministic validators, scenario probing, and final reviewer gate.

## Implementation Map
- Files: `reviewer/SKILL.md` entrypoint; `reviewer/references/lite-gate-integration.md` shared integration guide; `idea-refine/SKILL.md`, `interview-me/SKILL.md`, `spec2plan/SKILL.md`, `plan2do/SKILL.md` consumer hooks; `.codex/work/20260621-reviewer-lite-gate/artifacts/debug-skill-trace.md`, `.codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md`, `.codex/work/20260621-reviewer-lite-gate/review.md` execution artifacts.
- Symbols / APIs: Markdown sections `Route Preflight`, `Recheck Loop`, `Rubric Routing`, `Output`, `Quality Gates`, `Resources`, `Workflow`, `Completion`; script CLIs `spec2plan/scripts/validate_plan_contract.py`, `plan2do/scripts/compile_execution.py`, `plan2do/scripts/pre_review_ready.py`, `plan2do/scripts/validate_execution.py`, `reviewer/scripts/validate_review_report.py`, `skill-tokenless/scripts/validate_skill_production.py`.
- Tests: `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-reviewer-lite-gate/plan.md --mode light`; `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-reviewer-lite-gate/plan.md`; `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-reviewer-lite-gate/review.md`; `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`; `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`; `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-reviewer-lite-gate`.
- Commands: `git diff --check -- reviewer idea-refine interview-me spec2plan plan2do .codex/work/20260621-reviewer-lite-gate`; `rg -n "reviewer-lite|PASS|REVISE|BLOCK|three" reviewer idea-refine interview-me spec2plan plan2do`; `python3 debug-skill/scripts/skill_audit_core.py --self-test`; `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`.
- Data / migration impact: Not applicable; only Markdown skill guidance and `.codex/work/20260621-reviewer-lite-gate/` artifacts are written.

## Assumptions
- `reviewer` lite can stay inline by default because `reviewer/SKILL.md` explicitly allows inline lite reviews.
- A separate reviewer reference file is the cleanest way to centralize integration details and prevent consumer skill bloat.
- Final reviewer gate should use heavy routing because the work changes workflow contracts across multiple skills.
- The debug-skill trace can be an execution artifact that records skill-trigger decisions, friction, and candidate improvements without modifying `debug-skill`.

## User Inputs Needed
- None; the user confirmed the spec and requested execution.

## Proposed Approach
Add a shared `reviewer` integration guide, patch each consumer skill with short references to that guide, execute deterministic validation and production reporting, run a final reviewer gate, then capture debug-skill observations for future optimization.

## Scenario Probes
- Scenario 1: A future user says “insert reviewer into skill X”; expected result is that the agent reads `reviewer/references/lite-gate-integration.md`, chooses an artifact boundary, and inserts a compact gate without copying reviewer rubrics.
- Scenario 2: `idea-refine` produces `idea.md`; expected result is a `reviewer-lite` packet before final artifact acceptance, with `REVISE` self-repair capped at three cycles and `BLOCK` stopping.
- Scenario 3: `spec2plan` produces `plan.md`; expected result is reviewer lite around plan quality while `validate_plan_contract.py` remains a hard gate.
- Scenario 4: `plan2do` completes execution; expected result is reviewer coordination after verification, while `validate_execution.py` and command evidence remain hard gates.

## Dependency Graph
- Task 1 creates the shared reviewer integration surface.
- Tasks 2, 3, 4, and 5 depend on Task 1.
- Task 6 depends on Tasks 1 through 5.
- Task 7 depends on Task 6 draft production evidence.
- Final acceptance updates production and final reports after Task 7 reviewer verdict.

## Task Breakdown
### Task 1: Add reviewer integration guide

- Description: Add the shared reviewer-lite integration contract and link it from the reviewer entrypoint.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `reviewer` documents insertion, replacement, packet shape, verdict handling, three-cycle `REVISE`, immediate `BLOCK`, escalation, and consumer pushback.
- Verification: `rg -n "Lite Gate Integration|reviewer-lite|PASS|REVISE|BLOCK|three" reviewer/SKILL.md reviewer/references/lite-gate-integration.md`
- Concrete edits: Create `reviewer/references/lite-gate-integration.md`; add one concise reference in `reviewer/SKILL.md`.
- Interfaces / contracts changed: Adds stable consumer integration interface for skill review delegation.
- Test cases: Manual check: compare guide bullets against `.codex/work/20260621-reviewer-lite-gate/spec.md` Success Criteria.
- Pre-check commands: `sed -n '1,180p' reviewer/SKILL.md`
- Post-check commands: `rg -n "Lite Gate Integration|reviewer-lite|three|BLOCK" reviewer`
- Dependencies: None.
- Files likely touched: `reviewer/SKILL.md`, `reviewer/references/lite-gate-integration.md`
- Writable scope: `reviewer/SKILL.md`, `reviewer/references/lite-gate-integration.md`
- Output artifact: `.codex/work/20260621-reviewer-lite-gate/artifacts/task1-reviewer-guide.md`
- Estimated scope: S

### Task 2: Patch idea-refine gate

- Description: Add a compact consumer hook so `idea-refine` routes final direction artifacts through reviewer lite before save or handoff.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `idea-refine` preserves its exit gate, save confirmation, and direction-only boundary while delegating artifact review to `reviewer-lite`.
- Verification: `rg -n "reviewer-lite|REVISE|BLOCK|lite-gate-integration" idea-refine/SKILL.md`
- Concrete edits: Add a short reviewer-lite gate rule near `Mandatory Exit Gate` or `Verification`.
- Interfaces / contracts changed: `idea-refine` consumes reviewer verdict interface and does not copy reviewer report template.
- Test cases: Manual check: confirm target user, success criteria, variations, clusters, assumptions, MVP, Not Doing, and save prompt still remain required.
- Pre-check commands: `sed -n '120,235p' idea-refine/SKILL.md`
- Post-check commands: `rg -n "Mandatory Exit Gate|reviewer-lite|Save-confirm|Not Doing" idea-refine/SKILL.md`
- Dependencies: Task 1.
- Files likely touched: `idea-refine/SKILL.md`
- Writable scope: `idea-refine/SKILL.md`
- Output artifact: `.codex/work/20260621-reviewer-lite-gate/artifacts/task2-idea-refine.md`
- Estimated scope: XS

### Task 3: Patch interview-me gate

- Description: Add a compact consumer hook so `interview-me` routes confirmed spec artifacts through reviewer lite after explicit user approval and before downstream readiness.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `interview-me` preserves one-question flow, explicit yes, automatic save behavior, and spec quality rubric while delegating artifact review to `reviewer-lite`.
- Verification: `rg -n "reviewer-lite|REVISE|BLOCK|lite-gate-integration" interview-me/SKILL.md`
- Concrete edits: Add a short reviewer-lite gate rule near `Produce The Spec`, `Save / Hand Off`, or `Quality Gates`.
- Interfaces / contracts changed: `interview-me` consumes reviewer verdict interface and does not copy reviewer report template.
- Test cases: Manual check: confirm explicit `yes` remains mandatory before final spec authority.
- Pre-check commands: `sed -n '90,179p' interview-me/SKILL.md`
- Post-check commands: `rg -n "explicit|reviewer-lite|spec-quality-rubric|Quality Gates" interview-me/SKILL.md`
- Dependencies: Task 1.
- Files likely touched: `interview-me/SKILL.md`
- Writable scope: `interview-me/SKILL.md`
- Output artifact: `.codex/work/20260621-reviewer-lite-gate/artifacts/task3-interview-me.md`
- Estimated scope: XS

### Task 4: Patch spec2plan gate

- Description: Add reviewer-lite coordination around plan quality while keeping `validate_plan_contract.py` as the hard plan gate.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `spec2plan` references reviewer-lite for artifact quality, preserves plan validator, preserves heavy mode rules, and preserves Skill Production Gate requirements.
- Verification: `rg -n "reviewer-lite|validate_plan_contract.py|Skill Production Gate|REVISE|BLOCK|lite-gate-integration" spec2plan/SKILL.md`
- Concrete edits: Add a short reviewer-lite gate rule near `Resources`, `Light Workflow`, or `Planning Rules`.
- Interfaces / contracts changed: `spec2plan` consumes reviewer verdict interface after deterministic plan validation evidence exists.
- Test cases: Manual check: confirm `scripts/validate_plan_contract.py <plan.md> --mode light|heavy` remains a hard gate.
- Pre-check commands: `sed -n '16,97p' spec2plan/SKILL.md`
- Post-check commands: `rg -n "validate_plan_contract.py|reviewer-lite|Skill Production Gate" spec2plan/SKILL.md`
- Dependencies: Task 1.
- Files likely touched: `spec2plan/SKILL.md`
- Writable scope: `spec2plan/SKILL.md`
- Output artifact: `.codex/work/20260621-reviewer-lite-gate/artifacts/task4-spec2plan.md`
- Estimated scope: XS

### Task 5: Patch plan2do gate

- Description: Add reviewer delegation for execution acceptance while keeping verification commands, bounded rework, production gates, and execution validation authoritative.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `plan2do` delegates non-trivial review through reviewer, preserves execution ownership, preserves `validate_execution.py`, and preserves Skill Production Gate requirements.
- Verification: `rg -n "reviewer-lite|reviewer|validate_execution.py|Skill Production Gate|REVISE|BLOCK|lite-gate-integration" plan2do/SKILL.md`
- Concrete edits: Add a short reviewer delegation rule near `Primary-Agent Workflow`, `Quality Gates`, or `Rework`.
- Interfaces / contracts changed: `plan2do` consumes reviewer verdict interface after task verification evidence exists.
- Test cases: Manual check: confirm false completion remains forbidden after failed verification or failed review.
- Pre-check commands: `sed -n '1,78p' plan2do/SKILL.md`
- Post-check commands: `rg -n "validate_execution.py|reviewer|false completion|Skill Production Gate" plan2do/SKILL.md`
- Dependencies: Task 1.
- Files likely touched: `plan2do/SKILL.md`
- Writable scope: `plan2do/SKILL.md`
- Output artifact: `.codex/work/20260621-reviewer-lite-gate/artifacts/task5-plan2do.md`
- Estimated scope: XS

### Task 6: Validate and draft production evidence

- Description: Run deterministic checks, write task evidence, update debug-skill trace, and save draft production report before final review.
- Worker role: coding
- Wave: 3
- Acceptance criteria: Validation commands complete or record concrete blockers; draft production report validates with stage `draft`; draft final report exists; debug-skill trace names skill usage, friction, and candidate optimization points.
- Verification: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
- Concrete edits: Write `.codex/work/20260621-reviewer-lite-gate/artifacts/task6-validation.md`, `.codex/work/20260621-reviewer-lite-gate/artifacts/debug-skill-trace.md`, `.codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md`, and `.codex/work/20260621-reviewer-lite-gate/artifacts/final-report.md`.
- Interfaces / contracts changed: Production report records Behavior Lock, Token Budget, Deterministic Validators, Scenario Gate, Reviewer Gate placeholder, Reuse Attribution, Changed Files, and Residual Risks.
- Test cases: Run `python3 debug-skill/scripts/skill_audit_core.py --self-test` and `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`.
- Pre-check commands: `git diff --check -- reviewer idea-refine interview-me spec2plan plan2do .codex/work/20260621-reviewer-lite-gate`
- Post-check commands: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
- Dependencies: Task 1, Task 2, Task 3, Task 4, Task 5.
- Files likely touched: `.codex/work/20260621-reviewer-lite-gate/artifacts/task6-validation.md`, `.codex/work/20260621-reviewer-lite-gate/artifacts/debug-skill-trace.md`, `.codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md`, `.codex/work/20260621-reviewer-lite-gate/artifacts/final-report.md`
- Writable scope: `.codex/work/20260621-reviewer-lite-gate/artifacts/task6-validation.md`, `.codex/work/20260621-reviewer-lite-gate/artifacts/debug-skill-trace.md`, `.codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md`, `.codex/work/20260621-reviewer-lite-gate/artifacts/final-report.md`
- Output artifact: `.codex/work/20260621-reviewer-lite-gate/artifacts/task6-validation.md`
- Estimated scope: M

### Task 7: Run reviewer gate

- Description: Run final reviewer gate on the changed skill artifacts and production evidence, saving the review report.
- Worker role: review
- Wave: 4
- Acceptance criteria: `.codex/work/20260621-reviewer-lite-gate/review.md` contains one top-level `Verdict:` and passes `reviewer/scripts/validate_review_report.py`; `PASS` continues, `REVISE` triggers bounded rework, and `BLOCK` stops.
- Verification: `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-reviewer-lite-gate/review.md`
- Concrete edits: Write `.codex/work/20260621-reviewer-lite-gate/review.md` and record reviewer cleanup status.
- Interfaces / contracts changed: Reviewer verdict becomes final acceptance input for `plan2do` completion.
- Test cases: Manual check: compare review findings against `.codex/work/20260621-reviewer-lite-gate/spec.md`, `skill-tokenless/references/skill-production-gate.md`, and changed files.
- Pre-check commands: `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-reviewer-lite-gate --stage draft --require-production-report --require-final-report`
- Post-check commands: `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-reviewer-lite-gate/review.md`
- Dependencies: Task 6.
- Files likely touched: `.codex/work/20260621-reviewer-lite-gate/review.md`
- Writable scope: `.codex/work/20260621-reviewer-lite-gate/review.md`
- Output artifact: `.codex/work/20260621-reviewer-lite-gate/review.md`
- Estimated scope: S

## Step-by-Step Plan
1. Run `sed -n '1,180p' reviewer/SKILL.md` and add `reviewer/references/lite-gate-integration.md`.
2. Patch `reviewer/SKILL.md` with a reference to `reviewer/references/lite-gate-integration.md`.
3. Patch `idea-refine/SKILL.md` with the reviewer-lite handoff before final artifact acceptance.
4. Patch `interview-me/SKILL.md` with the reviewer-lite handoff after explicit `yes` and spec quality review.
5. Patch `spec2plan/SKILL.md` with reviewer-lite coordination while keeping `spec2plan/scripts/validate_plan_contract.py`.
6. Patch `plan2do/SKILL.md` with reviewer delegation while keeping `plan2do/scripts/validate_execution.py`.
7. Run `git diff --check -- reviewer idea-refine interview-me spec2plan plan2do .codex/work/20260621-reviewer-lite-gate`.
8. Write `.codex/work/20260621-reviewer-lite-gate/artifacts/debug-skill-trace.md`.
9. Write `.codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md`.
10. Run `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`.
11. Run `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-reviewer-lite-gate --stage draft --require-production-report --require-final-report`.
12. Save final review to `.codex/work/20260621-reviewer-lite-gate/review.md`.
13. Run `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-reviewer-lite-gate/review.md`.
14. Update `.codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md` and `.codex/work/20260621-reviewer-lite-gate/artifacts/final-report.md` after reviewer `PASS`.
15. Run `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-reviewer-lite-gate`.
16. Run `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`.

## Parallelization
- Wave 1 must run first because it creates `reviewer/references/lite-gate-integration.md`.
- Wave 2 tasks can run in parallel because `idea-refine/SKILL.md`, `interview-me/SKILL.md`, `spec2plan/SKILL.md`, and `plan2do/SKILL.md` have disjoint writable scopes.
- Waves 3 and 4 must run sequentially because production evidence and review verdict depend on prior artifacts.

## Files / Components Likely Affected
- `reviewer/SKILL.md`
- `reviewer/references/lite-gate-integration.md`
- `idea-refine/SKILL.md`
- `interview-me/SKILL.md`
- `spec2plan/SKILL.md`
- `plan2do/SKILL.md`
- `.codex/work/20260621-reviewer-lite-gate/manifest.yaml`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/debug-skill-trace.md`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/final-report.md`
- `.codex/work/20260621-reviewer-lite-gate/review.md`

## Owners / Responsibilities
- Primary agent: execute edits, run validators, maintain artifacts, and stop on failed hard gates.
- Reviewer gate: judge changed skill artifacts and production evidence from source contracts.
- Debug-skill tracking: record skill-trigger timeline, friction, and optimization candidates without editing `debug-skill`.

## Validation Plan
- `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-reviewer-lite-gate/plan.md --mode light`
- `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-reviewer-lite-gate/plan.md`
- `git diff --check -- reviewer idea-refine interview-me spec2plan plan2do .codex/work/20260621-reviewer-lite-gate`
- `rg -n "reviewer-lite|PASS|REVISE|BLOCK|lite-gate-integration" reviewer idea-refine interview-me spec2plan plan2do`
- `python3 debug-skill/scripts/skill_audit_core.py --self-test`
- `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`
- `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
- `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260621-reviewer-lite-gate --stage draft --require-production-report --require-final-report`
- `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-reviewer-lite-gate/review.md`
- `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-reviewer-lite-gate`
- `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`

## Rollout Plan
- Local skill docs change only in `/data/lcq/.codex/skills`.
- Rollout occurs when the working tree changes are accepted by the user.
- No package install, service restart, or deployment step is required.

## Monitoring / Observability
- Use `.codex/work/20260621-reviewer-lite-gate/artifacts/debug-skill-trace.md` to record skill workflow friction and optimization candidates.
- Use `.codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md` for production gate evidence.
- Use `.codex/work/20260621-reviewer-lite-gate/review.md` for reviewer verdict.

## Documentation / ADR Updates
ADR: Not needed
The shared reviewer integration guide is the documentation update; no architecture decision record is needed because this is local skill workflow guidance.

## Rollback / Recovery Plan
- Revert edits to `reviewer/SKILL.md`, `reviewer/references/lite-gate-integration.md`, `idea-refine/SKILL.md`, `interview-me/SKILL.md`, `spec2plan/SKILL.md`, and `plan2do/SKILL.md` from the working tree if validators or reviewer gate block.
- Preserve `.codex/work/20260621-reviewer-lite-gate/` artifacts for audit unless the user requests cleanup.
- If reviewer returns `REVISE`, patch only the cited files and rerun focused checks.
- If reviewer returns `BLOCK`, stop and report the blocking source conflict or missing evidence.

## Abort Criteria
- `spec2plan/scripts/validate_plan_contract.py` fails after one plan repair cycle.
- `skill-tokenless/scripts/validate_skill_production.py` fails after one production report repair cycle.
- `reviewer` returns `BLOCK`.
- Three `REVISE` cycles fail to produce reviewer `PASS`.
- A validator reveals script behavior that conflicts with the planned skill text.

## Risks
- Consumer skill text may copy too much reviewer detail; mitigation is central guide plus short references.
- The reviewer recheck cycle limit may conflict with existing reviewer default text; mitigation is explicit consumer integration contract plus preserved reviewer default.
- Production gate may require evidence not available from Markdown-only changes; mitigation is scenario probes and explicit skipped-command reasons.
- Final heavy review may be unavailable; mitigation is stop with blocker rather than downgrading silently.

## Open Questions
- None blocking.

## Plan Self-Review
- Exact writable scope: every task has concrete writable scope; same-wave writes are disjoint for Wave 2.
- Coverage: behavior changes have smoke coverage through `rg`, `git diff --check`, production report validation, execution validation, and reviewer report validation.
- Unknown handling: no hidden unknown remains in task text; any runtime reviewer availability failure becomes a blocker.
- Rollback: rollback and abort criteria name exact files and commands for the risk level.
- Task 1 fresh-agent readiness: a fresh agent can start with `reviewer/SKILL.md`, `reviewer/references/lite-gate-integration.md`, and `.codex/work/20260621-reviewer-lite-gate/spec.md`.

## Execution Decision
Proceed with primary-agent `plan2do` execution after this plan passes `spec2plan/scripts/validate_plan_contract.py --mode light` and `plan2do/scripts/compile_execution.py`.

## Execution Handoff

- Goal: Implement reviewer-lite gate integration across `reviewer`, `idea-refine`, `interview-me`, `spec2plan`, and `plan2do`.
- Current state: `.codex/work/20260621-reviewer-lite-gate/spec.md` is confirmed; this `plan.md` is the executable handoff after validation.
- Authoritative artifacts: `.codex/work/20260621-reviewer-lite-gate/spec.md`, `.codex/work/20260621-reviewer-lite-gate/plan.md`, `skill-tokenless/references/skill-production-gate.md`, `reviewer/SKILL.md`.
- Decisions: Use light spec2plan planning, primary-agent plan2do execution, centralized reviewer guide, short consumer references, final reviewer gate, and debug-skill trace artifact.
- Verification: Run the commands listed in `Validation Plan` and stop on failed hard gates.
- Remaining risks: Reviewer heavy route may be unavailable; integration wording may need one focused rework cycle after reviewer feedback.
- Next action: Run `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-reviewer-lite-gate/plan.md --mode light`.
- Suggested skills: `plan2do`, `reviewer`, `debug-skill`, `skill-tokenless`, `context-engineering`, `edit-orchestration`.
- Redactions / omitted raw data: Raw command logs and future reviewer transcripts should stay in `.codex/work/20260621-reviewer-lite-gate/artifacts/`.
