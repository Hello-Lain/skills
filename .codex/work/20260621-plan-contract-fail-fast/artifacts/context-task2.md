# Context Task 2

TASK:
- Plan path: `/data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md`
- Current task: Task 2, add `spec2plan` semantic validation.
- Phase: implement
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: bad plans fail early, valid plans still pass.
- Plan sections: Task 2, Validation Plan, Rollback / Recovery Plan.
- Files/tests/configs: `spec2plan/scripts/validate_plan_contract.py`; bad and valid fixture plans.
- Existing pattern: `task_errors()` aggregates task-level errors.

CONSTRAINTS:
- Must: preserve existing validator behavior.
- Must not: add dependencies or rewrite plan format.

UNKNOWN / CONFLICT:
- None.
