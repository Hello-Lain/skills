# Context Wave 1

TASK:
- Plan path: `/data/lcq/.codex/skills/.codex/work/20260621-reviewer/plan.md`
- Current task: Tasks 2-5, continue implementation after scaffold
- Phase: implement / verify / review / report
- Context state: focused
- Risk level: medium

AUTHORITATIVE SOURCES:
- User goal: implement confirmed `reviewer` spec with `spec2plan` and `plan2do`, then audit with `reviewer`.
- Plan sections: Goal, Task Breakdown, Validation Plan, Rollback / Recovery Plan, Abort Criteria, Execution Handoff.
- Files/tests/configs: `reviewer/SKILL.md`, `reviewer/agents/openai.yaml`, `reviewer/references/*.md`, `execution/tasks.json`.
- Existing pattern: `.system/skill-creator` skill layout and `agents/openai.yaml` constraints.

CONSTRAINTS:
- Must: preserve existing upstream skills; keep `reviewer` review-only by default; use `apply_patch` for manual edits; validate with `quick_validate.py` and `validate_execution.py`.
- Must not: modify `idea-refine`, `interview-me`, `spec2plan`, or `plan2do`; vendor third-party code; commit changes.

UNKNOWN / CONFLICT:
- Subagent availability is runtime-dependent; inline fallback is allowed only with explicit reason.
