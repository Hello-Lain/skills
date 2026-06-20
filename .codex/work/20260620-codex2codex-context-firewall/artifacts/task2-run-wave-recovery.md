Salvaged-From-Worker: coding-1

## Summary
- Added `PRE_FIRST_ITEM_STALL` as infra-recoverable.
- Implemented rotate/shutdown → fresh `MEIGHT_HOME` → nonce smoke → one retry.
- Smoke failure skips original retry; retry failure terminates.
- New PRE_FIRST ledger entries omit `result_tail`.
- Fixed review-blocking recovery semantics:
  - Retry contract failures now terminate as `CONTRACT_FAILED`, not infra failure.
  - Nonce smoke requires the exact nonce as the full result.
  - `--fresh-worker-restarts 0` disables fresh pre-first-item recovery.

## Changed Files
- `codex2codex/scripts/run_wave.py`
- `codex2codex/scripts/test_run_wave_recovery.py`

## Verification
- `python codex2codex/scripts/test_run_wave_recovery.py` → OK, 42 tests.
- `python codex2codex/scripts/test_worker_recovery_contracts.py` → OK, 15 tests.

## Residual Risks
- Live daemon/app-server rotation depends on real `meight shutdown`; unit coverage mocks it.
