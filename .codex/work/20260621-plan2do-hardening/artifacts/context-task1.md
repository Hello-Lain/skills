TASK:
- Plan path: /data/lcq/.codex/skills/.codex/work/20260621-plan2do-hardening/plan.md
- Current task: Task 1, add execution compiler and validator.
- Phase: implement
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: generate a spec2plan plan, then execute it with plan2do itself.
- Plan sections: Task 1, Validation Plan, Execution Handoff.
- Files/tests/configs: /data/lcq/.codex/skills/plan2do/SKILL.md; /data/lcq/.codex/skills/plan2do/references/execution-contract.md; /data/lcq/.codex/skills/codex2codex/scripts/plan_to_tasks.py; /data/lcq/.codex/skills/codex2codex/scripts/validate_execution_complete.py
- Existing pattern: stdlib CLI scripts that parse Markdown/JSON, print actionable errors, and return nonzero on validation failure.

CONSTRAINTS:
- Must: stdlib-only scripts; fail closed on missing files or malformed execution artifacts; write output under the plan workspace.
- Must not: modify codex2codex; change default plan2do mode; touch unrelated dirty files.

UNKNOWN / CONFLICT:
- None.
