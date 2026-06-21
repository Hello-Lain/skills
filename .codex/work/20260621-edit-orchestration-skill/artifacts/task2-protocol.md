# Task 2: Core Workflow And Route References

- Status: complete
- Files changed:
  - `edit-orchestration/SKILL.md`
  - `edit-orchestration/references/route-matrix.md`
  - `edit-orchestration/references/tooling.md`
  - `edit-orchestration/references/failure-recovery.md`
- Key behavior:
  - `edit-orchestration` is the default entrypoint for manual file edits.
  - Small edits use `apply_patch` fast path.
  - Complex routes require helper self-check and explicit stop on selected-route failure.
  - Diff and verification gates are mandatory before final reporting.

## Verification

- `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration` -> `Skill is valid!`
- `wc -l edit-orchestration/SKILL.md edit-orchestration/references/route-matrix.md edit-orchestration/references/tooling.md edit-orchestration/references/failure-recovery.md` showed `SKILL.md` at 80 lines and combined docs at 370 lines.
