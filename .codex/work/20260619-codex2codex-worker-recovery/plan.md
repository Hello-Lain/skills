# Codex2Codex Worker Recovery Implementation Plan

Mode: light
Risk level: High
Confidence: Medium

## Goal
Implement recoverable `codex2codex` worker execution so transient API/tool failures are classified and retried by worker recovery flows, while blocked artifacts, missing diffs, and missing review verdicts fail validation instead of being treated as success.

## Non-Goals
- Do not rewrite `meight.py` into a durable scheduler.
- Do not add unlimited retries.
- Do not make lead-agent implementation or review fallback the default.
- Do not add review quorum as a v1 requirement.
- Do not change external API providers or credential systems.
- Do not change unrelated skills.

## Evidence Inspected
- `.codex/work/20260619-codex2codex-worker-recovery/spec.md`
- `.codex/work/20260619-codex2codex-worker-recovery/manifest.yaml`
- `codex2codex/SKILL.md`
- `codex2codex/README.md`
- `codex2codex/ARCHITECTURE.md`
- `codex2codex/scripts/run_wave.py`
- `codex2codex/scripts/run_plan.py`
- `codex2codex/scripts/validate_wave.py`
- `codex2codex/scripts/validate_result_contract.py`
- `codex2codex/scripts/prepare_wave.py`
- `codex2codex/scripts/plan_to_tasks.py`
- `codex2codex/scripts/test_run_wave_salvage.py`
- `codex2codex/meight.py`
- CodeGraph exploration for `run_wave`, `validate_wave`, `validate_result_contract`, `meight`, `prepare_wave`, and `plan_to_tasks`

## Spec Summary
The confirmed spec requires a bounded worker recovery system. `run_wave.py` should classify transient API/provider/tool failures, steer stalled active workers, follow terminal transient workers, restart workers within a bounded budget, and end with explicit failure categories when recovery is exhausted. Validators must reject blocked artifacts, implementation no-diff cases, and review artifacts without `Verdict: PASS|FAIL`. `PATCH_BODY` may be used as a worker-produced fallback, but runner-side application must validate writable scope before applying changes.

## Domain Language Check
Canonical terms:
- `TRANSIENT_API`: provider timeout, 5xx, unavailable provider, no active credentials, app-server/socket disconnect.
- `TOOL_INFRA`: worker tool backend failure, approval backend failure, `apply_patch` backend unavailable, meight daemon/socket drift.
- `PATCH_CONTEXT`: stale hunk, target changed, patch context mismatch.
- `TASK_BLOCKER`: real ambiguous requirement, design conflict, writable-scope conflict, or repo-unanswerable question.
- `CONTRACT_FAIL`: missing artifact, blocked artifact, missing review verdict, missing expected file change.
- `PATCH_BODY`: worker-emitted patch fallback consumed by the runner only after scope validation.
- `INFRA_FAILED`, `CONTRACT_FAILED`, `TASK_BLOCKED`: explicit terminal wave categories.

Term conflict to resolve: current `run_wave.py` "salvage" can treat blocked-write output as a useful artifact. The new contract should allow artifact-body salvage for reports, but must not allow blocked implementation or review contract failures to pass.

## Current Context
`run_wave.py` currently starts workers, waits for each, salvages artifacts from `ARTIFACT_BODY` or fenced markdown, runs `validate_wave.py`, optionally creates fix waves, then marks tasks complete. It has no explicit failure classifier or bounded recovery state machine.

`validate_wave.py` already rejects some blocked terminal results unless an artifact was salvaged, and validates review artifacts through `validate_result_contract.py`. It does not fully enforce expected target-file diffs for implementation tasks.

`validate_result_contract.py` has review verdict validation and blocked-result rejection. Existing tests in `test_run_wave_salvage.py` cover salvage extraction only, not failure classification, retry behavior, or no-diff gates.

`meight.py` already exposes `status`, `steer`, `follow`, `interrupt`, `start`, `wait`, `result`, and `shutdown`, plus `status.json` fields such as `state`, `last_event_at`, `failure_detail`, `files_changed`, `tokens`, and `current_item`. The plan should prefer these primitives before modifying `meight.py`.

