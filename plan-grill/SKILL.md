---
name: plan-grill
description: "Use when the user wants a production-grade plan.md, wants to upgrade an initial plan.md, or asks for a safer replacement for ordinary planning. Produces or iterates a plan document under .plan-grill task-specific directories by default through subagent-first planning, stress review, synthesis, and main-agent acceptance. Does not execute by default; the user decides whether and how to execute the final plan."
metadata:
  short-description: "Generate and harden isolated production plans"
---

# Plan Grill

Plan Grill is a production-grade `.plan-grill/<task-slug>/plan.md` generator and plan hardening workflow.

Default outcome:

```text
final .plan-grill/<task-slug>/plan.md, not execution
```

Use this skill to create a new plan document or improve an existing one. The user decides whether and how to execute the final plan.

## Core Contract

- Produce or update a `plan.md` document under `.plan-grill/<task-slug>/` by default.
- Do not perform implementation or operational execution unless the user separately asks after reviewing the document.
- Planning files may be created or updated as part of the workflow; implementation files must not be changed.
- Prefer subagents for planning, critique, and synthesis.
- Keep the main agent's context clean: the main agent should only inspect task framing, final `.plan-grill/<task-slug>/plan.md`, concise subagent summaries, and diffs.
- If an existing `plan.md` is provided, treat it as an input draft and produce a stronger revision.
- If overwriting an existing plan is risky or not explicitly requested, write a new `.plan-grill/<task-slug>/plan.md` and explain how it differs.

## Language And User-Input Policy

- Write the final plan, decision prompts, open questions, and final user response in the user's language.
- If the user writes Chinese, use Simplified Chinese for the plan and user-facing artifacts. Keep commands, paths, env vars, code identifiers, package names, API names, and error strings exact.
- If source evidence is in another language, summarize it in the user's language rather than translating literal code or filenames.
- Include `Output language:` in every task packet.
- Pass the required output language to Planner, Grill, and Synthesizer subagents.
- If the plan needs user decisions before execution, include a user-facing `用户需提供的信息` / `User Inputs Needed` section.
- Decision tables must include: ID, needed information, recommended default, options, why it matters, and what happens if unanswered.
- Open questions must reference decision IDs from the user-input table. Do not leave abstract questions that users cannot answer.
- Include a short "minimum answers needed to proceed" line when the execution decision is `Needs answers`.

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
- Audit subagent status and recent activity before deciding to wait, steer, cancel, or fallback.
- Avoid reading large unrelated context directly.
- Review the final `.plan-grill/<task-slug>/plan.md` against the acceptance checklist.
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
- Synthesizer should return final plan content and a short changelog.
- The main agent performs the final file write after acceptance.
- No agent should commit changes unless the user explicitly asks.

## Subagent Lifecycle

Subagents are disposable for each `plan-grill` run.

Rules:

- Launch only the minimum subagents needed, normally Planner, Grill, and Synthesizer.
- Do not leave completed subagents alive after their outputs are collected.
- After collecting a subagent's final result, archive or kill it when the environment provides such a control.
- Treat `wait` timeout as a checkpoint, not a stall. Inspect status and recent activity before deciding.
- Cancel only after the Subagent Progress Audit below shows no useful progress, unrelated permission blocking, unsafe behavior, or repeated inability to proceed.
- Do not reuse stale subagents across separate `plan-grill` runs; create fresh ones with a fresh task packet.
- Keep a short local summary of each subagent result before releasing it.
- If the environment has a subagent limit or visible live-agent list, check it before launching more agents.

If agents cannot be released explicitly, note the limitation in the final response and avoid spawning optional review agents.

## Subagent Progress Audit

Before canceling or falling back from any running subagent:

1. Inspect lifecycle state with the available agent status tool.
2. Inspect recent activity, terminal output, or progress artifacts with the available activity tool.
3. Decide whether the agent is active, idle, blocked, unsafe, or complete.
4. Record the decision in `.plan-grill/<task-slug>/subagent-status.md` when the run is non-trivial.

Use the best status source available:

- Paseo-style agents: use `get_agent_status`, then `get_agent_activity`; use `list_agents` when unsure which agents are alive.
- `codex2codex-meight`: use `meight status <name>`, `meight result <name>`, and recent `events.log`; a `wait --timeout` exit is only a checkpoint.
- Terminal-backed agents: capture recent terminal output before deciding.
- Unknown backend: poll the backend's status API or keep waiting with a clear checkpoint note.

