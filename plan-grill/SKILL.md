---
name: plan-grill
description: "Use when the user wants a production-grade plan.md, safer planning, improved existing plans, risky refactors, migrations, auth/billing/security, CI/CD/infra/rollback planning, or approach stress review. Generate or harden `.plan-grill/task-slug/plan.md`, validate required sections, and include an Execution Handoff. Do not execute the plan by default."
---

# Plan Grill

Generate or harden `.plan-grill/<task-slug>/plan.md`. Do not change implementation files or execute operational steps unless the user later asks after reviewing the plan.

## Defaults

- Write final plans, questions, and final response in the user's language.
- Keep commands, paths, env vars, identifiers, package names, API names, and error strings exact.
- Prefer subagents; main agent keeps only task framing, final plan, concise summaries, and diffs.
- If overwrite intent is unclear, create a new task slug instead of replacing an existing plan.
- If iterating a plan, preserve important prior risks, assumptions, and open questions unless the new plan resolves them.

## Workflow

1. Read `references/plan-contract.md`.
2. Build a compact task packet: objective, request, repo, git status, constraints, likely files, output path, `Output language:`, redaction, no implementation.
3. Planner: inspect evidence and return draft plan text only.
4. Grill: find missing assumptions, weak validation, rollback gaps, blast radius, data/security risks, and unclear ownership.
5. Synthesizer: merge draft + findings into final plan text only.
6. Main agent writes the plan after acceptance, validates it, then reports status.

## Subagents

- Use read-only modes when possible.
- Planner/Grill/Synthesizer return text only; they must not write files.
- Inspect returned artifacts, not only terminal/status output.
- Reject progress-only outputs.
- If output is invalid, send one targeted follow-up; if still invalid, stop with `Needs revision` or `Unsafe`.
- Release completed subagents before the next phase. If unavailable, run the same roles sequentially and label `single-agent fallback`.

## Output

- Default path: `.plan-grill/<task-slug>/plan.md`; use a user-provided path if specified.
- Required contract: `references/plan-contract.md`.
- Required handoff: `## Execution Handoff` with goal, current state, authoritative artifacts, decisions, verification, remaining risks, next action, suggested skills, and redactions / omitted raw data.
- Validate new plans with `scripts/validate_plan_contract.py <plan.md>`. Use `--allow-missing-handoff` only for old plans.

## Final Response

Keep it short: generated/updated path, artifact directory, validation status, subagents released, key risks, open questions, and a note that implementation/ops were not executed.
