Salvaged-From-Worker: coding-1

## Summary
- Added `PRE_FIRST_ITEM_STALL` classification.
- Detects stale active worker after `turn/started` with no item, no item timestamp, zero tokens.
- Preserves `first_item_started_at` so a worker that previously began an item is not later misclassified after current item fields clear.
- Propagates `stall_classification` through status diagnostics so runners do not depend only on reason text.
- Generic stale-running remains fallback as `WORKER_STALL`.

## Changed Files
- `codex2codex/meight.py`
- `codex2codex/scripts/test_worker_recovery_contracts.py`

## Verification
- `python codex2codex/scripts/test_worker_recovery_contracts.py`
- Result: `Ran 15 tests in 0.701s` → `OK`
- `python codex2codex/scripts/test_meight_status_recovery.py`
- Result: `Ran 4 tests in 0.001s` → `OK`

## Judgment Calls
- Exposed `classify_worker_stall()` for Task 2; no recovery behavior added.
- Added `stall_classification` to diagnostics only.

## Residual Risks
- Artifact file write blocked by local apply_patch credential review; body provided for salvage.
