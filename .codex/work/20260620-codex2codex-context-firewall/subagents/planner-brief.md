Use role: consult
Instance: spec2plan-planner
Mode: read-only planning worker
Objective: Draft a heavy-mode executable plan for refactoring `/data/lcq/.codex/skills/codex2codex` into a context firewall execution protocol.

User constraints:
- Target users: all future agents using `codex2codex`.
- Primary metric: reduce lead/main-agent context tokens.
- Non-negotiable: output quality must not degrade.
- Acceptable tradeoff: slower execution, but not excessive.
- Main/subagent division and subagent-to-subagent interaction must be meaningful.

Authoritative direction artifact:
- `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/idea.md`

Evidence inspected by upstream:
- `/data/lcq/.codex/skills/codex2codex/SKILL.md`
- `/data/lcq/.codex/skills/codex2codex/ARCHITECTURE.md`
- `/data/lcq/.codex/skills/codex2codex/scripts/run_plan.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/run_wave.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/plan_to_tasks.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/execution_state.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/validate_execution_complete.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/validate_wave.py`
- `/data/lcq/.codex/skills/codex2codex/roles/*.yaml`
- `/data/lcq/.codex/skills/codex2codex/scripts/test_execution_completion.py`
- `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`

Planning requirements:
- Output language: Chinese.
- Do not implement. Do not mutate repo.
- Use heavy mode.
- Plan output path will be `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/plan.md`.
- Task output artifacts must be under `.codex/work/20260620-codex2codex-context-firewall/artifacts/`.
- Review artifacts must be under `.codex/work/20260620-codex2codex-context-firewall/review*.md`.
- Every task must include Description, Worker role, Wave, Acceptance criteria, Verification, Dependencies, Files likely touched, Writable scope, Output artifact, Estimated scope.
- Same-wave implementation tasks must have non-overlapping writable scopes.
- Include final independent review.
- Include validators/tests: unit tests under `codex2codex/scripts/test_*.py`, plan dry-run, capsule validators, final execution validator.
- Record assumptions because user explicitly requested direct `spec2plan` from a confirmed direction, skipping `interview-me`.

Required plan sections:
`# <title>`, Goal, Non-Goals, Evidence Inspected, Spec Summary, Domain Language Check, Current Context, Assumptions, User Inputs Needed, Proposed Approach, Scenario Probes, Dependency Graph, Task Breakdown, Step-by-Step Plan, Parallelization, Files / Components Likely Affected, Owners / Responsibilities, Validation Plan, Rollout Plan, Monitoring / Observability, Documentation / ADR Updates, Rollback / Recovery Plan, Abort Criteria, Risks, Open Questions, Execution Decision, Execution Handoff.

Return exactly:
SPEC2PLAN_ARTIFACT_V1
phase: planner
status: complete
artifact:
<complete draft plan markdown only>
SPEC2PLAN_ARTIFACT_END
