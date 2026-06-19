Salvaged-From-Worker: coding-2

## Summary

- Confirmed existing `meight.py` status fields are sufficient for recovery interpretation: `state`, `needs_input_source`, `needs_input_detail`, `stalled`, `stalled_reason`, `failure_detail`, and activity timestamps.
- Added fixture tests for wait-state mapping and worker diagnostics instead of changing daemon state-machine behavior.
- No `meight.py` implementation changes were needed.

## Changed Files

- `codex2codex/scripts/test_meight_status_recovery.py`

## Verification

- `python3 codex2codex/meight.py --help`
- `python3 -m unittest codex2codex/scripts/test_meight_status_recovery.py`
- Result: `Ran 3 tests in 0.001s` / `OK`

## Judgment Calls

- Kept Task 3 minimal because `worker_diagnostics()` already exposes enough metadata for stalled, failed, interrupted, needs-input, and active workers.
- Preserved daemon behavior and avoided scheduler rewrites.

## Residual Risks

- The worker hit a transient provider credential 404 while writing its final artifact; lead verified the code and tests locally.
