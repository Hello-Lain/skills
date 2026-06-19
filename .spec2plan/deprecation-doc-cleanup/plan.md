# Extend Deprecation Skill With Documentation Cleanup

Mode: light
Risk level: Medium
Confidence: High

## Goal

Extend `deprecation-and-migration` so it also governs stale, temporary, redundant, and agent-generated documentation cleanup while preserving authoritative records.

## Non-Goals

- Do not perform broad cleanup of the `/data/lcq/.codex/skills` directory.
- Do not delete existing project documentation outside this skill update.
- Do not add heavyweight scripts unless the implementation shows a clear need.
- Do not change unrelated dirty files in `codex2codex/` or `spec2plan/`.

## Evidence Inspected

- `/data/lcq/.codex/skills/deprecation-and-migration/SKILL.md`
- `/data/lcq/.codex/skills/deprecation-and-migration/references/upstream.md`
- `/data/lcq/.codex/skills/.system/skill-creator/SKILL.md`
- `/data/lcq/.codex/skills/skill-tokenless/SKILL.md`
- `/data/lcq/.codex/skills/spec2plan/SKILL.md`
- `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- `/data/lcq/.codex/skills/codex2codex/SKILL.md`
- `/data/lcq/.codex/skills/git-workflow-and-versioning/SKILL.md`

## Spec Summary

The user wants the existing `deprecation-and-migration` skill expanded to cover cleanup, organization, and concise refinement of outdated, temporary, process, redundant, and result documents produced during agent work. The end goal is a clean directory with no redundant documentation.

## Domain Language Check

- Use the existing skill terms: deprecation, migration, consumers, compatibility constraints, rollback, completion criteria.
- Add consistent document lifecycle terms: authoritative, working, historical, stale, duplicate, temporary, archive, delete.
- Avoid treating all docs as disposable; docs with unique decisions, verification, or user-facing guidance remain authoritative or historical records.

## Current Context

`deprecation-and-migration/SKILL.md` is intentionally lean and delegates detail to `references/upstream.md`. The new doc-cleanup behavior should preserve that structure: trigger and core rules in `SKILL.md`, detailed workflow in `references/upstream.md`, concise metadata in `agents/openai.yaml`.

## Assumptions

- Documentation cleanup belongs in this skill because stale docs are retired artifacts with consumers and compatibility constraints.
- No deterministic script is needed in the first version.
- Existing `agents/openai.yaml` should remain aligned with the expanded trigger scope.
- Validation can be limited to skill validation plus targeted grep/read checks.

## User Inputs Needed

None. The user specified the target skill, desired capability, and executor skill.

## Proposed Approach

Update the skill as a lightweight extension:

1. Expand the frontmatter description and core rules in `SKILL.md`.
2. Add a concise documentation lifecycle cleanup section to `references/upstream.md`.
3. Update `agents/openai.yaml` so UI-facing metadata mentions doc cleanup.
4. Validate skill syntax and inspect the diff.

## Scenario Probes

- If asked to remove `old-plan.md`, the skill should require checking references and whether useful content was captured elsewhere before deletion.
- If duplicate summaries exist, the skill should prefer merging unique decisions into the authoritative doc before deleting duplicates.
- If a temporary agent artifact contains no unique information and has no references, the skill should allow deletion.
- If a doc is the only record of an ADR, verification, migration decision, or user-facing guide, the skill should preserve or archive it instead of deleting.

## Dependency Graph

Task 1 and Task 2 can run in parallel because they touch different files but must follow the same terminology. Task 3 depends on Task 1 so metadata matches the final trigger language. Task 4 reviews all outputs after implementation.

## Task Breakdown

### Task 1: Expand skill entrypoint triggers and core rules

- Description: Update `deprecation-and-migration/SKILL.md` frontmatter and core rules to include stale, temporary, redundant, and agent-generated documentation cleanup without bloating the entrypoint.
- Worker role: coding
- Wave: 1
- Acceptance criteria:
  - Frontmatter description explicitly triggers on documentation lifecycle cleanup.
  - Core rules include doc classification, merge-before-delete, and reference verification.
  - Existing migration/deprecation behavior remains intact.
- Verification: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/deprecation-and-migration && rg -n "documentation|stale|duplicate|temporary|authoritative|merge" /data/lcq/.codex/skills/deprecation-and-migration/SKILL.md`
- Dependencies: None
- Files likely touched:
  - `deprecation-and-migration/SKILL.md`
