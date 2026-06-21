# Task 5: `apply-patch` Coexistence

- Status: complete
- Files changed:
  - `apply-patch/SKILL.md`
  - `apply-patch/agents/openai.yaml`
- Change:
  - `apply-patch` is now described as a low-level patch grammar and recovery support skill.
  - `edit-orchestration` is the route-selection and manual-edit orchestration entrypoint.

## Verification

- `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/apply-patch` -> `Skill is valid!`
- `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration` -> `Skill is valid!`

## Trigger Review

- General manual edit request should route to `edit-orchestration`.
- Patch grammar, malformed hunk, or visual-match miss support should still route to `apply-patch`.
