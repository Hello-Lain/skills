---
name: plan-grill
description: "Use when the user wants a production-grade plan.md, wants to upgrade an initial plan.md, or asks for a safer replacement for ordinary planning. Produces or iterates a plan document through subagent-first planning, stress review, synthesis, and main-agent acceptance. Does not execute by default; the user decides whether and how to execute the final plan."
metadata:
  short-description: "Generate and harden production plan.md"
---

# Plan Grill

Plan Grill is a production-grade `plan.md` generator and plan hardening workflow.

Default outcome:

```text
final plan.md, not execution
```

Use this skill to create a new plan document or improve an existing one. The user decides whether and how to execute the final plan.

## Core Contract

- Produce or update a `plan.md` document.
- Do not perform implementation or operational execution unless the user separately asks after reviewing the document.
- Planning files may be created or updated as part of the workflow; implementation files must not be changed.
- Prefer subagents for planning, critique, and synthesis.
- Keep the main agent's context clean: the main agent should only inspect task framing, final `plan.md`, concise subagent summaries, and diffs.
- If an existing `plan.md` is provided, treat it as an input draft and produce a stronger revision.
- If overwriting an existing `plan.md` is risky or not explicitly requested, write `plan.updated.md` and explain how it differs.

## When To Use

Use for:

- User asks for `$plan-grill`.
- User asks for a `plan.md`.
- User provides an initial `plan.md` and wants it improved, reviewed, hardened, or made production-ready.
- Production deployments or release plans.
- Database/schema/data migrations.
- Auth, permissions, secrets, payment, billing, or security changes.
- CI/CD, infra, config, container, networking, observability, or rollback changes.
- Dependency upgrades with runtime risk.
- Refactors with unclear blast radius.
- Work touching user data, destructive writes, or unknown blast radius.
- User asks for "safe plan", "production plan", "migration", "rollout", "architecture", "review my approach", "stress-test this", or "think first" in a context with meaningful risk.

Do not use automatically for:

- Typos.
- Tiny local style edits.
- Single-file obvious fixes.
- Pure explanation questions.
- User explicitly asks to execute a low-risk change directly.

## Main-Agent Role

The main agent is the auditor and coordinator, not the primary planner.

Main agent responsibilities:

- Create a compact task packet for subagents.
- Launch subagents when available.
- Avoid reading large unrelated context directly.
- Review the final `plan.md` against the acceptance checklist.
- Report whether the plan is acceptable, incomplete, or unsafe.
- Ask the user before overwriting an existing plan when intent is unclear.

The main agent should not:

- Execute the final plan by default.
- Dump all subagent reasoning into the conversation.
- Let one subagent both create and approve its own plan.
- Treat a plan as accepted without validation, rollback, and open-question sections.

## Subagent-First Workflow

Use subagents when the environment supports them.

## Subagent Isolation Rules

- Prefer read-only subagent modes when available.
- Do not grant subagents permission to modify implementation files.
- If a subagent tool supports isolated worktrees, use one only for investigation, not implementation.
- Planner and Grill subagents should return text artifacts, not write files.
- Synthesizer should return final `plan.md` content and a short changelog.
- The main agent performs the final file write after acceptance.
- No agent should commit changes unless the user explicitly asks.

## Planning Artifact Contract

Use `.plan-grill/<task-slug>/` only when intermediate artifacts help reviewability or context hygiene.

Rules:

- The main agent owns artifact file writes; subagents return text.
- Artifacts are optional scratch files, safe to delete, and should not be committed.
- Artifacts must contain summaries and source references, not raw secret values, env dumps, full logs, or large excerpts.
- Redact tokens, credentials, private keys, cookies, and personal data.
- Keep final user-facing output as `plan.md` unless overwrite rules require another path.

Suggested artifact files:

```text
.plan-grill/<task-slug>/task-packet.md
.plan-grill/<task-slug>/planner-summary.md
.plan-grill/<task-slug>/review-findings.md
.plan-grill/<task-slug>/synthesizer-changelog.md
.plan-grill/<task-slug>/diff-summary.md
```

Do not create artifacts for trivial plans.

### 1. Task Packet

Prepare a compact packet:

```text
Objective:
Relevant user request:
Existing plan path, if any:
Repository root:
Current git status summary:
Known constraints:
Likely relevant files/directories:
Output path:
Artifact path, if used:
Redaction constraints:
Do not execute implementation changes.
```

Include only necessary context. Do not pass unrelated conversation history.

### 2. Planner Subagent

Goal: create a first-draft `plan.md` from evidence.

Prompt shape:

```text
You are the planner. Inspect the repo as needed and produce a production-grade plan.md draft.
Do not implement code changes.
Include goal, non-goals, evidence inspected, context, assumptions, approach, steps, affected files, owners, validation, rollout, monitoring, rollback, abort criteria, risks, risk level, confidence, open questions, and execution decision.
Return the plan document and a concise evidence summary.
```

### 3. Grill Subagent

Goal: stress-test the draft.

Prompt shape:

```text
You are the reviewer. Review only the draft plan and necessary evidence.
Do not rewrite the whole plan.
Find missing assumptions, weak validation, rollback gaps, blast-radius issues, data/security risks, operational gaps, and unclear ownership.
Check that risk level and confidence follow the rubric.
Flag any unsupported facts, fake owners, fake precision, missing evidence, unredacted sensitive data, or unsafe overwrite behavior.
Return prioritized findings with severity and concrete fixes.
```

