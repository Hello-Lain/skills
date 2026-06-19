Salvaged-From-Worker: coding-1

## Summary

- Added implementation-wave preflight using `meight doctor --json` plus local `MEIGHT_HOME` writability checks.
- Added bounded `--same-worker-restarts`, `--fresh-worker-restarts`, `--no-preflight`, and `--preflight-timeout` flags to `run_wave.py`.
- Forwarded the same recovery controls through `run_plan.py`.
- Fixed a recovery edge where a nonzero wait could leave the original worker active before a same-name restart.

## Changed Files

- `codex2codex/scripts/run_wave.py`
- `codex2codex/scripts/run_plan.py`
- `codex2codex/scripts/test_run_wave_recovery.py`

## Verification

- `python3 codex2codex/scripts/run_wave.py --help`
- `python3 codex2codex/scripts/run_plan.py --help`
- `python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py`
- Result: `Ran 27 tests` / `OK`

## Judgment Calls

- Used passive `meight doctor --json` for preflight rather than a live worker smoke test to avoid external/provider side effects.
- Kept retry budgets bounded to `0..3`.
- Preserved successful current flows by defaulting to one same-worker restart and one fresh-worker restart.

## Residual Risks

- Preflight confirms local runner readiness, not live provider credentials; transient provider failures remain handled by recovery classification.
