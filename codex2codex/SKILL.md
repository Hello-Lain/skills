---
name: codex2codex
description: "Meight execution backend and plan orchestrator for Codex worker teams. Use for explicit /codex2codex work, plan.md-to-worker decomposition, codex2codex/spec2plan waves, isolated Codex workers, file-disjoint implementation, scoped review, PASS/FAIL gates, or consults without polluting primary context. Do not use for ordinary single-agent tasks."
---

# Codex2Codex

Use `plan.md` as the high-level intent input when available. Compile it to `.codex/specs/<slug>/tasks.md`/manifest first, then run workers. `tasks.md` remains the execution IR: waves, file-disjoint scopes, scoped briefs, PASS/FAIL review, lead consolidation. Role definitions, prompts, aliases, caps, effort, sandbox, context profile, and preferred skills live in `roles/*.yaml`; `scripts/roles.py` loads them.

## Use / Skip

- Use: `plan.md` exists, or a bounded wave exists/can be cheaply written in `.codex/specs/<slug>/tasks.md`.
- Skip: trivial task, unclear reqs, overlapping edits without worktrees, or single-agent path is safe.

## Artifacts

Default shared state:

```text
.codex/specs/<slug>/
  spec.md
  design.md          # optional
  tasks.md
  review.md | review-<scope>.md
  review-summary.md
  decisions.md
```

`plan.md` owns user intent; `tasks.md` owns executable worker scope. Same-wave write files must not overlap. Each task needs exact paths, worker role, verify command, and output artifact. Record blockers/scope changes in `decisions.md`.

- Plan input: use `scripts/plan_to_tasks.py <plan.md> --spec-dir <dir> --add-review` to compile tasks/waves; add `--force` only when replacing generated `tasks.md`.
- One-command preview/run: use `scripts/run_plan.py <plan.md> --dry-run` to inspect generated workers without mutating the real spec dir; dry-run is compile-only and never a quality gate. Drop `--dry-run` to compile and run waves sequentially.
- Final acceptance: after non-dry-run execution, use `scripts/validate_execution_complete.py <spec-dir>` to prove execution receipts, worker artifacts, review `Verdict: PASS`, provenance summaries, and shutdown cleanup exist.
- Wave input: use `scripts/prepare_wave.py --spec-dir <dir> --wave "<wave>"` to generate briefs/manifest and reject overlapping write scopes.

## Modes

- `consult`: read-only expert check.
- `implement`: file-disjoint coding/test wave.
- `review`: read product scope, write only `review*.md`, verdict `PASS` or `FAIL`.
- `fix`: fix FAIL findings -> rerun affected review only.

## Roles

- Edit `roles/*.yaml`, not Python, to change a role prompt or config.
- `fullstack-agent`: lead/orchestrator only; defined in `roles/fullstack.yaml` and rejected as a worker.
- Worker roles are `coding`, `test`, `review`, `sa`, and `consult`; each has its own YAML file.
- Effort is limited to `high|xhigh` by `roles/_defaults.yaml`.
- Context profile defaults to `role`: resolve each worker's YAML `context_profile`. Override a whole wave with `--profile minimal|standard|full` only when justified.

`devops-agent` is retired. `devops`, `ops`, `ci`, `deploy`, and `infra` remain compatibility aliases to `coding`; route high-stakes operational decisions to `sa`.

Use councils only for high-stakes decisions with real rollback/security/cost/reliability risk.

## Worker Brief

```text
Use role:
Instance:
Spec:
Wave:
File scope:
Task:
Verify:
Output:
Concurrency:
Restrictions:
```

One worker = one role, one scope, one output artifact. Workers must not edit outside scope, commit, push, talk to user, or invoke `/codex2codex`. Review workers use workspace-write only so they can write review artifacts; their product scope is read-only by instruction. Workers may end with `QUESTION:` for blockers, wrong assumptions, or better paths.
Lead fallback is prohibited unless explicitly requested: the lead must not silently implement worker-scoped changes after worker failure. Use runner recovery, validated `PATCH_BODY`, a fix wave, or fail the wave with an explicit category.
If an artifact write is blocked by approval/tooling/credentials, workers must not ask for approval or end with `QUESTION:`. They must finish with `ARTIFACT_BODY:` followed by the exact Markdown artifact body so `run_wave.py` can salvage only that body into the requested path.
If direct edit tooling fails after scoped implementation work, implementation workers may provide `PATCH_BODY:` as a last-resort fallback. The body must be a complete `apply_patch` patch or unified diff, touch only listed file-scope paths, and produce real changes. `run_wave.py` validates writable scope before applying; out-of-scope paths, unsupported formats, no-change patches, or stale context fail recovery rather than authorizing lead fallback.

## Meight Loop

