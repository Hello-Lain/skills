TASK:
- Plan path: `.codex/work/20260621-skill-production-gate/plan.md`
- Current task: Task 1
- Phase: implement
- Context state: focused
- Risk level: High

AUTHORITATIVE SOURCES:
- User goal: production-grade skill gate; reviewer subagent health policy polls `2 x 45s` only after abnormal signals; healthy running subagents continue; no automatic inline downgrade.
- Plan sections: Task 1, Validation Plan, Abort Criteria.
- Files/tests/configs: `skill-tokenless/SKILL.md`, `skill-tokenless/references/testing.md`, `skill-tokenless/references/validation.md`, `.system/skill-creator/SKILL.md`, `.system/skill-creator/scripts/quick_validate.py`.
- Existing pattern: `reviewer/scripts/validate_review_report.py` self-test style; `debug-skill` reuse matrix discipline.

CONSTRAINTS:
- Must: use `apply_patch`; preserve unrelated dirty work; keep long schema in references.
- Must not: add mandatory third-party deps; rewrite unrelated skills.

UNKNOWN / CONFLICT:
- None.
