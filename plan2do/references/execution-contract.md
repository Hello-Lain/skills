# Plan2Do Execution Contract

Use this contract after reading `SKILL.md` and before editing files for a plan.

## Focused Context Pack

Use `/data/lcq/.codex/skills/context-engineering` as the governing source for context artifact granularity. Default to one wave-level pack for a coherent non-trivial plan wave, not one task-level pack per task. Create a task-level pack only when the specific task has risk, ambiguity, failure, confidence loss, or cross-cutting scope.

Wave pack path:

```text
<plan-workspace>/artifacts/context-wave<N>.md
```

Task pack path for escalations:

```text
<plan-workspace>/artifacts/context-task<N>.md
```

Pack shape:

```markdown
TASK:
- Plan path:
- Current task:
- Phase: implement | verify | review | rework | report
- Context state:
- Risk level:

AUTHORITATIVE SOURCES:
- User goal:
- Plan sections:
- Files/tests/configs:
- Existing pattern:

CONSTRAINTS:
- Must:
- Must not:

UNKNOWN / CONFLICT:
-
```

Store the chosen pack under the path above. If a task-level pack is skipped because the wave pack is sufficient, record the wave pack path in that task's execution artifact.

## Plan Intake Gate

Continue only when the plan has:

- `Task Breakdown` with `### Task N`;
- dependency order or waves;
- `Writable scope`;
- `Verification`;
- `Acceptance criteria`;
- `Output artifact`;
- validation, rollback, abort, risk, and handoff sections.

If the plan is missing executable fields, run the upstream plan validator when available or stop with `PLAN_INVALID`.

For non-trivial primary-agent execution, run:

```bash
python /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py <plan.md>
```

Treat `<plan-workspace>/execution/tasks.json` as the task checklist. If compilation fails, stop with `PLAN_INVALID`.
During execution, update each task status to `complete` only after its output artifact and verification evidence exist. Leave failed work as `pending` or `blocked`; final success requires every task status to be `complete`.
Re-running the compiler preserves existing task statuses by default; use `--reset-status` only when intentionally restarting execution.

## Primary-Agent Mode

Primary-agent mode is the default.

Rules:

- Work one task or coherent task group at a time.
- Rehydrate current source files before edits.
- Use `apply_patch` for manual edits.
- Do not touch files outside writable scope without updating the execution note and confirming the scope is still safe.
- Preserve unrelated dirty work.
- Keep raw command output, logs, and diffs out of the active narrative; write summaries and paths.
- Run the plan's pre-checks and post-checks when safe.
- Write task artifacts to `<plan-workspace>/artifacts/`.
- Keep each compiled task's `output_artifact` non-empty before marking that task complete.

## Context Engineering Gates

Use `/data/lcq/.codex/skills/context-engineering` as the governing source.

Mandatory triggers:

- Rehydrate before editing a task's writable scope.
- Rehydrate before final acceptance; summaries and prior chat are not evidence.
- Emit a `Decision Packet` before destructive, production, security, public API, schema/data, dependency, or hard-to-rollback work.
- Emit a `Context Capsule` at major phase boundaries when execution context is bloated, stale, or about to be compacted.
- Emit `COMPACT_NOW` only after a Context Capsule when no verified compaction actuator exists and context pressure threatens execution quality.
- Quarantine raw logs, full diffs, worker transcripts, and stale failed attempts into artifacts; keep only summaries and paths active.

If evidence conflicts, stop with a context conflict summary instead of guessing.

## Codex2Codex Mode

Use only when the user explicitly requests `codex2codex`.

Minimum flow:

1. Read `/data/lcq/.codex/skills/codex2codex/SKILL.md`.
2. Run `codex2codex/scripts/run_plan.py <plan.md> --dry-run` when available to inspect workers; dry-run is not a quality gate.
3. Run the requested waves or plan through `codex2codex`.
4. Accept only summarized worker artifacts, review verdicts, verification, decisions, blockers, and cleanup status.
5. Keep transcripts and raw event streams out of primary context.
6. Run `validate_execution_complete.py` when the backend produced a compatible spec directory.

The primary agent still owns final acceptance, blocker escalation, and rework guidance.

## Quality Review Gate

Before final completion, review:

- Functional completeness against the plan acceptance criteria.
- Verification status and any skipped checks.
- Regression risk in touched files.
- Architecture simplicity: no speculative abstraction, needless configurability, or hidden global state.
- Scope discipline: no unrelated edits.
- Documentation or runbook changes when behavior or usage changed.
- Artifact completeness and redaction.

Review result must be either `Verdict: PASS` or `Verdict: FAIL`.

Use `references/review-rubric.md` for PASS/FAIL conditions.

## Rework Guidance

Before each fix cycle, write `<plan-workspace>/artifacts/rework-guidance[-N].md`:

```markdown
# Rework Guidance

- Evidence:
- Defect:
- Impact:
- Required change:
- Writable scope:
- Verification:
- Cycle:
```

Use at most two fix cycles per failed task or review scope unless the user changes the limit. If the same failure remains, stop with `BLOCKED_REWORK_LIMIT`.

## Failure Classes

- `PLAN_INVALID`: plan lacks executable fields or conflicts with user instruction.
- `VERIFY_FAILED`: command or manual check failed.
- `REVIEW_FAILED`: review found functional, regression, or architecture issues.
- `SCOPE_VIOLATION`: edits touched files outside writable scope without a justified execution note.
- `CONTEXT_CONFLICT`: current source files, plan, artifacts, or user constraints disagree.
- `APPROVAL_REQUIRED`: user approval is needed for destructive, production, security, or rollback actions.
- `BLOCKED_REWORK_LIMIT`: bounded rework did not resolve the defect.
- `TOOLING_BLOCKED`: required local tool is unavailable and no safe fallback exists.

Use `references/failure-policy.md` for failure response and rework flow.

Do not report success for any failure class.

## Artifacts

Use the plan workspace:

```text
<plan-workspace>/
  artifacts/
    context-wave<N>.md
    context-task<N>.md
    task<N>-execution.md
    task<N>-verification.md
    review.md
    rework-guidance.md
    final-report.md
  execution/
    tasks.json
```

Artifacts should summarize exact commands, relevant results, changed files, and decisions. Avoid raw secrets, credentials, private data, full transcripts, or large logs.

## Final Acceptance

Before reporting success:

- Rehydrate the current plan, changed files, verification results, and review artifact.
- Confirm every required task is complete or explicitly blocked.
- Confirm verification passed or has a concrete blocker.
- Confirm review is `Verdict: PASS` for non-trivial plans or explicitly exempted with reason.
- Confirm no unresolved failure class remains.
- Confirm artifacts exist for execution, verification, review, rework cycles, and final report.
- If `<plan-workspace>/execution/tasks.json` exists, run `python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py <plan-workspace>` and require `VALID`.

If any check fails, final status is `INCOMPLETE`, not success.

## Final Report

Final response and `artifacts/final-report.md` must include:

- Mode: `primary-agent` or `codex2codex`.
- Status: `COMPLETE` or `INCOMPLETE`.
- Plan path.
- Tasks completed.
- Files changed.
- Verification commands and outcomes.
- Review verdict.
- Rework cycles.
- Artifact paths.
- Blockers or risks.
- Raw data omitted.

If incomplete, state the failure class and next action.