## Assumptions
- Fixture-based tests can cover most `run_wave.py` and validator behavior without live provider calls.
- `run_wave.py` can be refactored to make recovery decisions testable without starting real workers.
- `PATCH_BODY` scope validation can start with path extraction and conservative rejection before becoming a full patch parser.
- `meight.py` only needs minimal status metadata changes, if any.
- Existing review `FAIL` fix-wave behavior should remain intact.

## User Inputs Needed
None before planning. Open implementation choices are recorded under Open Questions and can be resolved during implementation if defaults remain conservative.

## Proposed Approach
Implement strict gates first so bad worker outputs cannot pass. Then add a testable failure classifier and recovery decision layer. Next, wire recovery into `run_wave.py` using existing meight commands. Then add safe `PATCH_BODY` runner application with writable-scope validation. Finally update docs and run a targeted regression suite plus `run_plan.py --dry-run`.

## Scenario Probes
- Worker reports `Blocked: apply_patch approval backend 404` and no files changed: classify `TOOL_INFRA`, recover; if exhausted, fail as `INFRA_FAILED`, not `VALID`.
- Review worker completes without `Verdict: PASS|FAIL`: classify `CONTRACT_FAIL`; rerun/restart review within budget; if exhausted, fail as `CONTRACT_FAILED`.
- Worker result includes valid `PATCH_BODY` that only touches writable scope: runner applies patch, verifies diff, writes implementation artifact.
- Worker `PATCH_BODY` touches outside writable scope: runner rejects and sends the exact error back to worker within recovery budget.
- Worker has `Verdict: FAIL`: existing fix-wave creation remains unchanged.
- Worker asks final `QUESTION:` for a real blocker: return `TASK_BLOCKED` or existing exit-3 question flow, not transient retry.

## Dependency Graph
1. Validator gates must land before recovery can be trusted.
2. Failure taxonomy and decision helpers must land before orchestration loop wiring.
3. Meight status metadata improvements can run in parallel with classifier helpers if needed.
4. Recovery loop wiring depends on classifier helpers and current meight commands.
5. `PATCH_BODY` runner application depends on strict writable-scope validation.
6. Docs depend on the implemented behavior.
7. Final review depends on all implementation and tests.

## Task Breakdown
### Task 1: Harden worker output validation gates

- Description: Strengthen validators and tests so blocked artifacts, missing review verdicts, and missing expected implementation evidence cannot pass as successful wave results.
- Worker role: coding
- Wave: 1
- Acceptance criteria:
  - Blocked implementation result without a valid successful artifact fails.
  - Review artifact without `Verdict: PASS|FAIL` fails.
  - Validation errors distinguish blocked result, missing artifact, missing verdict, and review `FAIL`.
  - New fixture tests cover the prior `apply_patch` blocked-artifact failure mode.
- Verification: `python3 -m unittest codex2codex/scripts/test_run_wave_salvage.py codex2codex/scripts/test_worker_recovery_contracts.py`
- Dependencies: None
- Files likely touched: `codex2codex/scripts/validate_wave.py`, `codex2codex/scripts/validate_result_contract.py`, `codex2codex/scripts/test_worker_recovery_contracts.py`
- Writable scope: `codex2codex/scripts/validate_wave.py`, `codex2codex/scripts/validate_result_contract.py`, `codex2codex/scripts/test_worker_recovery_contracts.py`
- Output artifact: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-1-validation-gates.md`
- Estimated scope: M

### Task 2: Add failure taxonomy and recovery decision helpers

- Description: Add testable failure classification and recovery decision helpers to `run_wave.py`, without changing live worker orchestration yet.
- Worker role: coding
- Wave: 2
- Acceptance criteria:
  - Known provider/tool strings map to `TRANSIENT_API` or `TOOL_INFRA`.
  - Hunk/context failures map to `PATCH_CONTEXT`.
  - Missing artifact/no verdict/no diff maps to `CONTRACT_FAIL`.
  - Real worker `QUESTION:` or repo ambiguity maps to `TASK_BLOCKER`.
  - Helpers are covered by fixture tests.
- Verification: `python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py`
- Dependencies: Task 1
- Files likely touched: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_recovery.py`
- Writable scope: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_recovery.py`
- Output artifact: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-2-taxonomy.md`
- Estimated scope: M

### Task 3: Add minimal worker status support if needed