### 4. Synthesizer Subagent

Goal: produce the final `plan.md`.

Prompt shape:

```text
You are the synthesizer. Merge the planner draft and reviewer findings into a final plan.md.
Do not implement code changes.
Preserve useful detail, remove speculation, mark unresolved questions explicitly, and include changes from previous draft if applicable.
Use Unknown or TBD rather than inventing evidence, owners, dates, metrics, or guarantees.
Return only the final plan document plus a short changelog.
```

### 5. Main-Agent Acceptance

The main agent reads:

- Final `plan.md`.
- Concise planner evidence summary.
- Prioritized grill findings.
- Synthesizer changelog.
- Diff against previous `plan.md`, if any.

Then decide:

- Acceptable: plan is ready for user review.
- Needs revision: send a targeted follow-up to a subagent.
- Unsafe: stop and explain missing decisions or evidence.

## Fallback Without Subagents

If subagents are unavailable:

1. State that subagents are unavailable.
2. Use the same roles sequentially in the main agent.
3. Keep intermediate notes short.
4. Still write or update `plan.md`.
5. Clearly label the result as "single-agent fallback".

Do not skip the grill pass just because subagents are unavailable.

## Output Path Rules

Default output path:

```text
plan.md
```

If the user provides a path, use that path.

If `plan.md` already exists:

- If the user asked to "iterate", "update", "improve", or "rewrite" it, update that file.
- If overwrite intent is unclear, write `plan.updated.md`.
- If the existing plan contains important history, preserve it in `Changes From Previous Plan` instead of deleting it.
- Require a `Previous Plan Diff Summary` for every existing-plan revision.
- Do not delete prior risks, assumptions, or open questions unless the new plan explains why they are resolved or obsolete.

## Required plan.md Structure

Use this structure unless the user requests another format:

```markdown
# Plan

## Goal

## Non-Goals

## Evidence Inspected

## Current Context

## Assumptions

## Proposed Approach

## Step-by-Step Plan

## Files / Components Likely Affected

## Owners / Responsibilities

## Validation Plan

## Rollout Plan

## Monitoring / Observability

## Rollback / Recovery Plan

## Abort Criteria

## Risks

## Open Questions

## Execution Decision

- Recommendation: Ready for user-approved execution / Wait / Needs answers
- Risk Level: Low / Medium / High / Critical
- Confidence: Low / Medium / High
- Reason:
```

When iterating an existing plan, also include:

```markdown
## Issues Found In Previous Plan

## Previous Plan Diff Summary

- Kept:
- Changed:
- Removed:
- Unresolved:

## Changes From Previous Plan
```

If a section is not applicable, write `Not applicable` with a one-line reason. For production, deploy, data, auth, billing, or security plans, `Not applicable` in validation, rollback, monitoring, rollout, or abort criteria requires reviewer scrutiny.

Owner fields must use one of:

- `Known`: cite evidence.
- `Inferred`: cite evidence and mark as inference.
- `TBD`: add an open question.

Do not invent owners.

## Acceptance Checklist

A final plan is acceptable only if it answers:

- What is the goal and non-goal?
- What evidence was inspected?
- What assumptions could invalidate the plan?
- What is the smallest safe implementation path?
- What files/components are likely affected?
- Who owns execution, review, validation, and rollback?
- How will success be validated?
- How will rollout be staged or limited?
- What monitoring or observability proves runtime behavior?
- What can fail silently?
- What abort criteria stop execution?
- What is the rollback or recovery path?
- What user data, secrets, auth, billing, or security risk exists?
- What open questions block execution?
- Is the execution recommendation explicit?
- Are risk level and confidence justified by evidence?

If any item is missing, revise or mark it as an explicit open question.

## Risk And Confidence Rubric

Risk Level:

- `Low`: local or easily reversible change; no user data, auth, billing, deploy, or broad runtime impact.
- `Medium`: moderate blast radius, limited runtime impact, or partial rollback uncertainty.
- `High`: production, user data, auth, billing, migrations, security, destructive writes, or weak rollback.
- `Critical`: irreversible data/security impact, broad outage risk, compliance risk, or no credible recovery path.

Confidence:

- `High`: evidence inspected, low unresolved ambiguity, clear validation, clear rollback.
- `Medium`: some assumptions remain but validation and recovery are plausible.
- `Low`: key evidence missing, unknown owners, weak validation, weak rollback, or unresolved blockers.

## Production Defaults

- Prefer boring, observable, reversible plans.
- Prefer staged rollout, backups, feature flags, and small blast radius.
- Do not let "tests pass" replace runtime validation for deploy-impacting changes.
- Require smoke checks for deploy/runtime behavior.
- Require regression tests for bug fixes when practical.
- Require data backup or reversible migration for schema/data changes.
- Require secret/config review when env vars or credentials are touched.
- Mark irreversible work clearly.

## Final Response To User

Keep the final response short:

```text
Generated/updated: <path>
Planning artifacts: <path or none>
Status: Acceptable / Needs revision / Unsafe
Key risks:
- ...
Open questions:
- ...

I did not execute implementation or operational steps.
```

Do not paste the entire `plan.md` unless the user asks.

## Limits

This skill cannot globally replace Codex's built-in Plan mode. It works when invoked as `$plan-grill` or when the skill selector loads it from task context.
