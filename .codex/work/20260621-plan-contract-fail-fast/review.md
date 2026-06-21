# Review

Verdict: PASS

- Functional completeness: `spec2plan/scripts/validate_plan_contract.py` now rejects review-role tasks whose output artifact is not `.codex/work/<topic>/review*.md` unless task text explicitly requires a standalone `Verdict: PASS` and `Verdict: FAIL`.
- Compile-time fail-fast: `plan2do/scripts/compile_execution.py` now rejects the same invalid review artifact shape before writing a task state.
- Regression coverage: Bad fixture fails both `validate_plan_contract.py` and `compile_execution.py`; valid fixture passes both.
- Scope discipline: Code changes are limited to `spec2plan/scripts/validate_plan_contract.py` and `plan2do/scripts/compile_execution.py`; generated artifacts are limited to `.codex/work/20260621-plan-contract-fail-fast/`.
- Architecture simplicity: Implementation uses local Python helpers only; no new dependency, schema system, or Markdown format change.
- Context hygiene: `context-task1.md` through `context-task5.md` exist; raw logs and failed command output are summarized in artifacts.
- Residual risk: Rule logic is duplicated across two scripts; acceptable for v1, but a later shared contract helper may reduce future drift.