- Writable scope:
  - `deprecation-and-migration/SKILL.md`
- Output artifact: `.codex/specs/deprecation-doc-cleanup/artifacts/task-1-entrypoint.md`
- Estimated scope: S

### Task 2: Add detailed documentation cleanup workflow

- Description: Extend `deprecation-and-migration/references/upstream.md` with a compact workflow for cleaning stale, duplicate, temporary, process, and result docs safely.
- Worker role: coding
- Wave: 1
- Acceptance criteria:
  - Adds doc classification categories and actions: keep, merge, summarize, archive, delete.
  - Defines delete gates: no active references, no unique decision/verification/user-facing content, useful content captured elsewhere.
  - Covers agent process docs and result docs specifically.
  - Keeps the reference readable and avoids duplicating the entire entrypoint.
- Verification: `rg -n "Documentation Lifecycle|authoritative|temporary|duplicate|delete gates|merge|archive" /data/lcq/.codex/skills/deprecation-and-migration/references/upstream.md`
- Dependencies: None
- Files likely touched:
  - `deprecation-and-migration/references/upstream.md`
- Writable scope:
  - `deprecation-and-migration/references/upstream.md`
- Output artifact: `.codex/specs/deprecation-doc-cleanup/artifacts/task-2-reference.md`
- Estimated scope: S

### Task 3: Update skill UI metadata

- Description: Update `deprecation-and-migration/agents/openai.yaml` to reflect the expanded scope, keeping the prompt concise.
- Worker role: coding
- Wave: 2
- Acceptance criteria:
  - `short_description` or equivalent metadata mentions doc lifecycle cleanup.
  - Default prompt remains short and references `$deprecation-and-migration`.
  - YAML remains valid.
