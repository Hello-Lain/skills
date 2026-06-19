# Task 3: Update Skill UI Metadata

Status: completed by worker `coding-1`; artifact recorded by lead because the worker approval layer could not create `.codex` artifacts.

## Changed Files

- `deprecation-and-migration/agents/openai.yaml`

## Summary

- Updated `short_description` to mention doc lifecycle cleanup.
- Kept `default_prompt` concise and referenced `$deprecation-and-migration`.
- Preserved implicit invocation policy.

## Verification

- `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/deprecation-and-migration` passed in worker context.
- `rg -n "doc|documentation|cleanup|deprecation|migration" /data/lcq/.codex/skills/deprecation-and-migration/agents/openai.yaml` matched required metadata terms in worker context.

## Risks

- UI display name remains unchanged; acceptable because the short description and default prompt carry the expanded scope.
