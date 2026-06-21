# Task 6: Forward-Test Notes

- Status: complete

## Scenario Results

- Fast path: `SKILL.md` routes small unique-context edits to `apply_patch`, followed by diff and verification gate.
- Patch recovery path: `failure-recovery.md` requires raw source re-read, one small retry, then stop if unsafe.
- Structural rewrite path: `route-matrix.md` selects `ast-grep` or codemod helpers for repeated syntax-aware edits.
- Selected-route self-check failure: `prepare_edit_tools.py --check-only --tool ast-grep --json` returned nonzero when `ast-grep` was absent, and did not create the provided root.
- Generated-output path: `route-matrix.md` routes generator-owned files to owning project commands followed by diff inspection.

## Review Inputs

- `edit-orchestration` validator: pass.
- `apply-patch` validator: pass.
- `plan.md` dry-run through `codex2codex/scripts/run_plan.py --dry-run`: pass compile.
- Tool list smoke: pass.
