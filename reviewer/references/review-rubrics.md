# Review Rubrics

Use these as defaults after checking local user goals, `AGENTS.md`, source artifacts, and producing skill contracts.

## Pipeline Artifacts

### `idea-refine`

- Problem and target user are specific.
- Success criteria are observable.
- Variations are meaningfully different, not shallow restatements.
- Clusters include value, feasibility, and differentiation tradeoffs.
- Assumptions include validation paths and kill conditions.
- MVP tests the core assumption.
- Not Doing list protects focus.

### `interview-me`

- User explicitly confirmed the restated intent before final spec.
- User, why, success, constraints, scope, and non-goals are explicit.
- Requirements describe behavior, not labels or vibes.
- Assumptions are marked and testable.
- Acceptance checks are judgeable by a future agent.

### `spec2plan`

- Plan contract sections exist and are non-empty.
- Implementation map names exact files, commands, tests, and data impact.
- Tasks are dependency-ordered, executable, and have non-overlapping same-wave writable scopes.
- Verification and rollback are concrete.
- Unknowns are in assumptions or open questions, not hidden in tasks.

### `plan2do`

- Every task is complete or explicitly blocked.
- Verification evidence exists.
- Review verdict is present for non-trivial work.
- Rework guidance exists for failed checks.
- Final report does not claim success while blockers remain.

## Code Quality

- Correctness and behavioral regressions.
- Test, lint, type, or smoke coverage for changed behavior.
- API, data, security, privacy, and compatibility risk.
- Error handling and boundary cases.
- Simplicity, reuse, and deletion of unnecessary abstraction.
- No unrelated edits, hidden global state, or speculative configuration.

## Research Idea Feasibility

- Problem is concrete and important for a named user or field.
- Novelty claim is scoped and evidence level is stated.
- Baselines and comparison axes are named.
- Data availability and labeling cost are realistic.
- Evaluation metric, dataset/input, control, expected signal, cost, and stop condition are defined.
- Failure modes and invalidating evidence are explicit.
- MVP can test the core claim without full-scale buildout.

## Documentation And Process

- Enables a specific decision or action.
- Names audience and prerequisites.
- Contains exact commands, paths, examples, or checks where needed.
- Separates authoritative guidance from historical notes.
- Avoids duplicate, stale, or process-only docs.

## Execution Results

- Claimed outcomes map to tasks or acceptance criteria.
- Commands and manual checks are recorded with outcomes.
- Skipped checks have concrete blockers.
- Artifacts exist and are not just raw logs.
- Scope stayed within plan or scope changes are justified.
- Final status matches evidence.
