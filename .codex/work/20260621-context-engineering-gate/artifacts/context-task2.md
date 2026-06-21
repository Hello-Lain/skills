# Context Pack: Task 2

TASK:
- Plan path: `/data/lcq/.codex/skills/.codex/work/20260621-context-engineering-gate/plan.md`
- Current task: Task 2, add deterministic context gate.
- Phase: implement
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: add a no-dependency gate that reduces context artifact overuse without hiding risk.
- Plan sections: Task 2, Validation Plan, Acceptance Checks.
- Files/tests/configs: `context-engineering/SKILL.md`, `references/artifact-policy.md`, `references/replay.md`.
- Existing pattern: stdlib Python CLI scripts in skills.

CONSTRAINTS:
- Must output one of `internal`, `wave-pack`, `task-pack`, `decision-packet`, `capsule`, `compact-request`.
- Must pass `--self-test` and `py_compile`.
- Must not add third-party imports.

UNKNOWN / CONFLICT:
- None for Task 2.
