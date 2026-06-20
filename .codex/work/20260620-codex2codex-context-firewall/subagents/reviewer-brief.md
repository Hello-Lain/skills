Use role: review
Instance: spec2plan-reviewer
Mode: read-only plan review worker
Objective: Review the planner artifact for the `codex2codex` context firewall plan.

Inputs:
- Direction: `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/idea.md`
- Planner artifact will be provided in the brief update or readable at `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/subagents/planner.md` after planner completes.
- Plan contract: `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- Heavy mode contract: `/data/lcq/.codex/skills/spec2plan/references/heavy-mode.md`
- Core evidence:
  - `/data/lcq/.codex/skills/codex2codex/SKILL.md`
  - `/data/lcq/.codex/skills/codex2codex/ARCHITECTURE.md`
  - `/data/lcq/.codex/skills/codex2codex/scripts/run_plan.py`
  - `/data/lcq/.codex/skills/codex2codex/scripts/run_wave.py`
  - `/data/lcq/.codex/skills/codex2codex/scripts/execution_state.py`
  - `/data/lcq/.codex/skills/codex2codex/scripts/validate_execution_complete.py`
  - `/data/lcq/.codex/skills/codex2codex/scripts/validate_wave.py`

Review focus:
- Missing assumptions or user questions hidden as implementation details.
- Weak token-reduction validation.
- Weak quality gate validation.
- Missing rollback/recovery.
- Blast-radius and same-wave writable scope risks.
- Any contradiction with `codex2codex` architecture or existing runner contracts.
- Whether subagent interaction is meaningful instead of ceremony.
- Whether output artifacts are codex2codex-compatible.

Reviewer artifact must include:
- Scenario Probes
- Code/doc contradictions
- Repo-unanswerable user questions
- Blocking issues
- Recommended fixes

Do not implement. Do not mutate repo.

Return exactly:
SPEC2PLAN_ARTIFACT_V1
phase: reviewer
status: complete
artifact:
<review findings only>
SPEC2PLAN_ARTIFACT_END
