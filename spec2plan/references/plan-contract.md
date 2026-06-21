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
- `## Implementation Map`
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
- `## Plan Self-Review`
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
- Reject vague execution language. Do not write `TBD`, `TODO`, `later`, `as needed`, `relevant files`, `appropriate tests`, `etc.`, `相关`, `必要时`, or `适当` in executable fields.
- If a fact is unknown, put it under `Open Questions` or `Assumptions` and state why repo evidence cannot answer it.
- Before final handoff, run `scripts/validate_plan_contract.py <plan.md> --mode light|heavy`. This validator must also pass `plan2do/scripts/compile_execution.py` compatibility. If it fails, revise the plan from the exact validator errors and rerun until it passes, or stop with the blocking errors. Never hand off an invalid canonical plan.

## Skill Production Plans

When a plan creates or materially updates a skill, validator script, workflow/safety contract, or skill metadata:

- Include `skill-tokenless/references/skill-production-gate.md` in `Evidence Inspected`.
- Add exact production-gate files in the `Implementation Map`.
- Add a task that writes a production report under `.codex/work/<topic>/artifacts/production-report.md`.
- Add verification with `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/<topic>/artifacts/production-report.md --root <repo>`.
- Add a final `reviewer` gate task unless the change is typo-only or formatting-only and review-exempt with reason.
- In `Execution Handoff`, carry the production report path, reviewer report path, and any skipped gate reasons.

## Implementation Map

Before `Task Breakdown`, anchor the plan to concrete repo evidence:

- Files: exact repo-relative paths or conservative globs, with purpose.
- Symbols / APIs: functions, classes, commands, endpoints, schemas, or config keys likely affected.
- Tests: exact test files, suites, or new test locations.
- Commands: exact pre-check and post-check commands, or why not runnable yet.
- Data / migration impact: data touched, migration/backfill needs, or `Not applicable` with reason.

## Task Breakdown Rules

Prefer vertical slices that deliver a working path over horizontal layers.

Each task must include:

```md
### Task N: Short title

- Description:
- Worker role: coding|devops|review|consult|sa
- Wave: N
- Acceptance criteria:
- Verification:
- Concrete edits:
- Interfaces / contracts changed:
- Test cases:
- Pre-check commands:
- Post-check commands:
- Dependencies:
- Files likely touched:
- Writable scope:
- Output artifact:
- Estimated scope: XS|S|M|L
```

Each required field must have a non-empty value on the same line as the field label. Supporting bullets may follow. Do not leave a required field line blank when the first supporting bullet contains `:`, because the execution compiler treats `- Label:` lines as fields.

Sizing:

- `XS`: one small function/config/doc edit.
- `S`: one component, endpoint, script, or test group.
- `M`: one feature slice across a few files.
- `L`: multi-component slice; split if avoidable.
- `XL`: not allowed; break down before writing the final plan.

Break a task down further when it touches unrelated subsystems, takes more than one focused session, has more than three acceptance bullets, or the title needs "and".

Each task should be executable by another agent without rereading the raw spec. Include concrete paths, symbols, commands, assertions, and artifact paths. Avoid generic tasks like "update related code", "add tests", or "clean up".

## Ordering Rules

- Map dependencies before ordering tasks.
- Build foundations before dependents.
- Put high-risk unknowns early.
- Add checkpoints after every 2-3 tasks.
- State what can run in parallel, what must be sequential, and what needs a shared contract first.
- Each checkpoint must leave the repo in a buildable/testable state.
- Tasks in the same wave must not have overlapping `Writable scope` unless they are `review`, `consult`, or `sa`.
- `Writable scope` must use exact repo-relative paths or conservative directory globs; do not write "TBD" in final plans.
- `Output artifact` should be under `.codex/work/<yyyyMMdd>-<topic-slug>/artifacts/` for implementation/consult tasks and `.codex/work/<yyyyMMdd>-<topic-slug>/review*.md` for reviews.
- Add a final review task/wave for multi-worker implementation unless the work is docs-only or explicitly review-exempt.
- `Parallelization` must name wave groups and explain why same-wave tasks are safe to run together.
- Artifact parent dirs must be creatable before execution; plan setup should create them or name the command that will.
- Plans intended for `$codex2codex` must pass `scripts/run_plan.py <plan.md> --dry-run` or explicitly record why dry-run is unavailable.

## Micro-Step Rules

In `Step-by-Step Plan`, each step should be a 2-5 minute action and must include at least one exact path, symbol/API, command, or output artifact. Split broader steps before finalizing.

## Plan Self-Review

Answer these checks explicitly:

- Every task has exact writable scope and non-overlapping same-wave writes.
- Every behavior change has regression or smoke coverage.
- Every unknown is in `Assumptions` or `Open Questions`, not hidden in task text.
- Rollback, abort criteria, and monitoring are specific enough for the risk level.
- A fresh agent can execute Task 1 from this plan without raw transcript context.

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
