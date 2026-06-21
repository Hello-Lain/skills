# Context Pack: Task 3

TASK:
- Plan path: `/data/lcq/.codex/skills/.codex/work/20260621-context-engineering-gate/plan.md`
- Current task: Task 3, validate skill package and replay behavior.
- Phase: verify
- Context state: focused
- Risk level: Low

AUTHORITATIVE SOURCES:
- User goal: validated, lean context-engineering skill with deterministic gate.
- Plan sections: Task 3, Validation Plan, Acceptance Checks.
- Files/tests/configs: `context-engineering/SKILL.md`, `context_gate.py`, `references/*.md`.
- Existing pattern: `quick_validate.py` for skill structure and script self-test for behavior.

CONSTRAINTS:
- Must pass quick validation, py_compile, self-test, character count, and replay default check.
- Must not create `agents/openai.yaml` unless validation requires it.

UNKNOWN / CONFLICT:
- None for Task 3.
