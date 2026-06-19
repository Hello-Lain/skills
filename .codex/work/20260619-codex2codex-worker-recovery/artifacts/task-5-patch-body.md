Salvaged-From-Worker: coding-1

## Task 5: Scoped PATCH_BODY Fallback

### Changed Files
- `codex2codex/scripts/run_wave.py`
- `codex2codex/scripts/test_run_wave_recovery.py`

### Implementation
- Fixed PATCH_BODY path normalization:
  - `/dev/null` in unified add/delete patches is ignored as a sentinel.
  - leading `./` is normalized without stripping dotfile components like `.github/...`.
- Preserved existing scoped fallback behavior:
  - implementation workers only; review workers ignored.
  - absolute paths, traversal, backslashes, unsupported patch formats, and out-of-scope paths rejected.
  - patch apply failures classify as `PATCH_CONTEXT` and are sent back through recovery `follow` when budget remains.
  - successful runner-applied patches update worker `status.json` with `files_changed` and `patch_body_fallback`.
- Added focused tests for:
  - unified add patch `/dev/null` handling.
  - dotfile path normalization.
  - absolute/traversal rejection.
  - in-scope apply-patch fallback application and status recording.
  - out-of-scope contract failure.
  - failed patch application flowing back to worker follow prompt.

### Verification
```text
$ python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py codex2codex/scripts/test_run_wave_salvage.py
.........................
----------------------------------------------------------------------
Ran 25 tests in 0.055s

OK
applied PATCH_BODY for coding-1: scoped.txt
```

### Judgment Calls
- Treated `/dev/null` as a non-path sentinel during path extraction, not as a scope candidate.
- Kept scope validation exact-file based, matching current manifest `files` semantics; no directory-prefix expansion added.
- Did not change artifact salvage logic beyond PATCH_BODY interaction; existing report/artifact salvage remains intact.

### Residual Risks
- Runner-side `apply_patch` support depends on the local `apply_patch` command being available; unsupported environments return a patch failure and enter recovery.
- Unified patch application still relies on `git apply`; malformed but path-parseable diffs fail safely as `PATCH_CONTEXT`.
