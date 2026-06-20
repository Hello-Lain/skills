# Compact Synthesis Packet

## Objective
Produce a heavy-mode executable `plan.md` for implementing a safer `codex2codex` recovery and planning flow after observed `turn/started` -> no event/no token stalls.

## Required Direction
- Add explicit `PRE_FIRST_ITEM_STALL` classification for workers that reached `turn/started` but have no `item/started`, no token usage, no current item, and stale activity.
- Treat this as infrastructure/app-server stream failure, not task quality failure.
- Recovery should rotate daemon/app-server with a fresh `MEIGHT_HOME`, run a nonce smoke worker, then retry once.
- Update `spec2plan` heavy-mode guidance so synthesizer input is compact:
  - Use validated planner/reviewer artifacts.
  - Prefer `reviewer -> planner follow finalizer` or compact synthesis packet before launching a full fresh synthesizer.
  - Still require a validated `SPEC2PLAN_ARTIFACT_V1` final artifact; no main-agent fallback plan synthesis.
- Preserve quality gates: review PASS/FAIL, artifact validators, dry-run not a quality gate, final validation after real execution.

## Evidence
- `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/idea.md`
- `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/subagents/planner.md` validated with `validate_subagent_artifact.py planner`
- `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/subagents/reviewer.md` validated with `validate_subagent_artifact.py reviewer`
- `/tmp/meight-codex2codex-context-firewall/workers/spec2plan-synthesizer/events.log`: only `turn/started`, then interrupt
- `/tmp/meight-codex2codex-context-firewall/workers/spec2plan-synthesizer-2/events.log`: only `turn/started`, then interrupt
- `codex2codex/meight.py`: `Worker._handle_event()` sets state to running on `turn/started`; `wait_for_worker()` treats stale running as generic stall.
- `codex2codex/scripts/run_wave.py`: recovery has categories, but not `PRE_FIRST_ITEM_STALL`.
- `spec2plan/references/heavy-mode.md`: requires planner/reviewer/synthesizer but lacks compact synthesis fallback.

## Reviewer Blocking Fixes to Include
- Define exact detection and recovery contract; do not leave validator/recovery integration vague.
- Add regression tests for pre-first-item stall classification and recovery decision.
- Do not let dry-run count as quality gate.
- Do not allow main-agent fallback synthesis.
- Preserve worker cleanup and no raw transcript leakage.
- Keep blackboard/context-firewall larger work out of this focused recovery plan unless explicitly deferred.

## Required Plan Shape
Use `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`.

Output must be Chinese and include all required sections. Include:
- `Mode: heavy`
- `Risk level: High`
- `Confidence: High`
- `ADR: Needed`
- exact task fields for every `### Task N`
- task output artifacts under `.codex/work/20260620-codex2codex-context-firewall/artifacts/`
- final independent review task writing `.codex/work/20260620-codex2codex-context-firewall/review.md`

## Likely Files
- `codex2codex/meight.py`
- `codex2codex/scripts/run_wave.py`
- `codex2codex/scripts/test_worker_recovery_contracts.py`
- `codex2codex/scripts/test_run_wave_recovery.py`
- `codex2codex/SKILL.md`
- `codex2codex/ARCHITECTURE.md`
- `spec2plan/references/heavy-mode.md`

## Return Envelope
SPEC2PLAN_ARTIFACT_V1
phase: synthesizer
status: complete
artifact:
<complete final plan markdown only>
SPEC2PLAN_ARTIFACT_END
