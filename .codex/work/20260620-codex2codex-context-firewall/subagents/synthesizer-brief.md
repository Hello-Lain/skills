Use role: consult
Instance: spec2plan-synthesizer
Mode: read-only synthesis worker
Objective: Merge planner + reviewer artifacts into the final heavy-mode executable `plan.md` for `codex2codex` context firewall refactor.

Inputs:
- Direction: `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/idea.md`
- Planner artifact: `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/subagents/planner.md`
- Reviewer artifact: `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/subagents/reviewer.md`
- Plan contract: `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- Heavy mode contract: `/data/lcq/.codex/skills/spec2plan/references/heavy-mode.md`

Synthesis rules:
- Output language: Chinese.
- Final artifact body must be the complete `plan.md`.
- Do not implement. Do not mutate repo.
- Preserve reviewer blocking fixes unless clearly invalid.
- Include all required plan sections.
- Include `Mode: heavy`, risk, confidence.
- Use exact task fields required by plan contract.
- Ensure same-wave implementation tasks do not overlap writable scopes.
- Ensure `Output artifact` paths are under `.codex/work/20260620-codex2codex-context-firewall/artifacts/` or review artifacts in `.codex/work/20260620-codex2codex-context-firewall/`.
- Include final review task.
- Explicitly state assumptions caused by skipping `interview-me`.

Return exactly:
SPEC2PLAN_ARTIFACT_V1
phase: synthesizer
status: complete
artifact:
<final plan markdown only>
SPEC2PLAN_ARTIFACT_END
