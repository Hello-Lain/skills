SPEC2PLAN_ARTIFACT_V1
phase: synthesizer
status: complete
artifact:
# Codex2Codex Continuation-First Recovery Plan

Mode: heavy
Risk level: Medium
Confidence: High

## Goal
Implement continuation-first recovery for `codex2codex` worker waves so transient provider/tool interruptions are resumed on the same thread before bounded restart/failure, while preserving strict artifact, review, diff, and scope contracts.

## Non-Goals
No live provider smoke test by default. No infinite retry. No lead fallback implementation for worker-scoped changes. No meight runtime replacement. No git branch, commit, or history changes.

## Evidence Inspected
- `.codex/work/20260619-codex2codex-continuation-recovery/spec.md`
- `.codex/work/20260619-codex2codex-continuation-recovery/manifest.yaml`
- `codex2codex/SKILL.md`
- `spec2plan/references/plan-contract.md`
- `spec2plan/references/heavy-mode.md`
- `references/artifact-contract.md`
- `codex2codex/scripts/run_wave.py`
- `codex2codex/scripts/run_plan.py`
- `codex2codex/scripts/validate_wave.py`
- `codex2codex/scripts/test_run_wave_recovery.py`
- `codex2codex/scripts/test_worker_recovery_contracts.py`

## Spec Summary
The runner must classify provider/stream/tool interruptions as recoverable, try `meight follow` on the same worker thread up to the default budget of `3`, track progress signals, persist attempt ledgers and summaries, escalate only after bounded no-progress recovery, avoid fix waves for review infrastructure failures, mark stale fix waves after later PASS reviews, and share exact-file versus directory scope semantics between runner and validator.

## Domain Language Check
Canonical terms from the spec and code: `same-thread continuation`, `same-worker restart`, `fresh-worker restart`, `TRANSIENT_API`, `TOOL_INFRA`, `PATCH_CONTEXT`, `CONTRACT_FAIL`, `TASK_BLOCKER`, `REVIEW_UNAVAILABLE`, `INFRA_FAILED`, `CONTRACT_FAILED`, `TASK_BLOCKED`, `attempts.jsonl`, `summary.json`, `fix-wave-obsolete`. No conflicting repo terms found.

## Current Context
Implementation should be isolated to `codex2codex/scripts`. The repo has unrelated dirty files under `interview-me/` and `rtk-doctor/`; those must remain untouched. The plan must be codex2codex-dry-run compatible and preserve existing CLI flags.

## Assumptions
- `meight follow` is the intended same-thread continuation command.
- Provider 404/no active credentials may be transient in this local provider path.
- Durable runner state under `<spec_dir>/runs/<wave-slug>/` is acceptable because spec workspaces already hold generated worker state.
- Sidecar metadata as `<artifact>.meta.json` is less disruptive than Markdown frontmatter.

## User Inputs Needed
None. Open policy choices are resolved with conservative defaults: nonzero `REVIEW_UNAVAILABLE`, sidecar JSON metadata, obsolete markers instead of deleting stale fix waves, and no default live provider smoke.

## Proposed Approach
1. Extract shared scope matching into a small stdlib-only helper.
2. Extend failure taxonomy and same-thread continuation in `run_wave.py`.
3. Persist per-worker attempt ledgers and per-wave summaries.
4. Preserve strict validation and treat `wait exit 3` or unresolved `QUESTION:` as non-success.
5. Add review-infra unavailable handling that suppresses code fix-wave generation.
6. Add artifact metadata and PASS-review stale fix-wave marking.
7. Cover the new behavior with deterministic unit tests and run the full `codex2codex/scripts` suite.

## Scenario Probes
- Provider stream closes after partial work: runner follows same thread with recovery brief, records a continuation attempt, then validates final artifact.
- Worker repeats transient failure with no progress: runner exhausts same-thread budget, then escalates to restart budgets and terminal category.
- Review worker fails due infrastructure: wave exits nonzero with `REVIEW_UNAVAILABLE`, but no code fix wave is created.
- Later review PASS supersedes earlier FAIL: derived fix wave is marked `fix-wave-obsolete` rather than silently deleted.
- `src/target.py/child.txt` reported for file scope `src/target.py`: runner and validator reject it.
- Child path reported under directory scope `src`: runner and validator accept it.

## Dependency Graph
Task 1 -> Task 2 -> Task 3 -> Task 4 -> Task 5.

## Task Breakdown
### Task 1: Share scope contract

- Description: Add a reusable helper for exact-file and directory-scope matching, then use it from runner and validator.
- Worker role: coding
- Wave: 1
- Acceptance criteria: File scope rejects child paths for exact files; directory scope accepts child paths for explicit directories; helper stays stdlib-only.
- Verification: `rtk python3 -m py_compile codex2codex/scripts/scope_contract.py codex2codex/scripts/run_wave.py codex2codex/scripts/validate_wave.py`
- Dependencies: None
- Files likely touched: `codex2codex/scripts/scope_contract.py`, `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/validate_wave.py`
- Writable scope: `codex2codex/scripts/scope_contract.py`, `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/validate_wave.py`
- Output artifact: `.codex/work/20260619-codex2codex-continuation-recovery/artifacts/task-1-scope-contract.md`
- Estimated scope: M

