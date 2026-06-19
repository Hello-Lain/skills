# Task 1: Expand Skill Entrypoint

Status: completed by worker `coding-1`; artifact recorded by lead because the worker approval layer could not create `.codex` artifacts.

## Changed Files

- `deprecation-and-migration/SKILL.md`

## Summary

- Expanded the skill description so `deprecation-and-migration` triggers for documentation lifecycle cleanup.
- Added stale, duplicate, temporary, redundant, process, result, and agent-generated documentation to the trigger scope.
- Added core rules for classifying docs, merging unique content before deletion, and verifying references before archiving or deleting docs.
- Preserved existing migration/deprecation rules.

## Verification

- `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/deprecation-and-migration` passed in worker context.
- `rg -n "documentation|stale|duplicate|temporary|authoritative|merge" /data/lcq/.codex/skills/deprecation-and-migration/SKILL.md` matched required terms in worker context.

## Risks

- Trigger may be broad; review should confirm it does not fire on ordinary doc edits without cleanup intent.