- Description: Inspect `meight.py` status fields and add minimal metadata only if `run_wave.py` cannot distinguish stalled, failed, interrupted, needs-input, and active states from existing status.
- Worker role: coding
- Wave: 2
- Acceptance criteria:
  - Existing status fields are documented as sufficient, or minimal new fields are added.
  - Any new status field is written atomically with existing `status.json`.
  - No daemon state-machine regression is introduced.
  - Tests or fixture assertions cover status interpretation.
- Verification: `python3 codex2codex/meight.py --help && python3 -m unittest codex2codex/scripts/test_meight_status_recovery.py`
- Dependencies: Task 1
- Files likely touched: `codex2codex/meight.py`, `codex2codex/scripts/test_meight_status_recovery.py`
- Writable scope: `codex2codex/meight.py`, `codex2codex/scripts/test_meight_status_recovery.py`
- Output artifact: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-3-meight-status.md`
- Estimated scope: S

### Task 4: Wire bounded recovery into run_wave

- Description: Replace one-shot wait behavior with a bounded recovery loop using `status`, `steer`, `follow`, same-worker restart, and fresh-worker restart before explicit terminal failure.
- Worker role: coding
- Wave: 3
- Acceptance criteria:
  - Active stalled workers receive a targeted `steer` before interruption.
  - Terminal transient failures receive a `follow` before restart.
  - Same-worker and fresh-worker restart budgets are configurable.
  - Recovery exhaustion emits a clear terminal category and reason.
  - Lead fallback is not invoked.
- Verification: `python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py`
- Dependencies: Task 2, Task 3
- Files likely touched: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_recovery.py`
- Writable scope: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_recovery.py`
- Output artifact: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-4-recovery-loop.md`
- Estimated scope: M

### Task 5: Implement scoped PATCH_BODY fallback

- Description: Add runner-side `PATCH_BODY` extraction, writable-scope validation, conservative patch application, and post-apply diff verification for implementation workers whose direct edit tooling failed.
- Worker role: coding
- Wave: 4
- Acceptance criteria:
  - In-scope `PATCH_BODY` patches are applied by the runner and verified.
  - Absolute paths, path traversal, and out-of-scope paths are rejected.
  - Patch application failures are sent back to the worker within recovery budget.
  - Existing report/artifact salvage behavior remains available for non-patch reports.
- Verification: `python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py codex2codex/scripts/test_run_wave_salvage.py`
- Dependencies: Task 4
- Files likely touched: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_recovery.py`, `codex2codex/scripts/test_run_wave_salvage.py`
- Writable scope: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_recovery.py`, `codex2codex/scripts/test_run_wave_salvage.py`
- Output artifact: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-5-patch-body.md`
- Estimated scope: M

### Task 6: Add preflight and user-visible recovery controls

- Description: Add implementation-wave preflight for worker edit/tool/provider readiness and expose conservative recovery budget controls through `run_wave.py` and pass-through flags in `run_plan.py`.
- Worker role: coding
- Wave: 5
- Acceptance criteria:
  - Preflight can detect edit/tool infra failure before starting expensive waves.
  - `run_wave.py` exposes bounded retry budget flags with safe defaults.
  - `run_plan.py` forwards relevant recovery flags to `run_wave.py`.
  - Defaults preserve current successful flows while preventing false success.
- Verification: `python3 codex2codex/scripts/run_wave.py --help && python3 codex2codex/scripts/run_plan.py --help && python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py`
- Dependencies: Task 5
- Files likely touched: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/test_run_wave_recovery.py`
- Writable scope: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/test_run_wave_recovery.py`
- Output artifact: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-6-preflight-controls.md`
- Estimated scope: M

### Task 7: Update worker prompts and documentation

- Description: Update `codex2codex` skill/docs to document no lead fallback, recovery categories, retry budget semantics, review verdict requirements, and `PATCH_BODY` fallback rules.
- Worker role: coding
- Wave: 6
- Acceptance criteria:
  - `codex2codex/SKILL.md` says lead fallback is prohibited unless explicitly requested.
  - `README.md` documents recovery outcomes and new flags.
  - `ARCHITECTURE.md` documents the recovery state machine and validator gates.
  - Worker brief text in `prepare_wave.py` aligns with the stricter `PATCH_BODY` behavior.