### Task 2: Add continuation-first recovery ledger

- Description: Expand transient classification, add default `--same-thread-continues 3`, follow same worker thread before restart, track progress snapshots, and persist `attempts.jsonl` plus `summary.json`.
- Worker role: coding
- Wave: 2
- Acceptance criteria: Transient provider/stream failures call `follow` before restart; recovery brief includes worker name, category, reason, scope, and output; durable state reconstructs final outcome.
- Verification: `rtk python3 -m unittest codex2codex.scripts.test_run_wave_recovery`
- Dependencies: Task 1
- Files likely touched: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/test_run_wave_recovery.py`
- Writable scope: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/test_run_wave_recovery.py`
- Output artifact: `.codex/work/20260619-codex2codex-continuation-recovery/artifacts/task-2-continuation-ledger.md`
- Estimated scope: M

### Task 3: Handle review unavailable and stale fix waves

- Description: Add `REVIEW_UNAVAILABLE`, suppress fix-wave creation for review infrastructure failures, write artifact sidecar metadata on salvage, and mark stale fix waves obsolete after PASS reviews.
- Worker role: coding
- Wave: 3
- Acceptance criteria: Infra-only review failure exits nonzero without code fix wave; real review FAIL still creates fix wave; PASS review can mark derived fix wave `fix-wave-obsolete`.
- Verification: `rtk python3 -m unittest codex2codex.scripts.test_run_wave_recovery`
- Dependencies: Task 2
- Files likely touched: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_recovery.py`
- Writable scope: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_recovery.py`
- Output artifact: `.codex/work/20260619-codex2codex-continuation-recovery/artifacts/task-3-review-staleness.md`
- Estimated scope: M

### Task 4: Complete regression coverage

- Description: Add and stabilize tests for transient taxonomy, same-thread budget, durable ledgers, shared scope semantics, review unavailable, stale fix-wave marking, and run-plan CLI forwarding.
- Worker role: coding
- Wave: 4
- Acceptance criteria: Targeted recovery tests pass; full `codex2codex/scripts` unittest discovery passes; py_compile passes for changed scripts.
- Verification: `rtk python3 -m unittest discover codex2codex/scripts -p "test_*.py"`
- Dependencies: Task 3
- Files likely touched: `codex2codex/scripts/test_run_wave_recovery.py`
- Writable scope: `codex2codex/scripts/test_run_wave_recovery.py`
- Output artifact: `.codex/work/20260619-codex2codex-continuation-recovery/artifacts/task-4-regression-tests.md`
- Estimated scope: S

### Task 5: Review recovery implementation

- Description: Independently inspect changed recovery code and tests for scope leaks, retry loops, stale artifact behavior, CLI compatibility, and validation gaps.
- Worker role: review
- Wave: 5
- Acceptance criteria: Review artifact includes findings, verification, and `Verdict: PASS|FAIL`; any FAIL points to concrete file/line and required fix.
- Verification: `rtk python3 -m unittest discover codex2codex/scripts -p "test_*.py"`
- Dependencies: Task 4
- Files likely touched: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/validate_wave.py`, `codex2codex/scripts/scope_contract.py`, `codex2codex/scripts/test_run_wave_recovery.py`
- Writable scope: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/validate_wave.py`, `codex2codex/scripts/scope_contract.py`, `codex2codex/scripts/test_run_wave_recovery.py`
- Output artifact: `.codex/work/20260619-codex2codex-continuation-recovery/review.md`
- Estimated scope: S

## Step-by-Step Plan
1. Implement Task 1 and run py_compile.
2. Implement Task 2 and run targeted recovery tests.
3. Implement Task 3 and rerun targeted recovery tests.
4. Implement Task 4 and run full unittest discovery.
5. Run Task 5 review and address any FAIL with a bounded fix wave.
6. Validate the plan and codex2codex dry-run.

## Parallelization
No implementation tasks should run in parallel because Tasks 1 to 4 share `run_wave.py` and recovery behavior dependencies. Task 5 must run after implementation. This intentionally favors safety over concurrency.

## Files / Components Likely Affected
- `codex2codex/scripts/run_wave.py`
- `codex2codex/scripts/run_plan.py`
- `codex2codex/scripts/validate_wave.py`
- `codex2codex/scripts/scope_contract.py`
- `codex2codex/scripts/test_run_wave_recovery.py`
- `.codex/work/20260619-codex2codex-continuation-recovery/plan.md`
- `.codex/work/20260619-codex2codex-continuation-recovery/subagents/`
- `.codex/work/20260619-codex2codex-continuation-recovery/manifest.yaml`

