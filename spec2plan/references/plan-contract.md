# Spec2Plan Contract

Use this for every generated or hardened `plan.md`.

## Required Sections

- `# <title>`
- `## Goal`
- `## Non-Goals`
- `## Evidence Inspected`
- `## Spec Summary`
- `## Domain Language Check`
- `## Current Context`
- `## Assumptions`
- `## User Inputs Needed`
- `## Proposed Approach`
- `## Scenario Probes`
- `## Dependency Graph`
- `## Task Breakdown`
- `## Step-by-Step Plan`
- `## Parallelization`
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

If a section does not apply, write `Not applicable` with a one-line reason. Do not leave required sections blank.

## Plan Quality Gates

- Include `Mode: light|heavy`, `Risk level: Low|Medium|High|Critical`, and `Confidence: Low|Medium|High`.
- Include `ADR: Needed|Not needed|Existing` under `Documentation / ADR Updates`.
- Cite inspected specs, docs, code, diffs, logs, or prior plans by path/URL.
- Ask the user only for repo-unanswerable questions; cite what was inspected.
- Use canonical domain terms from specs, docs, ADRs, and code; flag term conflicts.
- Prefer boring, observable, reversible plans.
- Mark irreversible work clearly.
- Require regression tests when practical.
- Require smoke checks for deploy/runtime work.
- Require backups or reversible migrations for schema/data changes.

## Task Breakdown Rules

Prefer vertical slices that deliver a working path over horizontal layers.

Each task must include:

```md
### Task N: Short title

- Description:
- Acceptance criteria:
- Verification:
- Dependencies:
- Files likely touched:
- Estimated scope: XS|S|M|L
```

Sizing:

- `XS`: one small function/config/doc edit.
- `S`: one component, endpoint, script, or test group.
- `M`: one feature slice across a few files.
- `L`: multi-component slice; split if avoidable.
- `XL`: not allowed; break down before writing the final plan.

Break a task down further when it touches unrelated subsystems, takes more than one focused session, has more than three acceptance bullets, or the title needs "and".

## Ordering Rules

- Map dependencies before ordering tasks.
- Build foundations before dependents.
- Put high-risk unknowns early.
- Add checkpoints after every 2-3 tasks.
- State what can run in parallel, what must be sequential, and what needs a shared contract first.
- Each checkpoint must leave the repo in a buildable/testable state.

## Execution Handoff

Use this exact shape and make it the final heading:

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

Do not duplicate raw artifacts. Reference source paths/URLs and redact sensitive data.