- Verification: `rtk grep -n "lead fallback\\|PATCH_BODY\\|INFRA_FAILED\\|CONTRACT_FAILED\\|TASK_BLOCKED" codex2codex/SKILL.md codex2codex/README.md codex2codex/ARCHITECTURE.md codex2codex/scripts/prepare_wave.py`
- Dependencies: Task 6
- Files likely touched: `codex2codex/SKILL.md`, `codex2codex/README.md`, `codex2codex/ARCHITECTURE.md`, `codex2codex/scripts/prepare_wave.py`
- Writable scope: `codex2codex/SKILL.md`, `codex2codex/README.md`, `codex2codex/ARCHITECTURE.md`, `codex2codex/scripts/prepare_wave.py`
- Output artifact: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-7-docs.md`
- Estimated scope: M

### Task 8: Final recovery review

- Description: Perform independent review of the worker recovery implementation, focusing on false-success prevention, retry bounds, patch scope safety, and compatibility with review `FAIL` fix waves.
- Worker role: review
- Wave: 7
- Acceptance criteria:
  - Review checks all changed `codex2codex` scripts and docs.
  - Review reports any false-success or unsafe patch-application risk.
  - Review includes exact verification commands and `Verdict: PASS` or `Verdict: FAIL`.
- Verification: `python3 -m unittest discover codex2codex/scripts -p "test_*.py" && python3 codex2codex/scripts/run_plan.py .codex/work/20260619-codex2codex-worker-recovery/plan.md --dry-run`
- Dependencies: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7
- Files likely touched: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/validate_wave.py`, `codex2codex/scripts/validate_result_contract.py`, `codex2codex/scripts/prepare_wave.py`, `codex2codex/meight.py`, `codex2codex/SKILL.md`, `codex2codex/README.md`, `codex2codex/ARCHITECTURE.md`
- Writable scope: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/validate_wave.py`, `codex2codex/scripts/validate_result_contract.py`, `codex2codex/scripts/prepare_wave.py`, `codex2codex/meight.py`, `codex2codex/SKILL.md`, `codex2codex/README.md`, `codex2codex/ARCHITECTURE.md`
- Output artifact: `.codex/work/20260619-codex2codex-worker-recovery/review.md`
- Estimated scope: S

## Step-by-Step Plan
1. Add validator regression fixtures for blocked artifacts and missing review verdicts.
2. Tighten validators so blocked/no-verdict cases fail before any recovery loop claims success.
3. Add failure category helpers to `run_wave.py`.
4. Validate whether existing `meight.py` status fields are sufficient; add minimal metadata only if necessary.
5. Wire bounded recovery into worker execution.
6. Add `PATCH_BODY` scoped apply fallback.
7. Add preflight and recovery budget flags.
8. Update docs and worker brief text.
9. Run unit tests and `run_plan.py --dry-run`.
10. Run independent review and fix any `FAIL` findings.

## Parallelization
Wave 1 must run first because validators define the success contract. Wave 2 can run Task 2 and Task 3 in parallel because Task 2 touches `run_wave.py` while Task 3 touches `meight.py`; both depend on Task 1. Waves 3, 4, and 5 are sequential because they all change `run_wave.py`. Wave 6 docs run after behavior is known. Wave 7 review runs last.

## Files / Components Likely Affected
- `codex2codex/scripts/run_wave.py`
- `codex2codex/scripts/run_plan.py`
- `codex2codex/scripts/validate_wave.py`
- `codex2codex/scripts/validate_result_contract.py`
- `codex2codex/scripts/prepare_wave.py`
- `codex2codex/scripts/test_run_wave_salvage.py`
- `codex2codex/scripts/test_run_wave_recovery.py`
- `codex2codex/scripts/test_worker_recovery_contracts.py`
- `codex2codex/scripts/test_meight_status_recovery.py`
- `codex2codex/meight.py`
- `codex2codex/SKILL.md`
- `codex2codex/README.md`
- `codex2codex/ARCHITECTURE.md`

## Owners / Responsibilities
- Coding worker: implement validator gates, recovery helpers, orchestration loop, patch fallback, preflight, tests, and docs.
- Review worker: perform independent PASS/FAIL review of the completed implementation.
- Lead agent: preserve git hygiene, avoid lead fallback, run final validation, report unresolved blockers.

## Validation Plan
- Run contract validator for this plan: `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260619-codex2codex-worker-recovery/plan.md --mode light`.
- Compile worker waves: `python3 codex2codex/scripts/run_plan.py .codex/work/20260619-codex2codex-worker-recovery/plan.md --dry-run`.
- Run unit tests: `python3 -m unittest discover codex2codex/scripts -p "test_*.py"`.
- Run targeted CLI help checks: `python3 codex2codex/scripts/run_wave.py --help`, `python3 codex2codex/scripts/run_plan.py --help`, `python3 codex2codex/meight.py --help`.
- Run targeted grep checks for docs: `rtk grep -n "lead fallback\\|PATCH_BODY\\|INFRA_FAILED\\|CONTRACT_FAILED\\|TASK_BLOCKED" codex2codex`.

## Rollout Plan
Roll out as a local `codex2codex` script and documentation update. No production deployment is involved. After merge, use the stricter runner on low-risk plans first, then use it on implementation plans that need worker recovery.

## Monitoring / Observability
Use `run_wave.py` output categories, worker artifacts, `review-summary.md`, `status.json`, and `meight doctor --json` for observability. Recovery attempts should be summarized in artifacts without raw transcript dumps.

## Documentation / ADR Updates
ADR: Needed

Update `codex2codex/ARCHITECTURE.md` as the architecture record for the worker recovery state machine. Update `codex2codex/README.md` and `codex2codex/SKILL.md` for user-facing behavior.

## Rollback / Recovery Plan
The implementation is reversible by git because it is limited to scripts, tests, and docs. If the stricter gates break existing workflows, revert the validator and `run_wave.py` changes together; do not leave recovery loop and validators out of sync. If new preflight flags break `run_plan.py`, disable the preflight by default while keeping no-false-success validator gates.

## Abort Criteria
- Tests require live provider calls and cannot be made fixture-based.
- Scope validation for `PATCH_BODY` cannot be made conservative enough to prevent out-of-scope writes.
- `meight.py` changes become a durable scheduler rewrite rather than minimal status support.
- Recovery loop creates unbounded retry or token-cost behavior.
- Review finds a path where blocked/no-verdict/no-diff output can still pass.

## Risks
- High coupling in `run_wave.py` may make recovery changes fragile.
- Incorrect failure classification could retry real blockers or fail transient recoverable work.
- Runner-applied patches could bypass worker isolation if scope validation is weak.
- Existing salvage tests may need intentional updates because blocked-report salvage semantics become stricter.
- `run_plan.py --dry-run` may compile output paths under temporary spec dirs; validate generated worker scopes carefully.

## Open Questions
- Default retry budget: use one `steer`, one `follow`, one same-worker restart, and one fresh-worker restart unless implementation reveals this is too expensive.
- Enable `PATCH_BODY` only when direct edit tooling fails for v1; enabling it for all implementation workers can be considered later.
- Add explicit `expects_changes: false` support only if no-diff tasks are common; otherwise require implementation tasks to change scoped files.

## Execution Decision
Do not execute implementation in this planning step. The plan is ready for review and later execution.

## Execution Handoff

- Goal: Implement recoverable `codex2codex` worker execution with strict no-false-success gates.
- Current state: Confirmed spec exists; executable light plan generated; implementation not executed.
- Authoritative artifacts: `.codex/work/20260619-codex2codex-worker-recovery/spec.md`, `.codex/work/20260619-codex2codex-worker-recovery/plan.md`
- Decisions: Use light planning; do not self-host this planning pass through heavy `codex2codex` because `codex2codex` recovery is the target system under repair.
- Verification: Validate plan contract, run `run_plan.py --dry-run`, then execute tasks with unit tests and final review.
- Remaining risks: Core runner changes are high risk; fixture coverage must prevent false success and unsafe `PATCH_BODY` application.
- Next action: Run plan validation and dry-run, then execute Task 1 if implementation is approved.
- Suggested skills: codex2codex, test-driven-development, debugging-and-error-recovery, api-and-interface-design, apply-patch.
- Redactions / omitted raw data: No raw worker transcripts or secrets included.