Do not cancel solely because:

- The agent exceeded an arbitrary wall-clock threshold.
- The last wait call timed out but recent activity shows file reads, reasoning, commands, or draft generation.
- The task is complex and the agent is still inspecting relevant evidence.

Cancel or fallback when one or more is true:

- Two consecutive progress audits show no new activity and no useful partial output.
- The agent requests unrelated permissions or tries to modify implementation files during planning.
- The agent loops on irrelevant evidence despite one targeted steering message.
- The agent is unsafe, destructive, or ignores the task packet.
- The user asks to stop.

If the agent is active but slow, keep it running and provide a short user update. If its work is useful but incomplete, ask for a concise checkpoint summary instead of killing it.

## Planning Artifact Contract

Use `.plan-grill/<task-slug>/` for the final plan and any intermediate artifacts.

Rules:

- The main agent owns artifact file writes; subagents return text.
- Intermediate artifacts are optional scratch files, safe to delete, and should not be committed.
- Artifacts must contain summaries and source references, not raw secret values, env dumps, full logs, or large excerpts.
- Redact tokens, credentials, private keys, cookies, and personal data.
- Keep the final user-facing plan at `.plan-grill/<task-slug>/plan.md` unless the user explicitly provides another path.

Suggested artifact files:

```text
.plan-grill/<task-slug>/task-packet.md
.plan-grill/<task-slug>/plan.md
.plan-grill/<task-slug>/planner-summary.md
.plan-grill/<task-slug>/review-findings.md
.plan-grill/<task-slug>/synthesizer-changelog.md
.plan-grill/<task-slug>/diff-summary.md
.plan-grill/<task-slug>/subagent-status.md
```

For trivial plans, still use `.plan-grill/<task-slug>/plan.md` but skip optional intermediate artifacts.

## Scratch And Plan Lifecycle

`.plan-grill/` stores isolated planning runs. Each run must use its own `.plan-grill/<task-slug>/` directory so multiple Codex conversations can plan different tasks without conflicting.

Start-of-run rules:

- Create a task slug from the objective, e.g. lower-case words, digits, and hyphens only.
- Use `.plan-grill/<task-slug>/`; if it already exists for a different active task, append a short timestamp or counter.
- Reset only the current `.plan-grill/<task-slug>/` directory at the start of a fresh run. Never delete or reset the whole `.plan-grill/` directory by default.
- Never use stale `.plan-grill/<other-task-slug>/` artifacts as evidence for a new plan unless the user points to them.
- If the user wants to continue a previous plan, use that run's `.plan-grill/<task-slug>/plan.md` or user-provided plan path as the input, not unrelated scratch files.

Final-plan persistence:

