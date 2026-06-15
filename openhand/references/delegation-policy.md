# Delegation Policy

OpenHand delegation is opt-in and approval-gated.

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

## Approval Gate

Before backend use, report:

- Why delegation is recommended.
- Repository/worktree path.
- OpenHandsMCP commit/version.
- Expected tools to call.
- Whether secrets are needed.
- Cleanup plan.

If any answer is unknown, stop and ask.
