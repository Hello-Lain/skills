---
name: plan-grill
description: "Use when the user wants a production-grade plan.md, safer planning, or an improved existing plan. Generate or harden `.plan-grill/task-slug/plan.md` through planning, stress review, synthesis, and main-agent acceptance. Do not execute the plan by default."
---

# Plan Grill

Generate or harden `.plan-grill/<task-slug>/plan.md`. Do not change implementation files or execute operational steps unless the user later asks after reviewing the plan.

## Use
- Use for `plan.md`, production plans, safer plans, risky refactors, migrations, auth/billing/security, CI/CD/infra/rollback, or approach review/stress-test.
- Do not use for typos, tiny style fixes, obvious single-file edits, pure explanations, or explicit low-risk execution requests.

## Defaults
- Write final plans, questions, and final response in the user's language.
- Keep commands, paths, env vars, identifiers, package names, API names, and error strings exact.
- Prefer subagents; main agent keeps only task framing, final plan, concise summaries, and diffs.
- If overwrite intent is unclear, create a new task slug instead of replacing an existing plan.
- If iterating a plan, preserve important prior risks, assumptions, and open questions unless the new plan resolves them.

## Workflow
1. Build a compact task packet: objective, request, repo, git status, constraints, likely files, output path, `Output language:`, redaction, no implementation. Pass the language to all subagents.
2. Planner: inspect evidence and return draft plan text only.
3. Grill: find missing assumptions, weak validation, rollback gaps, blast radius, data/security risks, and unclear ownership.
4. Synthesizer: merge draft + findings into final plan text only.
5. Main agent writes the plan after acceptance and reports status.

## Subagents
- Use read-only modes when possible.
- Planner/Grill/Synthesizer return text only; they must not write files.
- Inspect returned artifacts, not only terminal/status output.
- Reject progress-only outputs.
- If output is invalid, send one targeted follow-up; if still invalid, stop with `Needs revision` or `Unsafe`.
- Release completed subagents before the next phase. If unavailable, run the same roles sequentially and label `single-agent fallback`.

## Output
- Default path: `.plan-grill/<task-slug>/plan.md`; use a user-provided path if specified.
- Required sections: Goal, Non-Goals, Evidence Inspected, Current Context, Assumptions, User Inputs Needed, Proposed Approach, Step-by-Step Plan, Files / Components Likely Affected, Owners / Responsibilities, Validation Plan, Rollout Plan, Monitoring / Observability, Rollback / Recovery Plan, Abort Criteria, Risks, Open Questions, Execution Decision.
- If iterating an existing plan, also include issues found, previous-plan diff, and changes from previous plan.

## Quality Gates
- User-input questions must be concrete, answerable, and include recommended defaults when possible.
- Risk level: Low / Medium / High / Critical. Confidence: Low / Medium / High.
- Prefer boring, observable, reversible plans.
- Require smoke checks for deploy/runtime work and regression tests when practical.
- Require backups or reversible migrations for schema/data changes.
- Mark irreversible work clearly.
- Do not leave required sections blank; use `Not applicable` with a one-line reason.

## Final Response
Keep it short: generated/updated path, artifact directory, status, subagents released, key risks, open questions, and a note that implementation/ops were not executed.