- The refined `.plan-grill/<task-slug>/plan.md` is not scratch.
- Keep the final plan until the user executes it, clears it, asks to replace it, or starts a new `plan-grill` run that intentionally creates a fresh plan.
- On a new run, create or reset only the selected task directory, then apply the output path rules for the final plan.
- If replacing an existing final plan, preserve the previous plan's important risks, assumptions, and open questions in the new plan's diff sections.

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
Output language:
Artifact path, if used:
Redaction constraints:
Do not execute implementation changes.
```

Include only necessary context. Do not pass unrelated conversation history.

### 2. Planner Subagent

Goal: create a first-draft `plan.md` from evidence for the selected output path.

Prompt shape:

```text
You are the planner. Inspect the repo as needed and produce a production-grade plan.md draft for the requested output path.
Write the plan in <output language>. Keep commands, file paths, env vars, identifiers, and errors exact.
Do not implement code changes.
Include goal, non-goals, evidence inspected, context, assumptions, approach, steps, affected files, owners, validation, rollout, monitoring, rollback, abort criteria, risks, risk level, confidence, open questions, and execution decision.
If user decisions are needed, include a user-facing decision table with IDs, recommended defaults, options, impact, and default handling.
If the task is large, send or leave a concise progress checkpoint before continuing deep inspection when the agent backend supports it.
Return the plan document and a concise evidence summary.
```

### 3. Grill Subagent

Goal: stress-test the draft.

Prompt shape:

```text
You are the reviewer. Review only the draft plan and necessary evidence.
Check that the draft is written in <output language> for user-facing content.
Do not rewrite the whole plan.
Find missing assumptions, weak validation, rollback gaps, blast-radius issues, data/security risks, operational gaps, and unclear ownership.
Check that risk level and confidence follow the rubric.
Flag any unsupported facts, fake owners, fake precision, missing evidence, unredacted sensitive data, unsafe overwrite behavior, or user-facing questions that are too abstract to answer.
If the review is taking longer than expected, report which section is being checked and whether useful progress is being made.
Return prioritized findings with severity and concrete fixes.
```

### 4. Synthesizer Subagent

Goal: produce the final plan for `.plan-grill/<task-slug>/plan.md` or the user-provided output path.

Prompt shape:

```text
You are the synthesizer. Merge the planner draft and reviewer findings into a final plan.md for the requested output path.
Write the final plan in <output language>. Keep commands, file paths, env vars, identifiers, and errors exact.
Do not implement code changes.
Preserve useful detail, remove speculation, mark unresolved questions explicitly, and include changes from previous draft if applicable.
Use Unknown or TBD rather than inventing evidence, owners, dates, metrics, or guarantees.
If user input is needed, make it directly answerable with recommended defaults and options.
If synthesis is delayed, report the current merge stage and unresolved blocker before continuing.
Return only the final plan document plus a short changelog.
```

### 5. Main-Agent Acceptance

The main agent reads:

- Final `.plan-grill/<task-slug>/plan.md` or user-provided output path.
- Concise planner evidence summary.
- Prioritized grill findings.
- Synthesizer changelog.
- Diff against previous plan, if any.

Then decide:

- Acceptable: plan is ready for user review.
- Needs revision: send a targeted follow-up to a subagent.
- Unsafe: stop and explain missing decisions or evidence.

## Fallback Without Subagents

If subagents are unavailable:

1. State that subagents are unavailable.
2. Use the same roles sequentially in the main agent.
3. Keep intermediate notes short.
4. Still write or update `.plan-grill/<task-slug>/plan.md` unless the user provided another path.
5. Clearly label the result as "single-agent fallback".

Do not skip the grill pass just because subagents are unavailable.

## Output Path Rules

Default output path:

```text
.plan-grill/<task-slug>/plan.md
```

If the user provides a path, use that path. If the user specifically asks for root `plan.md`, honor it.

If an existing plan is provided or the selected output path already exists:

- If the user asked to "iterate", "update", "improve", or "rewrite" that explicit file, update that file.
- If overwrite intent is unclear, write a new `.plan-grill/<new-task-slug>/plan.md` instead of `plan.updated.md`.
- If the existing plan contains important history, preserve it in `Changes From Previous Plan` instead of deleting it.
- Require a `Previous Plan Diff Summary` for every existing-plan revision.
- Do not delete prior risks, assumptions, or open questions unless the new plan explains why they are resolved or obsolete.

## Required plan.md Structure

Use this semantic structure unless the user requests another format. Translate headings into the user's language when appropriate.

```markdown
# Plan

## Goal

## Non-Goals

## Evidence Inspected

## Current Context

## Assumptions

## User Inputs Needed

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

For Chinese output, use clear Chinese headings such as:

```markdown
# 计划

## 目标
## 非目标
## 已检查证据
## 当前上下文
## 假设
## 用户需提供的信息
## 建议方案
## 分步计划
## 可能影响的文件 / 组件
## 负责人 / 职责
## 验证计划
## 发布 / 推进计划
## 监控 / 可观测性
## 回滚 / 恢复计划
## 中止条件
## 风险
## 待确认问题
## 执行决策
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

For `Needs answers`, `用户需提供的信息` / `User Inputs Needed` is required and must be concrete enough that a non-technical user can answer by choosing defaults or options.

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
Generated/updated: .plan-grill/<task-slug>/plan.md
Planning artifacts: .plan-grill/<task-slug>/ or none
Status: Acceptable / Needs revision / Unsafe
Key risks:
- ...
Open questions:
- ...

I did not execute implementation or operational steps.
```

Do not paste the entire plan unless the user asks.

## Limits

This skill cannot globally replace Codex's built-in Plan mode. It works when invoked as `$plan-grill` or when the skill selector loads it from task context.
