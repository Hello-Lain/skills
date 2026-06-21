TASK:
- Plan path: `.codex/work/20260621-skill-self-evolution-hardening/plan.md`
- Current task: Tasks 1-4 implementation wave
- Phase: implement
- Context state: full rehydration from spec, plan, skill contracts, target files, and script sources.
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: implement `.codex/work/20260621-skill-self-evolution-hardening/spec.md` using `spec2plan`, `plan2do`, `reviewer`, `debug-skill`, `skill-tokenless`, `context-engineering`, and `edit-orchestration`.
- Plan sections: Goal, Implementation Map, Task Breakdown, Validation Plan, Rollback / Recovery Plan.
- Files/tests/configs: `reviewer/references/subagent-dispatch.md`, `spec2plan/references/plan-contract.md`, `plan2do/references/execution-contract.md`, `skill-tokenless/scripts/validate_skill_production.py`, `debug-skill/SKILL.md`, `debug-skill/references/hermes-reuse.md`, `debug-skill/references/report-template.md`, `debug-skill/scripts/skill_audit_core.py`.
- Existing pattern: Skill Production Gate requires draft report before reviewer, reviewer PASS before final report, and final production report validation.

CONSTRAINTS:
- Must: preserve user dirty work outside writable scopes.
- Must: use `apply_patch` for manual edits.
- Must: keep `debug-skill` recommendation-only without autonomous edits.
- Must not: modify `.codex/work/20260621-reviewer-lite-gate/`.

UNKNOWN / CONFLICT:
- Reviewer path regression has scenario artifact proof because no reviewer dispatch fixture runner exists.
