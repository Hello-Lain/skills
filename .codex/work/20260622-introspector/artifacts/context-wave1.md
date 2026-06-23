TASK:
- Plan path: `/data/lcq/.codex/skills/.codex/work/20260622-introspector/plan.md`
- Current task: `Task 1` through `Task 4`
- Phase: implement
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: land `Introspector` as a real skill via `spec2plan`, `plan2do`, and `reviewer`.
- Plan sections: `Implementation Map`, `Task Breakdown`, `Validation Plan`, `Execution Handoff`.
- Files/tests/configs: `.codex/work/20260622-introspector/spec.md`, `.codex/work/20260622-introspector/plan.md`, `.system/skill-creator/scripts/init_skill.py`, `.system/skill-creator/scripts/quick_validate.py`, `skill-tokenless/references/skill-production-gate.md`.
- Existing pattern: `interview-me/` uses compact `SKILL.md` plus progressive-disclosure `references/`.

CONSTRAINTS:
- Must: keep edits inside `introspector/` and `.codex/work/20260622-introspector/`.
- Must not: add runtime services, verdict memory, or unrelated repo refactors.

UNKNOWN / CONFLICT:
- Smallest useful calibration-harness representation is not yet proven; keep it document-level in v1.
