Salvaged-From-Worker: coding-1-retry

## Summary

- Added canonical recovery taxonomy constants in `codex2codex/scripts/run_wave.py`.
- Added pure classification helpers for failure text, worker status/result/validation signals, and contract gate signals.
- Added `RecoveryDecision` helper to map category + retry budget to `retry` or terminal `INFRA_FAILED`, `CONTRACT_FAILED`, `TASK_BLOCKED`.
- Added focused fixture tests in `codex2codex/scripts/test_run_wave_recovery.py`.

## Changed Files

- `codex2codex/scripts/run_wave.py`
- `codex2codex/scripts/test_run_wave_recovery.py`

## Verification

- `python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py`
- Result: `Ran 11 tests in 0.001s` / `OK`

## Judgment Calls

- Kept helpers pure and unwired, matching Task 2 scope so live worker orchestration remains unchanged for later waves.
- Prioritized explicit `QUESTION:` / worker `needs_input_source=question` as `TASK_BLOCKER` before other text classifications.
- Treated exhausted `PATCH_CONTEXT` as `CONTRACT_FAILED`, because patch application needs contract-level runner handling in later waves.

## Residual Risks

- Regex fixtures cover known planned strings, but future provider/tool messages may need taxonomy additions.
- Decision helper currently exposes retry/stop only; later orchestration may need separate steer/follow/restart action names.
