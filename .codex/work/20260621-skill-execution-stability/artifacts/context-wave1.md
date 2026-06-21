# Context Wave 1

TASK:
- Plan path: `.codex/work/20260621-skill-execution-stability/plan.md`
- Current task: Tasks 1-4
- Phase: implement
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: use spec2plan + plan2do + reviewer to implement skill execution stability gates.
- Plan sections: `Task Breakdown`, `Validation Plan`, `Execution Handoff`.
- Files/tests/configs: `plan2do/scripts/pre_review_ready.py`, `skill-tokenless/scripts/validate_skill_production.py`, `plan2do/references/execution-contract.md`, `skill-tokenless/references/skill-production-gate.md`, `reviewer/references/subagent-dispatch.md`.
- Existing pattern: local stdlib validators with `--self-test`; plan2do execution artifacts under `.codex/work/<topic>/artifacts/`.

CONSTRAINTS:
- Must: use `apply_patch` for file edits; preserve dirty work; run draft readiness before reviewer.
- Must not: cancel/archive healthy reviewer subagents; add mandatory third-party dependencies; skip production gate.

UNKNOWN / CONFLICT:
- None.
