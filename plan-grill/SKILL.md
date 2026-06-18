---
name: plan-grill
description: "Use when the user wants a production-grade plan.md, safer planning, improved existing plans, risky refactors, migrations, auth/billing/security, CI/CD/infra/rollback planning, or approach stress review. Generate or harden `.plan-grill/task-slug/plan.md`, validate required sections, and include an Execution Handoff. Do not execute the plan by default."
---

# Plan Grill

Generate or harden `.plan-grill/<task-slug>/plan.md`. Do not change implementation files or execute operational steps unless the user later asks after reviewing the plan.

## Defaults

- Write final plans, questions, and final response in the user's language.
- Keep commands, paths, env vars, identifiers, package names, API names, and error strings exact.
- Planner/Grill/Synthesizer subagents are mandatory; main agent keeps only task framing, artifact validation, mechanical plan writing, concise summaries, and diffs.
- If overwrite intent is unclear, create a new task slug instead of replacing an existing plan.
- If iterating a plan, preserve important prior risks, assumptions, and open questions unless the new plan resolves them.
- Do not write `CONTEXT.md`, ADRs, or docs by default; propose doc updates in the plan unless the user explicitly asks to write them.

## Workflow

1. Read `references/plan-contract.md`.
2. Inspect domain context if present: `CONTEXT-MAP.md`, `CONTEXT.md`, `docs/adr/`, nearby docs, and likely code. Prefer code/docs evidence over asking the user.
3. Build a compact task packet: objective, request, repo, git status, constraints, likely files, domain terms, doc/code conflicts, output path, `Output language:`, redaction, no implementation.
4. Planner subagent: inspect evidence and return a validated draft plan artifact.
5. Grill subagent: find missing assumptions, weak validation, rollback gaps, blast radius, data/security risks, unclear ownership, scenario gaps, doc/code contradictions, and repo-unanswerable user questions; return a validated findings artifact.
6. Synthesizer subagent: merge draft + findings into a validated final plan artifact.
7. Main agent writes the synthesizer artifact to the plan path without replacing it with main-agent synthesis, validates it, then reports status.

## Subagents

- Use read-only modes when possible.
- Planner/Grill/Synthesizer return text only; they must not write files.
- Call a real subagent for each phase. The main agent must not impersonate, inline, or sequentially self-run planner/grill/synthesizer roles.
- If subagent creation/call fails before an artifact is returned, retry that phase once with the same task packet. If retry fails, stop before writing/updating the plan and report `Subagent unavailable`.
- Require the artifact envelope below for every subagent response; missing/partial envelopes mean the phase did not complete.
- Save each returned artifact immediately under `.plan-grill/<task-slug>/subagents/<phase>.md`.
- Validate each artifact with `scripts/validate_subagent_artifact.py <phase> <artifact.md>` before using it.
- Inspect returned artifacts, not only terminal/status output.
- Reject progress-only outputs, missing final sentinels, mismatched phase names, non-`complete` statuses, and empty artifacts.
- If output is invalid or appears interrupted, send one targeted follow-up with the validator error and ask for a full replacement artifact. If still invalid, stop with `Needs revision` or `Unsafe`.
- Do not degrade to main-agent synthesis after a partial or interrupted subagent result. Fail closed instead.
- No single-agent fallback. Subagent unavailability is a blocking failure, not permission for main-agent generation.
- Release completed subagents after artifact validation and before the next phase.

### Subagent Artifact Envelope

Every subagent must return exactly this outer shape, with the end marker as the final non-whitespace line:

```text
PLAN_GRILL_ARTIFACT_V1
phase: planner|grill|synthesizer
status: complete|needs_revision|unsafe
artifact:
<role-specific text only>
PLAN_GRILL_ARTIFACT_END
```

Continue only when `phase` matches the requested phase, `status: complete`, `artifact:` is substantive, and the validator passes. Treat `needs_revision`, `unsafe`, missing markers, trailing text after the end marker, or network/session interruption as blocking phase failures.

Grill artifacts must include `Scenario Probes`, `Code/doc contradictions`, and `Repo-unanswerable user questions`; use `None found` only after inspecting code/docs.

## Output

- Default path: `.plan-grill/<task-slug>/plan.md`; use a user-provided path if specified.
- Required contract: `references/plan-contract.md`.
- Required handoff: `## Execution Handoff` with goal, current state, authoritative artifacts, decisions, verification, remaining risks, next action, suggested skills, and redactions / omitted raw data.
- Required domain gates: `## Domain Language Check`, `## Scenario Probes`, and `## Documentation / ADR Updates`.
- Required provenance: validated `subagents/planner.md`, `subagents/grill.md`, and `subagents/synthesizer.md` must exist; `plan.md` must match the synthesizer artifact body exactly.
- Validate new plans with `scripts/validate_plan_contract.py <plan.md>`. Use `--allow-missing-handoff` only for old plans.
- Validate subagent returns with `scripts/validate_subagent_artifact.py <phase> <artifact.md>` before trusting them.

## Final Response

Keep it short: generated/updated path, artifact directory, validation status, subagents released, key risks, open questions, and a note that implementation/ops were not executed.
