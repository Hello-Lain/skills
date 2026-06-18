# Plan Contract

Use this for every new or hardened `.plan-grill/<task-slug>/plan.md`.

## Required Sections

- `# <title>`
- `## Goal`
- `## Non-Goals`
- `## Evidence Inspected`
- `## Domain Language Check`
- `## Current Context`
- `## Assumptions`
- `## User Inputs Needed`
- `## Proposed Approach`
- `## Scenario Probes`
- `## Step-by-Step Plan`
- `## Files / Components Likely Affected`
- `## Owners / Responsibilities`
- `## Validation Plan`
- `## Rollout Plan`
- `## Monitoring / Observability`
- `## Documentation / ADR Updates`
- `## Rollback / Recovery Plan`
- `## Abort Criteria`
- `## Risks`
- `## Open Questions`
- `## Execution Decision`
- `## Execution Handoff`

If iterating an existing plan, also include issues found, previous-plan diff, and changes from previous plan.

## Quality Gates

- User-input questions must be concrete, answerable, and include recommended defaults when possible.
- Ask user only for questions that cannot be answered from repo code/docs; cite what was inspected.
- Use canonical terms from `CONTEXT.md`, `CONTEXT-MAP.md`, ADRs, and code; flag conflicts or fuzzy terms.
- Include scenario probes for edge cases, counterexamples, blast radius, ownership, validation, and rollback.
- Put doc/ADR changes in `Documentation / ADR Updates`; do not write docs unless explicitly requested.
- Include `ADR: Needed|Not needed|Existing`; recommend a new ADR only when the decision is hard to reverse, future readers would be surprised, and there is a real trade-off.
- Generated plans must have validated sibling artifacts at `.plan-grill/<task-slug>/subagents/planner.md`, `grill.md`, and `synthesizer.md`; `plan.md` must match the synthesizer artifact body exactly.
- Include `Risk level: Low|Medium|High|Critical`.
- Include `Confidence: Low|Medium|High`.
- Prefer boring, observable, reversible plans.
- Require smoke checks for deploy/runtime work and regression tests when practical.
- Require backups or reversible migrations for schema/data changes.
- Mark irreversible work clearly.
- Do not leave required sections blank; use `Not applicable` with a one-line reason.

## Execution Handoff

Use this exact section shape:

```md
## Execution Handoff

- Goal:
- Current state:
- Authoritative artifacts:
- Decisions:
- Verification:
- Remaining risks:
- Next action:
- Suggested skills:
- Redactions / omitted raw data:
```

Do not duplicate existing artifacts. Reference PRDs, ADRs, issues, commits, diffs, logs, or prior plans by path/URL. Redact secrets, credentials, tokens, private personal data, and raw logs unless they are explicitly needed and safe.
