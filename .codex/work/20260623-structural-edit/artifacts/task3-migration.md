# Task 3 — Write skill contracts and migrate edit-orchestration

- Status: COMPLETE
- Scope: `structural-edit/`, `edit-orchestration/`
- Changed: `structural-edit/SKILL.md`, `structural-edit/agents/openai.yaml`, `structural-edit/references/route-matrix.md`, `structural-edit/references/tooling.md`, `structural-edit/references/fallback-policy.md`, `structural-edit/references/migration.md`, `structural-edit/references/compatibility.md`, `structural-edit/references/validation-scenarios.md`, `edit-orchestration/SKILL.md`, `edit-orchestration/agents/openai.yaml`, `edit-orchestration/references/route-matrix.md`, `edit-orchestration/references/tooling.md`
- Verification:
  - `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/structural-edit` → PASS
  - `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration` → PASS
- Notes:
  - `structural-edit` is now the authoritative default manual-edit skill.
  - `edit-orchestration` is reduced to a compatibility shell that delegates immediately to `structural-edit`.
  - Patch-first authority was removed from compatibility docs; strict fallback remains documented only as a constrained downstream path.

