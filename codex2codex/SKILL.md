---
name: codex2codex
description: "Meight execution backend and plan orchestrator for Codex worker teams. Use for explicit /codex2codex work, plan.md-to-worker decomposition, codex-agent-team/spec2plan waves, isolated Codex workers, file-disjoint implementation, scoped review, PASS/FAIL gates, or consults without polluting primary context. Do not use for ordinary single-agent tasks."
---

# Codex2Codex

Use `plan.md` as the high-level intent input when available. Compile it to `.codex/specs/<slug>/tasks.md`/manifest first, then run workers. `tasks.md` remains the execution IR: waves, file-disjoint scopes, scoped briefs, PASS/FAIL review, lead consolidation.

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
- One-command preview/run: use `scripts/run_plan.py <plan.md> --dry-run` to inspect generated workers without mutating the real spec dir; drop `--dry-run` to compile and run waves sequentially.
- Wave input: use `scripts/prepare_wave.py --spec-dir <dir> --wave "<wave>"` to generate briefs/manifest and reject overlapping write scopes.

## Modes

- `consult`: read-only expert check.
- `implement`: file-disjoint coding/devops wave.
- `review`: read product scope, write only `review*.md`, verdict `PASS` or `FAIL`.
- `fix`: fix FAIL findings -> rerun affected review only.

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
If an artifact write is blocked, workers must put the full artifact body in final output so `run_wave.py` can salvage it.

## Meight Loop

- Resolve `meight`: PATH -> `codex2codex/.venv/bin/python meight.py` -> `python3 meight.py`.
- `RUN_HOME=$(mktemp -d "${TMPDIR:-/tmp}/meight-${PWD##*/}-XXXXXX")`; prefix every command with `MEIGHT_HOME="$RUN_HOME"`.
- Use `--cwd` for repo/worktree. Use `start` + checkpoint `wait`; `dispatch` only for tiny consults.
- Exit `1`: read `status`; wait if healthy, `steer` if drifting, interrupt/restart once if stale.
- Exit `3`: answer `QUESTION:` with `reply`, or return repo-unanswerable questions upstream.
- Read `result`; accept only if artifact/review contract passes. Exit `0` alone is not success.
- End every wave/consult immediately after reading required results: `MEIGHT_HOME="$RUN_HOME" meight shutdown || MEIGHT_HOME="$RUN_HOME" meight shutdown --force || true`; remove `$RUN_HOME` unless debugging/resume requested.
- Do not leave completed/blocked sidecar agents alive for later convenience. Releasing workers is mandatory to avoid hitting the Codex subagent cap in later waves.

## Gates

- Any material bug/security/regression/interface mismatch/missing verification => review `FAIL`.
- Any scoped `FAIL` => wave fails; `run_wave.py` creates the next fix wave unless `--no-fix-wave`; add `--auto-run-fix` to run fix wave(s) and rerun the original review, bounded by `--max-fix-cycles`.
- Missing expected artifact or blocked terminal result => wave fails even if `meight wait` returned `0`.
- If artifact write tooling is blocked but the worker final output contains a complete artifact body, `run_wave.py` may salvage implementation and review artifacts into the requested path and continue validation.
- When a worker is continued after `QUESTION:`, validate only the final turn for unresolved blockers; earlier resolved blocker text must not fail the wave by itself.
- Never stream raw events/logs/transcripts into lead context.
- Keep secrets/credentials/raw logs/private data out of artifacts and final summaries.
- Git, user comms, irreversible decisions, and final acceptance stay with lead.

## Validate / Return

Prefer upstream validators. Otherwise check:

- implementation result: changed files + verification + risks;
- review result: scope + findings + tests/verification + `Verdict: PASS|FAIL`;
- decisions captured in `decisions.md`;
- no raw transcript/secret leak.

Use `scripts/run_plan.py <plan.md> --dry-run` when starting from a plan; it compiles `### Task N` sections into waves and appends a review wave unless `--no-add-review`. Use `scripts/run_wave.py --spec-dir <dir> --wave "<wave>"` for existing tasks. `run_wave.py` prepares minimal-profile briefs, starts workers, waits, runs `validate_wave.py`, updates `tasks.md` and enriched `review-summary.md` on success, creates a fix wave on review `FAIL`, shuts down `meight`, and returns nonzero on worker failure, blocked result, missing artifact, or review `FAIL`. Use `--auto-run-fix` for FAIL -> fix -> rerun review loops, `--dry-run` to preview workers, and `--profile full` only when minimal context is insufficient. For manual runs, use `--manifest`, `validate_result_contract.py`, and `validate_wave.py` directly.

Return only: mode/wave, workers, artifacts, verdicts, verification, decisions/blockers, cleanup status, raw data omitted.
