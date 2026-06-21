# Context Task 3

TASK:
- Plan path: `/data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md`
- Current task: Task 3, add `plan2do` compile-time fail-fast.
- Phase: implement
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: bad plans fail before final acceptance.
- Plan sections: Task 3, Validation Plan, Rollback / Recovery Plan.
- Files/tests/configs: `plan2do/scripts/compile_execution.py`; fixture plans.
- Existing pattern: `compile_plan()` accumulates task errors before writing `execution/tasks.json`.

CONSTRAINTS:
- Must: fail before writing output for invalid review artifact plans.
- Must not: add dependencies or alter task JSON schema.

UNKNOWN / CONFLICT:
- None.
