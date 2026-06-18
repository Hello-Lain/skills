---
name: codex2codex
description: "Meight execution backend for codex-agent-team style collaboration. Use for explicit /codex2codex work or upstream heavy-mode waves that need isolated Codex workers, file-disjoint implementation, scoped review, PASS/FAIL gates, or consults without polluting primary context. Do not use for ordinary single-agent tasks."
---

# Codex2Codex

Runtime only. Use `codex-agent-team` as the team protocol: `.codex/specs/<slug>/` artifacts, `tasks.md` waves, file-disjoint scopes, scoped briefs, PASS/FAIL review, lead consolidation.

## Use / Skip

- Use: bounded wave exists or can be cheaply written in `.codex/specs/<slug>/tasks.md`.
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

`tasks.md` owns wave/task scope. Same-wave write files must not overlap. Each task needs exact paths and a verify command. Record blockers/scope changes in `decisions.md`. Use `scripts/prepare_wave.py --spec-dir <dir> --wave "<wave>"` to generate briefs/manifest and reject overlapping write scopes.

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

## Meight Loop

- Resolve `meight`: PATH -> `codex2codex/.venv/bin/python meight.py` -> `python3 meight.py`.
- `RUN_HOME=$(mktemp -d "${TMPDIR:-/tmp}/meight-${PWD##*/}-XXXXXX")`; prefix every command with `MEIGHT_HOME="$RUN_HOME"`.
- Use `--cwd` for repo/worktree. Use `start` + checkpoint `wait`; `dispatch` only for tiny consults.
- Exit `1`: read `status`; wait if healthy, `steer` if drifting, interrupt/restart once if stale.
- Exit `3`: answer `QUESTION:` with `reply`, or return repo-unanswerable questions upstream.
- Read `result`; accept only if artifact/review contract passes. Exit `0` alone is not success.
- End: `MEIGHT_HOME="$RUN_HOME" meight shutdown || true`; remove `$RUN_HOME` unless debugging/resume requested.

## Gates

- Any material bug/security/regression/interface mismatch/missing verification => review `FAIL`.
- Any scoped `FAIL` => wave fails; `run_wave.py` creates the next fix wave unless `--no-fix-wave`; add `--auto-run-fix` to run fix wave(s) and rerun the original review, bounded by `--max-fix-cycles`.
- Missing expected artifact or blocked terminal result => wave fails even if `meight wait` returned `0`.
- Never stream raw events/logs/transcripts into lead context.
- Keep secrets/credentials/raw logs/private data out of artifacts and final summaries.
- Git, user comms, irreversible decisions, and final acceptance stay with lead.

## Validate / Return

Prefer upstream validators. Otherwise check:

- implementation result: changed files + verification + risks;
- review result: scope + findings + tests/verification + `Verdict: PASS|FAIL`;
- decisions captured in `decisions.md`;
- no raw transcript/secret leak.

Use `scripts/run_wave.py --spec-dir <dir> --wave "<wave>"` for generated waves. It prepares minimal-profile briefs, starts workers, waits, runs `validate_wave.py`, updates `tasks.md` and enriched `review-summary.md` on success, creates a fix wave on review `FAIL`, shuts down `meight`, and returns nonzero on worker failure, blocked result, missing artifact, or review `FAIL`. Use `--auto-run-fix` for FAIL -> fix -> rerun review loops, `--dry-run` to preview workers, and `--profile full` only when minimal context is insufficient. For manual runs, use `--manifest`, `validate_result_contract.py`, and `validate_wave.py` directly.

Return only: mode/wave, workers, artifacts, verdicts, verification, decisions/blockers, cleanup status, raw data omitted.
