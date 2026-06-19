Salvaged-From-Worker: coding-1

## Summary

- Wired `run_wave.py` worker waits through a bounded recovery loop.
- Added status-driven stalled-worker `steer` before `interrupt`.
- Added terminal recoverable `follow` before restart.
- Added same-worker and fresh-worker restart budgets as internal runner parameters for Task 6 CLI exposure.
- Fresh-worker success is mirrored back to the original manifest worker status/result so existing validation still targets manifest names.
- Recovery exhaustion now emits `terminal_category`, `failure_category`, and reason.

## Changed Files

- `codex2codex/scripts/run_wave.py`
- `codex2codex/scripts/test_run_wave_recovery.py`
- `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-4-recovery-loop.md`

## Verification

```text
$ python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py
...............
----------------------------------------------------------------------
Ran 15 tests in 0.006s

OK
```

## Judgment Calls

- Kept budget configuration internal to `_run_manifest`/`_wait_workers`; Task 6 is scoped to expose CLI flags.
- Used `follow` once per worker recovery sequence before restart to avoid looping on a poisoned thread.
- Used fresh worker names as `<original>-recovery-<n>` and copied successful terminal artifacts/status back to the manifest worker name for validator compatibility.
- Did not invoke or add lead fallback behavior.

## Residual Risks

- Real meight timing around `interrupt` can still be slow if a worker ignores interruption; loop waits once after successful interrupt to let terminal status settle.
- Fresh-worker mirroring copies status/result/events only; other worker directory diagnostics remain under the fresh worker name.
