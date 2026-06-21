# Failure Recovery

Use this when an edit route fails, verification fails, or source context becomes suspect.

## Patch Miss

1. Stop reusing the failed hunk.
2. Re-read the exact source region:

```bash
sed -n '120,150p' file
sed -n '120,150l' file
nl -ba file | sed -n '120,150p'
```

3. Compare intended old text with current source.
4. Shrink the patch to the smallest unique change.
5. Retry once.
6. If it misses again, switch route or stop with the missing evidence.

## Partial Patch

1. Re-read every touched file from disk.
2. Inspect diff.
3. Decide whether the partial change is valid.
4. Continue only with fresh anchors.
5. Do not apply a broad cleanup patch to hide the partial state.

## Tool Self-Check Failure

1. Capture tool id, root, command attempted, and exit status.
2. If the route selected that tool, run `prepare_edit_tools.py --tool <tool>`.
3. Re-run `self_check_edit_tools.py --tool <tool>`.
4. If it still fails, stop. Do not downgrade to manual editing unless the user explicitly changes the route or scope.

## Diff Drift

Stop when diff contains:

- unrelated files
- generated churn outside expected outputs
- lockfile changes without dependency intent
- formatting-only changes mixed with behavior changes
- secrets, credentials, keys, or private data

Recovery:

- Preserve unrelated user work.
- Re-scope the edit.
- Re-run the intended route on only the safe files.

## Verification Failure

1. Read the failure output slice, not the whole log.
2. Load one dependency ring: direct caller/callee, config, test, fixture, or generated file.
3. Write rework guidance before fixing if executing under a plan.
4. Run the failing check again after the smallest safe fix.

Stop when the same failure persists after the allowed rework cycles or the next diagnostic would be speculative.
