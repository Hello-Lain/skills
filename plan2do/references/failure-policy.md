# Plan2Do Failure Policy

Use this when verification, review, scope, tooling, or context checks fail.

## Classes

- `PLAN_INVALID`: the plan lacks executable fields, conflicts with the latest user instruction, or fails upstream validation.
- `VERIFY_FAILED`: a command, smoke check, fixture, or manual verification did not pass.
- `REVIEW_FAILED`: review found incomplete behavior, regression risk, poor architecture, or over-engineering.
- `SCOPE_VIOLATION`: edits touched files outside writable scope without a justified execution note.
- `CONTEXT_CONFLICT`: current source files, plan, artifacts, or user constraints disagree.
- `APPROVAL_REQUIRED`: destructive, production, security, public API, schema/data, dependency, or hard-to-rollback work needs user confirmation.
- `BLOCKED_REWORK_LIMIT`: the same failure remains after the allowed rework cycles.
- `TOOLING_BLOCKED`: a required local tool is unavailable and no safe fallback exists.

## Response

1. Stop success reporting.
2. Write `artifacts/rework-guidance[-N].md` before fixes unless the class is `APPROVAL_REQUIRED`.
3. Name evidence, defect, impact, required change, writable scope, verification, and cycle number.
4. Apply the smallest safe fix inside scope.
5. Rerun the failing check plus any cheap regression checks.
6. If the same failure persists after two cycles, report `INCOMPLETE` with the failure class and next action.

Never mark `Status: COMPLETE` while any failure class is unresolved.
