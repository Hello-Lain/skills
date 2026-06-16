# Delegation Policy

OpenHand delegation is recommendation-capable and execution approval-gated.

Codex may proactively recommend this workflow when task scale, ambiguity, or
runtime cost is high. Backend use remains opt-in: do not start OpenHandsMCP,
Docker, Podman, or live MCP tasks until the user approves that step.

## Positive Triggers

- Broad implementation spanning multiple files or modules.
- Complex refactors where an isolated workspace helps exploration.
- Long-running test or validation loops.
- Plan execution where a backend can produce a proposal diff for review.

## Negative Triggers

- Small local edits.
- Work involving production, billing, auth, destructive migrations, or irreversible data changes unless the user explicitly asks for a safe plan only.
- Tasks needing secrets before the secret policy is accepted.
- Tasks where Docker/Podman socket exposure is unacceptable.
- Tasks that cannot be reviewed as a diff before application.

## Recommendation Gate

Before asking to use the backend, report:

- Why the task looks large or context-heavy.
- Why local Codex-only execution may be inefficient or risky.
- What OpenHandsMCP would do in proposal-only mode.
- What stays under lead Codex control.

If the user declines, continue locally.

## Approval Gate

Before backend use, report:

- Why delegation is recommended.
- Repository/worktree path.
- OpenHandsMCP commit/version.
- Expected tools to call.
- Whether secrets are needed.
- Cleanup plan.

If any answer is unknown, stop and ask.
