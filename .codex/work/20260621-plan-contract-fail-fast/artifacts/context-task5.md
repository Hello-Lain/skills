# Context Task 5

TASK:
- Plan path: `/data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/plan.md`
- Current task: Task 5, review and final acceptance.
- Phase: review
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: land the confirmed spec with `spec2plan` and `plan2do`.
- Plan sections: Task 5, Validation Plan, Review and final acceptance.
- Files/tests/configs: changed validator/compiler scripts; fixture plans; task artifacts; `execution/tasks.json`.
- Existing pattern: `plan2do` review artifact must contain terminal `Verdict: PASS` or `Verdict: FAIL`.

CONSTRAINTS:
- Must: verify bad fixture fails early and valid fixture passes.
- Must not: report success if final execution validator fails.

UNKNOWN / CONFLICT:
- None.
