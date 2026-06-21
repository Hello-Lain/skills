# Skill Tokenless Workflow Upgrade Plan

Mode: light
Risk level: Low
Confidence: High

## Goal

Upgrade `skill-tokenless` using lessons from `writing-skills`: make token reduction test-driven, move rare validation detail out of always-loaded context, shorten discovery text, and preserve behavior.

## Non-Goals

No new runtime integration, no external service calls in validation, no changes outside `skill-tokenless/` except generated artifact directories under `.codex/specs/skill-tokenless-tokenless/`.

## Evidence Inspected

- `/data/lcq/.codex/skills/skill-tokenless/SKILL.md`
- `/data/lcq/.codex/skills/skill-tokenless/agents/openai.yaml`
- `https://github.com/obra/superpowers/tree/main/skills%2Fwriting-skills`
- `https://github.com/obra/superpowers/blob/main/skills/writing-skills/testing-skills-with-subagents.md`
- `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- `git status --short` showed clean repo before plan creation.
- `codegraph` unavailable; used targeted reads and file search.

## Spec Summary

User requested a `spec2plan` plan followed by execution. Prior analysis identified improvements: frontmatter should be trigger-only, `Scenario Gate` should become RED-GREEN-REFACTOR, long testing/validation guidance should move to references, and `SKILL.md` should stay a compact entrypoint.

## Domain Language Check

Use existing local terms: `SKILL.md`, `agents/openai.yaml`, `references/`, `Scenario Gate`, `Behavior Preservation`, `quick_validate.py`, `RED-GREEN-REFACTOR`, `micro-test`, `rationalization`, `progressive disclosure`.

## Current Context

`skill-tokenless` has only `SKILL.md` and `agents/openai.yaml`. `SKILL.md` is 148 lines and 1159 words. No local `references/` exist. The repo is clean before generated plan/artifact paths.

## Assumptions

- The skill remains a Codex skill with hyphen-case name.
- Long, conditional detail can move to `references/` without behavior loss because Codex skill loading supports progressive disclosure.
- A mock scenario gate is sufficient because no live systems or secrets are involved.

## User Inputs Needed

Not applicable: user already requested planning and execution; local context is sufficient.

## Proposed Approach

Create a compact main `SKILL.md` that states the contract, workflow, routing to references, hard stops, and minimal validation. Add references for testing and validation details. Keep `agents/openai.yaml` short. Validate with `quick_validate.py`, counts, grep gates, explicit cleanup command, and diff review.

## Scenario Probes

- RED probe: existing skill has post-edit Scenario Gate but no explicit pre-edit RED baseline; upgraded skill must require RED for material changes.
- GREEN probe: edited skill must route material changes to `references/testing.md`.
- Non-scenario probe: pure command/reference lookup should not trigger `skill-tokenless`.
- Cleanup probe: `.tmp-forward-test` must not remain.

## Dependency Graph

Plan validation -> main rewrite -> reference extraction -> validation/review.

## Task Breakdown

### Task 1: Write and validate execution plan

- Description: Create `skill-tokenless/plan.md` under the spec2plan contract.
- Worker role: coding
- Wave: 1
- Acceptance criteria: Plan has all required sections, executable tasks, and validation passes.
- Verification: `python /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/skill-tokenless/plan.md --mode light`
- Dependencies: None
- Files likely touched: `skill-tokenless/plan.md`, `.codex/specs/skill-tokenless-tokenless/artifacts/plan.md`
- Writable scope: `skill-tokenless/plan.md`
- Output artifact: `.codex/specs/skill-tokenless-tokenless/artifacts/task1-plan.md`
- Estimated scope: S

### Task 2: Rewrite main skill entrypoint

- Description: Shorten frontmatter and `SKILL.md`; preserve behavior while routing detailed testing/validation to references.
- Worker role: coding
- Wave: 2
- Acceptance criteria: Main skill keeps triggers, non-negotiables, workflow, hard stops, and report contract; wording no longer embeds long scenario/validation blocks.
- Verification: `wc -l skill-tokenless/SKILL.md skill-tokenless/agents/openai.yaml && wc -w skill-tokenless/SKILL.md && rg "RED|Behavior Lock|quick_validate|Hard Stops|references/testing.md" skill-tokenless/SKILL.md`
- Dependencies: Task 1
- Files likely touched: `skill-tokenless/SKILL.md`, `skill-tokenless/agents/openai.yaml`
- Writable scope: `skill-tokenless/SKILL.md`
- Output artifact: `.codex/specs/skill-tokenless-tokenless/artifacts/task2-entrypoint.md`
- Estimated scope: S

### Task 3: Add progressive-disclosure references

- Description: Add `references/testing.md` and `references/validation.md` for TDD-style skill testing, behavior preservation, validation commands, and fallback diff checks.
- Worker role: coding
- Wave: 3
- Acceptance criteria: References cover RED-GREEN-REFACTOR, micro-tests, scenario gate pass criteria, behavior lock checklist, validation commands, cleanup, and diff inspection.
- Verification: `rg "RED|GREEN|REFACTOR|micro-test|Behavior Lock|quick_validate|git -C" skill-tokenless/references`
- Dependencies: Task 2
- Files likely touched: `skill-tokenless/references/testing.md`, `skill-tokenless/references/validation.md`
- Writable scope: `skill-tokenless/references/`
- Output artifact: `.codex/specs/skill-tokenless-tokenless/artifacts/task3-references.md`
- Estimated scope: S

### Task 4: Validate, inspect, and record results

- Description: Run skill validator, counts, grep gates, explicit cleanup command, and diff inspection; record result artifact.
- Worker role: review
- Wave: 4
- Acceptance criteria: Validator passes; counts are reported; required gates are discoverable; no `.tmp-forward-test` remains; diff shows no behavior-loss risk.
- Verification: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/skill-tokenless && rtk proxy bash -lc 'test ! -e "$1/.tmp-forward-test"' _ /data/lcq/.codex/skills/skill-tokenless && git -C /data/lcq/.codex/skills diff -- skill-tokenless`
- Dependencies: Tasks 2 and 3
- Files likely touched: `.codex/specs/skill-tokenless-tokenless/artifacts/task4-validation.md`
- Writable scope: `.codex/specs/skill-tokenless-tokenless/artifacts/task4-validation.md`
- Output artifact: `.codex/specs/skill-tokenless-tokenless/artifacts/task4-validation.md`
- Estimated scope: S

