# Task 2: Add Documentation Cleanup Workflow

Status: completed by worker `coding-2`; artifact recorded by lead because the worker approval layer could not create `.codex` artifacts.

## Changed Files

- `deprecation-and-migration/references/upstream.md`

## Summary

- Added `Documentation Lifecycle Cleanup`.
- Added classifications: authoritative, working, historical, stale, duplicate, temporary, redundant.
- Added actions: keep, merge, summarize, archive, delete.
- Added cleanup workflow and delete gates.
- Added agent process/result doc handling.
- Added doc-cleanup red flags and verification checklist.

## Verification

- `rg -n "Documentation Lifecycle|authoritative|temporary|duplicate|delete gates|merge|archive" /data/lcq/.codex/skills/deprecation-and-migration/references/upstream.md` passed in worker context.
- Worker reported scoped diff as one file changed with 62 insertions.

## Risks

- Delete gates must remain explicit so agents do not remove authoritative or historical records too aggressively.