## Owners / Responsibilities
- coding worker: implement scoped runner, validator, CLI, and test changes.
- review worker: verify contract correctness and regression risk.
- lead agent: preserve unrelated dirty files, run validation, update canonical work artifacts, and report final status.

## Validation Plan
- `rtk python3 -m py_compile codex2codex/scripts/run_wave.py codex2codex/scripts/run_plan.py codex2codex/scripts/validate_wave.py codex2codex/scripts/scope_contract.py codex2codex/scripts/test_run_wave_recovery.py`
- `rtk python3 -m unittest codex2codex.scripts.test_run_wave_recovery codex2codex.scripts.test_worker_recovery_contracts`
- `rtk python3 -m unittest discover codex2codex/scripts -p "test_*.py"`
- `rtk python3 spec2plan/scripts/validate_subagent_artifact.py planner .codex/work/20260619-codex2codex-continuation-recovery/subagents/planner.md`
- `rtk python3 spec2plan/scripts/validate_subagent_artifact.py reviewer .codex/work/20260619-codex2codex-continuation-recovery/subagents/reviewer.md`
- `rtk python3 spec2plan/scripts/validate_subagent_artifact.py synthesizer .codex/work/20260619-codex2codex-continuation-recovery/subagents/synthesizer.md`
- `rtk python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260619-codex2codex-continuation-recovery/plan.md --mode heavy`
- `rtk python3 codex2codex/scripts/run_plan.py .codex/work/20260619-codex2codex-continuation-recovery/plan.md --dry-run`

## Rollout Plan
This is local runner/tooling behavior. Roll out by merging the script and test changes after validation. Existing CLI behavior remains compatible; the only new default is bounded same-thread continuation with `--same-thread-continues 3`.

## Monitoring / Observability
Use `.codex/work/<slug>/runs/<wave-slug>/<worker>/attempts.jsonl`, worker `summary.json`, wave `summary.json`, artifact `.meta.json`, and `tasks.md` `fix-wave-obsolete` markers to reconstruct outcomes after PTY/session loss.

## Documentation / ADR Updates
ADR: Not needed. The behavior is covered by the spec, plan, tests, and codex2codex skill contract. Consider a future README note if external users rely on runner flags.

## Rollback / Recovery Plan
Revert the scoped script/test changes if recovery behavior regresses. Because no data migration or history rewrite is involved, rollback is a normal code revert. Generated `runs/` ledgers and `.meta.json` sidecars can be ignored or deleted if not needed for debugging.

## Abort Criteria
- Same-thread continuation can loop beyond configured budgets.
- `wait exit 0` bypasses artifact/verdict/diff/scope validation.
- `wait exit 3` or unresolved `QUESTION:` is reported as success.
- Review infra failure creates a code fix wave.
- Runner and validator disagree on file-vs-directory scope semantics.
- Full `codex2codex/scripts` tests fail.

## Risks
- Progress heuristics may treat noisy status/token changes as useful progress; bounded budgets mitigate this.
- Provider 404/no active credentials might be persistently fatal in some environments; terminal `INFRA_FAILED` still surfaces after budget exhaustion.
- Marking stale fix waves obsolete could miss unusual review path formats; tests should cover absolute, spec-relative, repo-relative, and basename refs where practical.
- Sidecar metadata is generated state; consumers must not treat it as a source artifact.

## Open Questions
- Should a future release expose live provider smoke as an opt-in flag? Not required for this implementation.
- Should stale fix waves eventually be ignored by runner automatically, beyond marking them obsolete? Not required for this implementation.

## Execution Decision
Proceed. The implementation has already been applied in the current workspace and should be accepted only after the validation commands pass.

## Execution Handoff

- Goal: Deliver continuation-first recovery for `codex2codex`.
- Current state: Implementation and regression tests are present in the workspace.
- Authoritative artifacts: `.codex/work/20260619-codex2codex-continuation-recovery/spec.md`, `.codex/work/20260619-codex2codex-continuation-recovery/plan.md`, `.codex/work/20260619-codex2codex-continuation-recovery/subagents/`.
- Decisions: Use `--same-thread-continues 3`; use sidecar artifact metadata; mark stale fix waves obsolete; keep review infra failures nonzero without fix-wave creation.
- Verification: Run py_compile, targeted recovery unittests, full `codex2codex/scripts` unittest discovery, heavy plan validation, and `run_plan.py --dry-run`.
- Remaining risks: No live provider smoke was run; progress heuristics depend on available meight status fields.
- Next action: Review the diff and run any desired live meight smoke manually if provider credentials are available.
- Suggested skills: `codex2codex`, `test-driven-development`, `git-workflow-and-versioning`.
- Redactions / omitted raw data: Raw worker transcripts, provider logs, and unrelated dirty file diffs omitted.
SPEC2PLAN_ARTIFACT_END
