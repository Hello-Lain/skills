TASK:
- Plan path: /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/plan.md
- Current task: Task 5, review and final acceptance.
- Phase: review
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: execute the spec2plan plan with plan2do itself and inspect skill/process issues.
- Plan sections: Task 5, Validation Plan, Final Acceptance, Execution Handoff.
- Files/tests/configs: /data/lcq/.codex/skills/plan2do/SKILL.md; /data/lcq/.codex/skills/plan2do/references/execution-contract.md; /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py; /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py; /data/lcq/.codex/skills/plan2do/references/failure-policy.md; /data/lcq/.codex/skills/plan2do/references/review-rubric.md; /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/execution/tasks.json
- Existing pattern: review artifact must contain `Verdict: PASS` or `Verdict: FAIL`; final report must contain `Status: COMPLETE`.

CONSTRAINTS:
- Must: rehydrate current files before acceptance; require validator pass; cite artifacts instead of raw logs.
- Must not: report complete if validation/review fails or if unrelated dirty files are touched.

UNKNOWN / CONFLICT:
- None.