- Verification: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/deprecation-and-migration && rg -n "doc|documentation|cleanup|deprecation|migration" /data/lcq/.codex/skills/deprecation-and-migration/agents/openai.yaml`
- Dependencies: Task 1
- Files likely touched:
  - `deprecation-and-migration/agents/openai.yaml`
- Writable scope:
  - `deprecation-and-migration/agents/openai.yaml`
- Output artifact: `.codex/specs/deprecation-doc-cleanup/artifacts/task-3-metadata.md`
- Estimated scope: XS

### Task 4: Review expanded skill behavior

- Description: Review the modified skill for trigger coverage, token discipline, safety gates, validation, and absence of unrelated changes.
- Worker role: review
- Wave: 3
- Acceptance criteria:
  - Review states `Verdict: PASS` or `Verdict: FAIL`.
  - Findings include file/line references.
  - Confirms no broad doc deletion behavior was introduced without gates.
  - Confirms validation commands were run or explains why not.
- Verification: `git -C /data/lcq/.codex/skills diff -- deprecation-and-migration/SKILL.md deprecation-and-migration/references/upstream.md deprecation-and-migration/agents/openai.yaml && python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/deprecation-and-migration`
- Dependencies: Task 1, Task 2, Task 3
- Files likely touched:
  - `deprecation-and-migration/SKILL.md`
  - `deprecation-and-migration/references/upstream.md`
  - `deprecation-and-migration/agents/openai.yaml`
- Writable scope:
  - `.codex/specs/deprecation-doc-cleanup/review.md`
- Output artifact: `.codex/specs/deprecation-doc-cleanup/review.md`
- Estimated scope: S

## Step-by-Step Plan

1. Validate this plan with `spec2plan`.
2. Compile the plan with `codex2codex/scripts/plan_to_tasks.py`.
3. Run the generated waves with `codex2codex/scripts/run_plan.py`.
4. If worker execution is blocked, stop with the blocker instead of silently doing a single-agent fallback.
5. After execution, validate the skill and inspect the scoped diff.

## Parallelization

Wave 1 can run Task 1 and Task 2 concurrently because they write separate files. Wave 2 waits for Task 1 so metadata matches the final entrypoint. Wave 3 reviews after all implementation tasks finish.

## Files / Components Likely Affected

- `deprecation-and-migration/SKILL.md`
- `deprecation-and-migration/references/upstream.md`
- `deprecation-and-migration/agents/openai.yaml`
- `.codex/specs/deprecation-doc-cleanup/tasks.md`
- `.codex/specs/deprecation-doc-cleanup/review.md`
- `.codex/specs/deprecation-doc-cleanup/artifacts/*.md`

## Owners / Responsibilities

- Lead agent: generate/validate plan, run `codex2codex`, protect dirty tree, report final outcome.
- Coding workers: modify only assigned files and write task artifacts.
- Review worker: inspect scoped changes and write PASS/FAIL review.

## Validation Plan

- `python /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.spec2plan/deprecation-doc-cleanup/plan.md --mode light`
- `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/deprecation-and-migration`
- `rg -n "documentation|stale|duplicate|temporary|authoritative|merge|archive|delete" /data/lcq/.codex/skills/deprecation-and-migration`
- `git -C /data/lcq/.codex/skills diff -- deprecation-and-migration/SKILL.md deprecation-and-migration/references/upstream.md deprecation-and-migration/agents/openai.yaml`

## Rollout Plan

This is a local skill update. Rollout means the next Codex session can trigger the expanded skill from the updated frontmatter and use the new workflow.

## Monitoring / Observability

Monitor future usage for over-deletion risk. If agents delete docs too aggressively or ask too many questions, tighten the gates in `SKILL.md` or move more examples into `references/upstream.md`.

## Documentation / ADR Updates

ADR: Not needed. This is a skill behavior extension documented in the skill itself.

## Rollback / Recovery Plan

Revert only the scoped changes to:

- `deprecation-and-migration/SKILL.md`
- `deprecation-and-migration/references/upstream.md`
- `deprecation-and-migration/agents/openai.yaml`

Do not revert unrelated dirty files.

## Abort Criteria

- `codex2codex` cannot compile or run the plan.
- Worker attempts to edit outside writable scope.
- Skill validation fails after one fix attempt.
- Review returns `Verdict: FAIL` and the issue cannot be fixed safely in scope.

## Risks

- Trigger description may become too broad and fire on ordinary doc edits.
- Cleanup rules may encourage deleting useful historical records unless gates are explicit.
- Adding too much detail to `SKILL.md` would increase always-loaded context.

## Open Questions

None for this change.

## Execution Decision

Proceed with `codex2codex` execution after plan validation.

## Execution Handoff

- Goal: Extend `deprecation-and-migration` with safe stale/redundant/temporary documentation cleanup.
- Current state: Plan drafted; implementation not yet executed.
- Authoritative artifacts: `/data/lcq/.codex/skills/.spec2plan/deprecation-doc-cleanup/plan.md`
- Decisions: Keep `SKILL.md` lean; put detailed workflow in `references/upstream.md`; no script in first version.
- Verification: Run plan validator, skill validator, targeted `rg`, and scoped git diff.
- Remaining risks: Over-broad trigger or unsafe deletion guidance.
- Next action: Run `codex2codex/scripts/run_plan.py` with this plan.
- Suggested skills: `codex2codex`, `skill-creator`, `skill-tokenless`, `apply-patch`, `git-workflow-and-versioning`.
- Redactions / omitted raw data: No secrets or raw worker transcripts should be included in summaries.
