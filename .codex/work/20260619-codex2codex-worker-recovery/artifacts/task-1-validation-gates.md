Salvaged-From-Worker: coding-1

## Summary
- Hardened wave validation so implementation workers with declared file scope must report scoped `files_changed` evidence.
- Rejected implementation artifacts whose body itself reports blocked/unable output.
- Moved review contract validation before generic minimum-length checks so missing verdicts surface as missing verdicts.
- Added fixture-based contract tests for blocked results, blocked artifacts, missing artifacts, missing review verdicts, review `FAIL`, and successful scoped implementation evidence.

## Changed Files
- `codex2codex/scripts/validate_wave.py`
- `codex2codex/scripts/validate_result_contract.py`
- `codex2codex/scripts/test_worker_recovery_contracts.py`

## Verification
- `python3 -m py_compile codex2codex/scripts/validate_wave.py codex2codex/scripts/validate_result_contract.py codex2codex/scripts/test_worker_recovery_contracts.py`
  - Passed.
- `PYTHONPATH=codex2codex/scripts python3 -m unittest test_run_wave_salvage test_worker_recovery_contracts`
  - Passed: 12 tests.
- `python3 -m unittest discover codex2codex/scripts -p "test_run_wave_salvage.py" -v`
  - Passed: 4 tests.
- `python3 -m unittest -v codex2codex.scripts.test_worker_recovery_contracts`
  - Passed: 8 tests.
- Requested exact command: `python3 -m unittest codex2codex/scripts/test_run_wave_salvage.py codex2codex/scripts/test_worker_recovery_contracts.py`
  - Did not load tests in this Python 3.9 environment: `ModuleNotFoundError: No module named 'codex2codex/scripts/test_run_wave_salvage'`.
  - Same tests pass via module/discover invocation above.

## Judgment Calls
- Treated `status.files_changed` as the implementation evidence source because artifact text alone cannot prove scoped product changes.
- Only enforced expected implementation evidence when the manifest declares `files`; report-only workers without file scope are not newly blocked by this gate.
- Kept review artifact `Verdict: FAIL` semantics as an invalid completed wave result, preserving existing fix-wave behavior.

## Residual Risks
- Future no-diff implementation tasks with declared files will fail until the manifest gains an explicit `expects_changes: false` escape hatch.
- If a worker modifies a generated artifact but `meight` fails to populate `files_changed`, validation will now fail rather than risk false success.