- Resolve `meight`: PATH -> `codex2codex/.venv/bin/python meight.py` -> `python3 meight.py`.
- `RUN_HOME=$(mktemp -d "${TMPDIR:-/tmp}/meight-${PWD##*/}-XXXXXX")`; prefix every command with `MEIGHT_HOME="$RUN_HOME"`.
- Use `--cwd` for repo/worktree. Use `start` + checkpoint `wait`; `dispatch` only for tiny consults.
- Exit `1`: read `status`; wait if healthy, `steer` if drifting, interrupt/restart once if stale.
- `PRE_FIRST_ITEM_STALL`: worker reached `turn/started` but no item has ever started in that turn, no token usage exists, and no current item appears before stale timeout. Treat as infra/app-server stream failure, not task quality failure.
- For `PRE_FIRST_ITEM_STALL`, runner recovery rotates daemon/app-server into a fresh `MEIGHT_HOME`, runs a nonce smoke worker first, then retries the original worker once. If smoke fails or the retry stalls again, report infra recovery failure; do not loop.
- Exit `3`: answer `QUESTION:` with `reply`, or return repo-unanswerable questions upstream.
- Read `result`; accept only if artifact/review contract passes. Exit `0` alone is not success.
- End every wave/consult immediately after reading required results: `MEIGHT_HOME="$RUN_HOME" meight shutdown || MEIGHT_HOME="$RUN_HOME" meight shutdown --force || true`; remove `$RUN_HOME` unless debugging/resume requested.
- Do not leave completed/blocked sidecar agents alive for later convenience. Releasing workers is mandatory to avoid hitting the Codex subagent cap in later waves.

## Gates

- Any material bug/security/regression/interface mismatch/missing verification => review `FAIL`.
- Any scoped `FAIL` => wave fails; `run_wave.py` creates the next fix wave unless `--no-fix-wave`; add `--auto-run-fix` to run fix wave(s) and rerun the original review, bounded by `--max-fix-cycles`.
- Missing expected artifact, blocked terminal result, missing review `Verdict: PASS|FAIL`, or missing expected implementation diff => wave fails even if `meight wait` returned `0`.
- Dry-run output is not a PASS/FAIL quality gate; it must never be cited as review completion or final acceptance.
- Non-trivial implementation is not complete until `validate_execution_complete.py` passes, including at least one real review `Verdict: PASS` unless review was explicitly waived by the lead.
- If artifact write tooling is blocked but the worker final output contains `ARTIFACT_BODY:` or one complete fenced Markdown artifact, `run_wave.py` may salvage implementation and review artifacts into the requested path and continue validation.
- Recovery categories are explicit: `TRANSIENT_API` and `TOOL_INFRA` exhaust as `INFRA_FAILED`; `PATCH_CONTEXT` and `CONTRACT_FAIL` exhaust as `CONTRACT_FAILED`; real blockers exhaust as `TASK_BLOCKED`.
- When a worker is continued after `QUESTION:`, validate only the final turn for unresolved blockers; earlier resolved blocker text must not fail the wave by itself.
- Never stream raw events/logs/transcripts into lead context.
- Use `meight doctor --json` for routine global-skill availability checks; avoid live worker smoke tests unless debugging worker execution.
- Keep secrets/credentials/raw logs/private data out of artifacts and final summaries. Recovery artifacts may summarize `PRE_FIRST_ITEM_STALL`, nonce smoke status, retry counts, cleanup, and redacted paths only; never include raw transcripts or event streams.
- Git, user comms, irreversible decisions, and final acceptance stay with lead.

## Validate / Return

Prefer upstream validators. Otherwise check:

- implementation result: changed files + verification + risks;
- review result: scope + findings + tests/verification + `Verdict: PASS|FAIL`;
- decisions captured in `decisions.md`;
- no raw transcript/secret leak.

Use `scripts/run_plan.py <plan.md> --dry-run` when starting from a plan; it compiles `### Task N` sections into waves and appends a review wave unless `--no-add-review`, but prints `COMPILE ONLY - NOT A QUALITY GATE`. Use `scripts/run_wave.py --spec-dir <dir> --wave "<wave>"` for existing tasks. `run_wave.py` prepares role-profile briefs by default, preflights worker readiness, starts workers, waits, runs `validate_wave.py`, updates `tasks.md` and enriched `review-summary.md` on success, creates a fix wave on review `FAIL`, shuts down `meight`, writes execution receipts to `execution-state.json`, and returns nonzero on worker failure, blocked result, missing artifact, or review `FAIL`. Use `--same-worker-restarts N` and `--fresh-worker-restarts N` for bounded recovery retries, `--no-preflight` only when intentionally bypassing static readiness checks, `--auto-run-fix` for FAIL -> fix -> rerun review loops, `--dry-run` to preview workers, and `--profile minimal|standard|full` only when overriding role budgets. For manual runs, use `--manifest`, `validate_result_contract.py`, `validate_wave.py`, and `validate_execution_complete.py` directly.

Return only: mode/wave, workers, artifacts, verdicts, verification, decisions/blockers, cleanup status, raw data omitted.
