TASK:
- Plan path: `.codex/work/20260621-reviewer-lite-gate/plan.md`
- Current task: Tasks 1-5
- Phase: implement
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: make `reviewer` a decoupled light review gate for `idea-refine`, `interview-me`, `spec2plan`, `plan2do`, and future skills.
- Plan sections: `Goal`, `Task Breakdown`, `Validation Plan`, `Rollback / Recovery Plan`, `Execution Handoff`.
- Files/tests/configs: `reviewer/SKILL.md`, `reviewer/references/lite-gate-integration.md`, `idea-refine/SKILL.md`, `interview-me/SKILL.md`, `spec2plan/SKILL.md`, `plan2do/SKILL.md`.
- Existing pattern: `reviewer` owns verdicts; consumer skills preserve domain hard gates.

CONSTRAINTS:
- Must: centralize review semantics in `reviewer`.
- Must: preserve validators, user confirmation, and execution evidence.
- Must not: copy full reviewer rubrics into consumers.
- Must not: replace hard gates with lite review.

UNKNOWN / CONFLICT:
- Reviewer default recheck loop is two unresolved cycles; the new integration guide scopes the user-requested three-cycle cap to consumer-owned lite gates only.