## Step-by-Step Plan

1. Validate this plan.
2. Patch `SKILL.md` into a compact entrypoint with trigger-only description and explicit reference routing.
3. Patch `agents/openai.yaml` only if the default prompt needs a shorter wording.
4. Add `references/testing.md` and `references/validation.md`.
5. Run validator, counts, grep gates, explicit cleanup command, and diff review.
6. Report changed files, count delta, preserved gates, validation results, and residual risks.

## Parallelization

Sequential only. Task 3 depends on Task 2 reference names; Task 4 depends on all edits. No same-wave writable overlap.

## Files / Components Likely Affected

- `skill-tokenless/SKILL.md`
- `skill-tokenless/agents/openai.yaml`
- `skill-tokenless/references/testing.md`
- `skill-tokenless/references/validation.md`
- `skill-tokenless/plan.md`
- `.codex/specs/skill-tokenless-tokenless/artifacts/`

## Owners / Responsibilities

Main agent owns all tasks. No subagents needed for this low-risk local documentation refactor.

## Validation Plan

- `python /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/skill-tokenless/plan.md --mode light`
- `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/skill-tokenless`
- `wc -l /data/lcq/.codex/skills/skill-tokenless/SKILL.md /data/lcq/.codex/skills/skill-tokenless/agents/openai.yaml`
- `wc -w /data/lcq/.codex/skills/skill-tokenless/SKILL.md`
- `rg "RED|GREEN|REFACTOR|micro-test|Behavior Lock|quick_validate|Hard Stops" /data/lcq/.codex/skills/skill-tokenless`
- `rtk proxy bash -lc 'test ! -e "$1/.tmp-forward-test"' _ /data/lcq/.codex/skills/skill-tokenless`
- `git -C /data/lcq/.codex/skills diff -- skill-tokenless`

## Rollout Plan

Local documentation-only rollout. No deployment. The edited skill becomes active in future sessions after file save.

## Monitoring / Observability

Not applicable: no runtime service. Future observation is via Skill Monitor incidents and scenario-gate results when `skill-tokenless` is used.

## Documentation / ADR Updates

ADR: Not needed. Change is local skill documentation structure, not an architectural decision.

## Rollback / Recovery Plan

Use git diff to inspect and selectively revert only this task's files if validation reveals behavior loss. Do not run destructive git reset/checkout.

## Abort Criteria

- `quick_validate.py` fails after one repair attempt.
- Behavior preservation checklist cannot be represented after compression.
- Patch context diverges unexpectedly in touched files.

## Risks

- Over-compression could hide required validation gates.
- Moving detail to references could make agents skip required testing unless routing is explicit.
- Scenario gate is documented but not run through a live subagent in this execution.

## Open Questions

None.

## Execution Decision

Proceed now per user request.

## Execution Handoff

- Goal: Upgrade `skill-tokenless` workflow and docs using `writing-skills` lessons.
- Current state: Plan created; implementation pending.
- Authoritative artifacts: `skill-tokenless/plan.md`
- Decisions: Light mode; sequential execution; references for rare details.
- Verification: Run plan validator, skill validator, counts, grep gates, explicit cleanup command, diff review.
- Remaining risks: Mock/documentation validation only; no live subagent pressure run unless later requested.
- Next action: Validate plan, then patch `skill-tokenless`.
- Suggested skills: `spec2plan`, `skill-tokenless`, `edit-orchestration`, `git-workflow-and-versioning`.
- Redactions / omitted raw data: No secrets or private logs included.
