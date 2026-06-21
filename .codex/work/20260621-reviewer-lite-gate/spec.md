# Spec: Reviewer Lite Gate Integration

## Objective
Make `reviewer` the shared review capability for skill-produced artifacts, so `idea-refine`, `interview-me`, `spec2plan`, `plan2do`, and future skills can use a decoupled lightweight review gate instead of duplicating review logic.

## Users
- Primary: Codex agents modifying or running skills that produce artifacts requiring review.
- Secondary: Users who want to insert `reviewer` into a chosen skill or replace an existing skill-specific review step with `reviewer`.

## Problem
Review behavior is currently spread across several skills. This creates duplicate logic, uneven quality gates, and lower maintainability. The user wants `reviewer` to own review semantics while other skills only coordinate with it through a small integration contract. Future improvements to `reviewer` should automatically improve reliability for all skills that delegate review to it.

## Success Criteria
- `reviewer` documents a reusable integration guide for inserting or replacing review steps in any skill.
- `idea-refine`, `interview-me`, `spec2plan`, and `plan2do` explicitly call a `reviewer` lite gate for their relevant artifacts.
- Consumer skills do not copy reviewer rubrics or duplicate review report logic; they pass a compact review packet and consume `PASS`, `REVISE`, or `BLOCK`.
- `REVISE` triggers autonomous correction and focused re-review for at most three total self-repair cycles.
- `BLOCK` immediately stops the consumer workflow and reports the blocker instead of attempting self-repair.
- If three `REVISE` cycles fail to reach `PASS`, the workflow stops and identifies reviewer guidance, upstream contract ambiguity, or requirement conflict as the likely issue to fix.
- Existing hard gates remain authoritative: user confirmation, validators, executable checks, and real verification are not replaced by reviewer lite.

## Scope
### In
- Add `reviewer` guidance for generic skill integration: when to insert a lite gate, how to replace local review, packet shape, verdict handling, self-repair loop, escalation, and stop conditions.
- Update `idea-refine` to use reviewer lite before final direction artifact/save handoff.
- Update `interview-me` to use reviewer lite before treating a confirmed `spec.md` as ready for downstream planning.
- Update `spec2plan` to use reviewer lite around plan quality/self-review without replacing `validate_plan_contract.py`.
- Update `plan2do` to use reviewer for review/acceptance coordination without replacing task execution, verification commands, or `validate_execution.py`.
- Preserve `reviewer` route preflight: lite by default for small low-risk artifacts; escalate to heavy or blocked when evidence, risk, or source authority requires it.

### Out
- Do not modify every existing skill in v1.
- Do not make reviewer lite replace validators, tests, user approval, implementation execution, security review, data migration review, or production readiness gates.
- Do not require consumer skills to launch reviewer subagents for lite reviews.
- Do not allow infinite correction loops.
- Do not embed full reviewer rubrics into consumer skills.

## Requirements
### Functional
- `reviewer` must expose a "Lite Gate Integration" guide that future skills can follow.
- The guide must support two user requests:
  - Insert `reviewer` into a named skill at a chosen artifact boundary.
  - Replace a named skill's existing review step with `reviewer`.
- The guide must define a minimal review packet: source goal, artifact type, stage, artifact path or content, source contract, constraints, validators, allowed commands, and requested route.
- The guide must define the consumer state machine:
  - `PASS` -> continue workflow.
  - `REVISE` -> apply evidence-backed revision, then request focused recheck.
  - `BLOCK` -> stop workflow and report blocker.
- The guide must define a maximum of three self-repair cycles for `REVISE`.
- The guide must require consumers to stop after repeated failure and treat the failure as a review contract issue, reviewer guidance issue, or upstream requirement conflict needing correction.
- `idea-refine`, `interview-me`, `spec2plan`, and `plan2do` must reference `reviewer` as the review authority instead of implementing independent artifact review logic.
- Consumer skills must preserve their own domain responsibilities: ideation, interview confirmation, planning, execution, validation, and reporting.

### Non-Functional
- Decoupling: consumer skills should depend on a stable reviewer interface, not reviewer internals.
- Stability: a reviewer improvement should not require edits to every consumer unless the integration interface changes.
- Cost: lite review should stay inline, compact, and local by default.
- Safety: risky artifacts must escalate to reviewer heavy or stop as blocked.
- Clarity: reviewer findings must be actionable, evidence-backed, and specific enough for autonomous correction.

## Constraints
- Work occurs in the Codex skills workspace under `/data/lcq/.codex/skills`.
- Preserve existing skill behavior unless the change is needed for reviewer delegation.
- Do not remove existing validators or hard gates.
- Use Chinese or bilingual wording where the touched skill already uses Chinese-facing guidance only if consistent; otherwise keep existing skill language style.
- Keep integration guidance concise enough for skills to reference without bloating their own `SKILL.md`.

## Assumptions To Validate
- [ ] `reviewer` lite can be invoked inline by a consumer skill without launching a subagent - validate against `reviewer/SKILL.md` route rules.
- [ ] The four target skills have clear artifact boundaries where a lite gate can run - validate by reading each target `SKILL.md`.
- [ ] A three-cycle self-repair loop is acceptable for all four target skills - validate during plan/review against each skill's failure policy.
- [ ] Consumer skills can reference reviewer integration guidance instead of copying it - validate by checking final diffs for duplication.

## Risks
- Reviewer findings may be inaccurate or non-actionable - mitigate by requiring evidence, fix type, and consumer pushback when feedback is unsupported.
- Consumer skills may over-delegate and skip their own hard gates - mitigate by explicitly preserving validators, user confirmation, and execution verification.
- Lite review may be used for risky artifacts - mitigate with reviewer route preflight and mandatory escalation to heavy or blocked.
- Repeated self-repair may hide a broken reviewer contract - mitigate with the three-cycle stop rule and explicit reviewer-improvement blocker.
- Integration text may bloat target skills - mitigate by centralizing details in `reviewer` and using short references in consumers.

## Acceptance Checks
- Inspect `reviewer/SKILL.md` and any referenced reviewer docs to confirm the generic Lite Gate Integration guide exists.
- Inspect `idea-refine/SKILL.md`, `interview-me/SKILL.md`, `spec2plan/SKILL.md`, and `plan2do/SKILL.md` to confirm each delegates artifact review to `reviewer` using the shared interface.
- Confirm the four target skills define `PASS`, `REVISE`, and `BLOCK` handling consistently.
- Confirm `REVISE` has a maximum of three self-repair cycles and failed cycles stop the workflow.
- Confirm `BLOCK` stops immediately.
- Confirm validators and hard gates remain in place for `spec2plan` and `plan2do`.
- Confirm no target skill contains a copied full reviewer rubric or duplicate report template.
- Run any available skill validation or markdown/schema checks identified by the implementation plan.

## Open Questions
- None blocking. The exact file split for reviewer integration guidance can be chosen during planning to minimize `SKILL.md` bloat.
