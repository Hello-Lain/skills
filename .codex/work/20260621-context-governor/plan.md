# Decision-Grade Context Governor Implementation Plan

Mode: light  
Risk level: Low  
Confidence: High

## Goal

Rewrite `/data/lcq/.codex/skills/context-engineering/SKILL.md` into a lightweight Decision-Grade Context Governor that defines context states, compaction triggers, context capsules, decision-critical rehydration, anti-pollution rules, and best-effort compact fallback behavior.

## Non-Goals

- Do not implement a database, MCP server, hook, or live compaction service.
- Do not modify unrelated skills, Codex config, scripts, or historical artifacts.
- Do not guarantee direct `/compact` invocation from all Codex sessions.
- Do not create an implementation spec beyond this plan.

## Evidence Inspected

- `.codex/work/20260621-context-governor/spec.md`
- `.codex/work/20260621-context-governor/idea.md`
- `/data/lcq/.codex/skills/context-engineering/SKILL.md`
- `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- `/data/lcq/.codex/skills/references/artifact-contract.md`
- `git status --short`

## Spec Summary

The confirmed spec requires a `SKILL.md`-only rewrite that keeps normal work context lean and forces source-of-truth rehydration before risky decisions. Required capabilities: explicit context state model, compression triggers, context capsule, best-effort compact actuator policy, decision-critical triggers, rehydration rules, decision packet, anti-pollution rules, and verification checklist.

## Domain Language Check

Use the spec's terms exactly: `Context States`, `Compression Triggers`, `Context Capsule`, `COMPACT_NOW`, `Decision-Critical Triggers`, `Rehydration`, `Decision Packet`, `Anti-Pollution`, `source-of-truth`, `compressed summaries are continuity hints, not evidence`.

## Current Context

The existing `context-engineering/SKILL.md` is a tutorial-style document. It includes useful hierarchy, trust-level, focused-loading, conflict, and verification guidance, but only says to compact deliberately and does not define automatic timing, compaction fallback, or risk-decision rehydration.

## Assumptions

- V1 should keep the skill self-contained in `SKILL.md`.
- Mandatory `Decision Packet` is acceptable for high-risk or hard-to-reverse actions.
- Generic actuator language should mention verified local helpers without requiring them.
- Research, engineering, and idea workflows can share one governance loop.

## User Inputs Needed

None. The user explicitly requested plan generation followed by direct execution.

## Proposed Approach

Replace the current tutorial-style `SKILL.md` body with a concise governance workflow while preserving the durable useful concepts: context hierarchy, source trust, focused loading, conflict handling, and verification. Add operational templates for context capsules, compact fallback, and decision packets.

## Scenario Probes

- Long coding session with repeated failed tests: state becomes `bloated`; generate capsule; request/attempt compaction.
- Architecture/API decision after long exploration: state becomes `decision-critical`; rehydrate source files/specs/diffs; emit decision packet before action.
- Research conclusion from multiple papers/logs: quarantine speculative notes; rehydrate authoritative papers/results; emit decision packet.
- `/compact` unavailable: emit `COMPACT_NOW` with reason and capsule instead of claiming compaction succeeded.

## Dependency Graph

```text
spec.md + current SKILL.md
  -> plan.md
  -> rewrite context-engineering/SKILL.md
  -> grep/manual validation
