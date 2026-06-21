# Task 2 Execution

- Task: Add `spec2plan` semantic validation.
- Files changed:
  - `spec2plan/scripts/validate_plan_contract.py`
  - `.codex/work/20260621-plan-contract-fail-fast/artifacts/context-task2.md`
- Change summary: Added review-role output artifact validation. Review tasks must output `.codex/work/<topic>/review*.md` unless the task text explicitly requires a standalone `Verdict: PASS` and `Verdict: FAIL` line in the output artifact.
- RED command: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md --mode light`
- RED outcome before patch: `VALID`, exit `0`.
- Verification commands after patch:
  - `python3 -m py_compile /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py`
  - `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/bad-review-artifact-plan.md --mode light`
  - `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/fixtures/valid-review-artifact-plan.md --mode light`
  - `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md --mode light`
- Outcomes:
  - `py_compile`: passed.
  - Bad fixture: failed with Task 1, `Output artifact`, expected repair, exit `1`.
  - Valid fixture: `VALID`, exit `0`.
  - Current plan: `VALID`, exit `0`.
