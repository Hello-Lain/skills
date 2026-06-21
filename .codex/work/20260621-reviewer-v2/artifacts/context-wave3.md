# Context Wave 3-5

TASK:
- Plan path: `/data/lcq/.codex/skills/.codex/work/20260621-reviewer-v2/plan.md`
- Current task: Tasks 3-5
- Phase: implement | verify | review | report
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: use `spec2plan` + `plan2do` + `reviewer` to implement reviewer v2.
- Plan sections: Task Breakdown, Validation Plan, Rollback / Recovery Plan, Abort Criteria.
- Files/tests/configs: `reviewer/SKILL.md`, `reviewer/scripts/validate_review_report.py`, `plan2do/scripts/validate_execution.py`, `plan2do/references/execution-contract.md`.
- Existing pattern: plan2do execution artifacts under `.codex/work/20260621-reviewer-v2/artifacts/`.

CONSTRAINTS:
- Must: preserve unrelated work, use `apply_patch` for manual edits, keep `reviewer-lite` internal, avoid changing `plan2do` semantics.
- Must not: commit, delete historical state, globally force upstream skills to call `reviewer`.

UNKNOWN / CONFLICT:
- Task 4 dependencies in `execution/tasks.json` are empty despite plan text requiring Tasks 1-3 first; execution order will still follow plan order.