```

## Task Breakdown

### Task 1: Rewrite context-engineering skill

- Description: Replace tutorial-style content with the Decision-Grade Context Governor workflow and required templates.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `SKILL.md` includes state model, compression triggers, context capsule, compact actuator policy, decision-critical triggers, rehydration rules, decision packet, anti-pollution rules, and verification.
- Verification: `rg -n "Context States|Compression Triggers|Context Capsule|COMPACT_NOW|Decision-Critical|Rehydration|Decision Packet|Anti-Pollution" context-engineering/SKILL.md`
- Dependencies: plan saved and validated.
- Files likely touched: `context-engineering/SKILL.md`
- Writable scope: `context-engineering/SKILL.md`
- Output artifact: `.codex/work/20260621-context-governor/artifacts/implementation.md`
- Estimated scope: M

### Task 2: Validate rewritten skill

- Description: Check the rewritten skill against spec acceptance criteria and inspect the diff for unrelated edits.
- Worker role: review
- Wave: 2
- Acceptance criteria: required sections are present, no unrelated files changed by implementation, and no claim that `/compact` is always callable.
- Verification: `rg` checks, targeted read of `context-engineering/SKILL.md`, and `git diff -- context-engineering/SKILL.md`.
- Dependencies: Task 1.
- Files likely touched: `.codex/work/20260621-context-governor/artifacts/validation.md`
- Writable scope: `.codex/work/20260621-context-governor/artifacts/validation.md`
- Output artifact: `.codex/work/20260621-context-governor/artifacts/validation.md`
- Estimated scope: S

## Step-by-Step Plan

1. Save this plan and update manifest lineage.
2. Validate the plan with `spec2plan/scripts/validate_plan_contract.py`.
3. Rewrite `context-engineering/SKILL.md` via `apply_patch`.
4. Run grep checks for required section names and critical phrases.
5. Read the rewritten skill to ensure templates and rules are complete.
6. Inspect the diff for only intended target changes.
7. Record implementation and validation notes under `.codex/work/20260621-context-governor/artifacts/`.

## Parallelization

Not applicable for implementation. Task 2 depends on Task 1. This is a single-file documentation rewrite, so parallel workers would add coordination overhead without value.

## Files / Components Likely Affected

- `context-engineering/SKILL.md`
- `.codex/work/20260621-context-governor/plan.md`
- `.codex/work/20260621-context-governor/manifest.yaml`
- `.codex/work/20260621-context-governor/artifacts/implementation.md`
- `.codex/work/20260621-context-governor/artifacts/validation.md`

## Owners / Responsibilities

- Main agent: write the plan, execute the single-file rewrite, validate, and report residual risks.
- User: review final behavior if they want stricter or looser decision gating.

## Validation Plan

- Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-context-governor/plan.md --mode light`.
- Run required phrase grep against `context-engineering/SKILL.md`.
- Inspect `git diff -- context-engineering/SKILL.md`.
- Confirm the rewritten skill says compressed summaries are continuity hints, not evidence.

## Rollout Plan

Immediate local rollout by updating `context-engineering/SKILL.md`. No deployment, package publish, or runtime restart is required.

## Monitoring / Observability

Manual observation only. Future sessions using the skill should show `Context Capsule`, `COMPACT_NOW`, and `Decision Packet` behavior at the expected trigger points.

## Documentation / ADR Updates

ADR: Not needed. This is a skill documentation/workflow rewrite, not an architectural repo decision.

## Rollback / Recovery Plan

If the rewrite is unsatisfactory, use `git diff -- context-engineering/SKILL.md` to isolate the change and apply a targeted corrective patch. Do not use destructive git reset because the repository has unrelated dirty changes.

## Abort Criteria

- `context-engineering/SKILL.md` has unexpected concurrent changes.
- Plan validator fails and cannot be fixed with a small patch.
- Acceptance grep cannot find required sections after rewrite.
- The rewrite would require modifying unrelated skills or config.

## Risks

- The rewritten skill may become too long. Mitigation: keep templates short and operational.
- The decision gate may feel too heavy. Mitigation: restrict mandatory packets to high-risk or hard-to-reverse actions.
- Compact automation may be overclaimed. Mitigation: require verified actuator and fallback `COMPACT_NOW`.

## Open Questions

- Whether to add a future `Research Mode` reference file.
- Whether to wire the local compaction helper in a later implementation.
- Whether destructive actions should always require user confirmation or only when rollback is unclear.

## Execution Decision

Execute now. The user explicitly requested generating the plan and directly executing it.

## Execution Handoff

- Goal: Rewrite `context-engineering/SKILL.md` into Decision-Grade Context Governor.
- Current state: Plan saved; spec confirmed; target skill currently tutorial-style.
- Authoritative artifacts: `.codex/work/20260621-context-governor/spec.md`, `.codex/work/20260621-context-governor/plan.md`.
- Decisions: Light mode; single-file v1; no hook/database/MCP implementation.
- Verification: Plan validator, required phrase grep, targeted read, target diff.
- Remaining risks: Potential over-process; compact automation must remain best-effort.
- Next action: Rewrite `context-engineering/SKILL.md` with `apply_patch`.
- Suggested skills: `apply-patch`, `git-workflow-and-versioning`.
- Redactions / omitted raw data: Raw GitHub research details and dirty unrelated git state are omitted; paths are cited instead.
