TASK:
- Plan path: /data/lcq/.codex/skills/.codex/work/20260621-plan2do/plan.md
- Current task: Task 4 validation, then Task 5 review
- Phase: verify | review
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: use the emerging plan2do workflow to execute its own implementation plan and inspect workflow issues.
- Plan sections: Task 4, Task 5, Validation Plan, Quality Gates.
- Files/tests/configs: /data/lcq/.codex/skills/plan2do/SKILL.md; /data/lcq/.codex/skills/plan2do/references/execution-contract.md; /data/lcq/.codex/skills/plan2do/agents/openai.yaml; /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py.
- Existing pattern: skill-creator validation, plan2do execution-contract artifacts.

CONSTRAINTS:
- Must: preserve unrelated dirty work; keep raw outputs out of final; write review artifact.
- Must not: use codex2codex unless explicitly requested; report success after failed verification/review.

UNKNOWN / CONFLICT:
- Whether grep command from plan is too case-sensitive; treat command failure as validation feedback.
