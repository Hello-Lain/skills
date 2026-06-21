# Context Pack: Task 1

TASK:
- Plan path: `/data/lcq/.codex/skills/.codex/work/20260621-context-engineering-gate/plan.md`
- Current task: Task 1, split context policy into slim entrypoint and references.
- Phase: implement
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: implement confirmed Context Engineering Gate spec via spec2plan then plan2do.
- Plan sections: Goal, Task 1, Validation Plan, Rollback / Recovery Plan.
- Files/tests/configs: `context-engineering/SKILL.md`, `spec.md`, `plan.md`, current git status.
- Existing pattern: Codex skill progressive disclosure with `SKILL.md`, `references/`, `scripts/`.

CONSTRAINTS:
- Must keep `SKILL.md` below 10,000 characters.
- Must preserve lite/full/escalate, Source Hierarchy, Starvation Guard, Decision Packet, Capsule, compaction safety, anti-pollution, conflict handling.
- Must keep edits inside `context-engineering/` and the topic workspace.
- Must use apply_patch for manual edits.

UNKNOWN / CONFLICT:
- None for Task 1.
