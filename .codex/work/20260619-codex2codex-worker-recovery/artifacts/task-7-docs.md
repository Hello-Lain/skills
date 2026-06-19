Salvaged-From-Worker: coding-1

## Task 7: Update worker prompts and documentation

### Changed Files
- `codex2codex/SKILL.md`
- `codex2codex/README.md`
- `codex2codex/ARCHITECTURE.md`
- `codex2codex/scripts/prepare_wave.py`

### Summary
- Documented that lead fallback is prohibited unless explicitly requested.
- Documented recovery outcome categories: `INFRA_FAILED`, `CONTRACT_FAILED`, and `TASK_BLOCKED`.
- Documented retry budget semantics for `--same-worker-restarts`, `--fresh-worker-restarts`, `--preflight-timeout`, and `--no-preflight`.
- Documented review verdict and validator gate requirements, including `Verdict: PASS|FAIL`, missing artifacts, blocked artifacts, and missing expected diffs.
- Documented `PATCH_BODY` fallback rules and aligned generated implementation briefs with stricter behavior.

### Verification
- `rtk grep -n "lead fallback\\|PATCH_BODY\\|INFRA_FAILED\\|CONTRACT_FAILED\\|TASK_BLOCKED" codex2codex/SKILL.md codex2codex/README.md codex2codex/ARCHITECTURE.md codex2codex/scripts/prepare_wave.py`
  - Result: pass, 15 matches across 4 files.
- `rtk python3 codex2codex/scripts/prepare_wave.py --help`
  - Result: pass.
- `rtk python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py`
  - Result: pass, 27 tests.
- `rtk python3 codex2codex/scripts/prepare_wave.py --spec-dir .codex/work/20260619-codex2codex-worker-recovery --wave "Wave 6" --out-dir /tmp/task7-wave6 --json`
  - Result: pass, generated `coding-1` brief.
- `rtk grep -n "lead fallback\\|PATCH_BODY" /tmp/task7-wave6/coding-1.txt`
  - Result: pass, generated brief includes updated fallback language.

### Judgment Calls
- Kept implementation behavior unchanged; this task is docs and worker-prompt alignment only.
- Added recovery details in the README quick-start area and architecture recovery section rather than duplicating all runner internals in the skill entrypoint.
- Scoped `PATCH_BODY` language to implementation workers only; review workers still use artifact salvage and verdict gates.

### Residual Risks
- Existing dirty worktree includes unrelated files outside this task scope; not touched.
- Docs now reflect current recovery implementation, but future runner flag or taxonomy changes will need matching docs updates.
