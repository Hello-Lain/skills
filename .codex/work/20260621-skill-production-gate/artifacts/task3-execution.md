# Task 3 Execution

- Task: Add apply_patch payload preflight helper.
- Changed files:
  - `edit-orchestration/scripts/lint_apply_patch_payload.py`
  - `edit-orchestration/references/apply-patch.md`
  - `edit-orchestration/references/route-matrix.md`
- Behavior:
  - Added optional preflight linter for risky `apply_patch` payloads.
  - Documented preflight for generated, large, multi-hunk, or add-file payloads.
- Verification:
  - `python3 edit-orchestration/scripts/lint_apply_patch_payload.py --self-test`: PASS
  - `python3 .system/skill-creator/scripts/quick_validate.py edit-orchestration`: PASS
- Residual risk: linter catches common grammar issues only; `apply_patch` and diff review remain authoritative.
