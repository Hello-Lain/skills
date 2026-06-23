# Migration from edit-orchestration

`structural-edit` is now the authoritative manual-edit entrypoint.

## Outcome

- `structural-edit/` owns the default route contract.
- `edit-orchestration/` has been deleted.
- Patch-first language is removed from `edit-orchestration` authority docs.

## Compatibility Shell Rules

- Old `edit-orchestration` invocations should delegate to `structural-edit`.
- If `structural-edit` is missing or unusable, stop and repair the default skill instead of pretending the old patch-first route is still valid.
- Existing helper scripts inside `edit-orchestration` are historical implementation references, not the default policy source.

## Rollback

- Restore `edit-orchestration/SKILL.md`, `agents/openai.yaml`, and redirected references from the current diff if the compatibility shell misroutes requests.
- Keep `structural-edit/` installed but non-authoritative until the fix is validated.
