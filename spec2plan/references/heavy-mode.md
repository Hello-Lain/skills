# Heavy Mode

Use heavy mode by launching `$codex2codex` in an upstream task subagent. That subagent coordinates meight workers to create, attack, and synthesize a production-grade plan while the primary agent receives only compact artifacts and status.

## Required Dependency

Heavy mode must use `$codex2codex` from `/data/lcq/.codex/skills/codex2codex`.

`spec2plan` owns the plan contract, required phase artifacts, artifact envelope, validators, and final `plan.md`. `$codex2codex` owns adaptive worker topology, fresh `MEIGHT_HOME`, supervised `start`/`wait`, `status`, `steer`, `reply`, `result`, `QUESTION:` handling, worker cleanup, and compact handoff back to the upstream task subagent.

## Worker Phases

- `planner`: inspect evidence and return a complete draft plan.
- `reviewer`: find missing assumptions, weak validation, rollback gaps, blast radius, data/security risks, ownership gaps, scenario gaps, doc/code contradictions, and repo-unanswerable questions.
- `synthesizer`: merge planner output and reviewer findings into the final plan artifact.

Workers must be read-only and must not write repo files. The upstream task subagent saves and validates plan artifacts, then returns only compact paths/status to the primary agent.

## Meight Supervision

- Use `$codex2codex` as an adaptive shell; planner/reviewer/synthesizer are required phases, but consult/arbiter workers are allowed when useful.
- Before planner/reviewer/synthesizer fan-out, require `$codex2codex` to run a nonce smoke worker. If the nonce is not echoed exactly, stop with `Subagent unavailable`.
- Use `start` + checkpoint `wait` via `$codex2codex`; do not use fire-and-forget for substantive phases.
- On wait exit `1`, read compact `status`; wait again if healthy, `steer` if drifting, `interrupt` only if unsafe.
- Treat `updated_age_sec` / `activity_age_sec` over the phase budget as a stall even if `stalled: false`; interrupt or restart once instead of waiting indefinitely.
- On exit `3`, answer or discuss through `reply` in the same thread. Treat `QUESTION:` as valuable pushback, not only blockage.
- If the upstream task subagent is unsure about a planning assumption, launch a read-only consult worker through `$codex2codex` before locking the direction.
- Use at most one targeted `reply`/`follow` per phase after validator failure; then fail closed.
- Copy only the exact `SPEC2PLAN_ARTIFACT_V1` envelope into `<plan-dir>/subagents/<phase>.md`; do not append `$codex2codex` Handoff Capsule text to this artifact.

## Task Packet

Send `$codex2codex` one compact upstream packet; let it derive worker briefs:

- Objective and user request.
- Spec path/text summary, compact evidence summary, and output language.
- Repo root, git status summary, constraints, likely files/docs.
- Evidence paths inspected by the upstream task subagent.
- For small specs, embed the relevant facts directly; do not make workers depend on `rtk` commands or large file reads.
- Output path and mode.
- Redaction rules.
- Required contract: `references/plan-contract.md`.
- Required executable task fields: `Worker role`, `Wave`, `Writable scope`, `Verification`, `Dependencies`, and `Output artifact`.
- Required validator commands.
- Artifact path: `<plan-dir>/subagents/<phase>.md`.
- Instruction: do not implement, do not mutate repo, return artifact envelope only.

Do not include raw secrets, large logs, full diffs, or unrelated transcripts.

## Artifact Envelope

Every worker response must use exactly this outer shape. The end marker must be the final non-whitespace line.

```text
SPEC2PLAN_ARTIFACT_V1
phase: planner|reviewer|synthesizer
status: complete|needs_revision|unsafe
artifact:
<role-specific text only>
SPEC2PLAN_ARTIFACT_END
```

Continue only when `phase` matches the requested phase, `status: complete`, `artifact:` is substantive, and `scripts/validate_subagent_artifact.py` passes.

Treat `needs_revision`, `unsafe`, missing markers, trailing text after the end marker, progress-only output, or session interruption as blocking for that phase.

## Reviewer Required Content

Reviewer artifacts must include:

- `Scenario Probes`
- `Code/doc contradictions`
- `Repo-unanswerable user questions`

Use `None found` only after inspecting available code/docs.

## Failure Policy

- If `$codex2codex` reports meight unavailable, daemon dead, or worker creation failure, stop before writing/updating `plan.md` and report `Subagent unavailable`.
- If a worker returns `QUESTION:`, answer through `$codex2codex reply` or promote the question to `User Inputs Needed` only if repo-unanswerable.
- If an artifact is invalid, send one targeted `reply`/`follow` with the validator error and request a full replacement artifact.
- If retry fails, stop before writing/updating `plan.md` and report `Needs revision` or `Unsafe`.
- Never degrade heavy mode to main-agent-only synthesis.
- Save validated artifacts under `<plan-dir>/subagents/planner.md`, `reviewer.md`, and `synthesizer.md`.
- `plan.md` must match the synthesizer artifact body exactly.
- Before accepting a synthesizer plan, ensure it can be compiled by `$codex2codex scripts/plan_to_tasks.py` without missing writable scopes or unresolved worker roles.
- If execution is expected next, create/check artifact parent directories and run `$codex2codex scripts/run_plan.py <plan.md> --dry-run`; fix the plan before handoff if dry-run fails.
