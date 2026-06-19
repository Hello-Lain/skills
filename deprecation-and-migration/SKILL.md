---
name: deprecation-and-migration
description: Manages deprecation, migration, and documentation lifecycle cleanup. Use when removing old systems, renaming APIs, changing data models, replacing dependencies, moving users, retiring behavior safely, or cleaning up stale, duplicate, temporary, redundant, process, result, or agent-generated documentation while preserving authoritative records.
---

# Safe migration

MIT-derived workflow from addyosmani/agent-skills. Keep this entrypoint lean; preserve upstream detail in `references/upstream.md`.

## Use
Read `references/upstream.md` for staged migration plans, comms, and rollback templates.

## Core Rules
- Inventory consumers and compatibility constraints.
- Use expand/contract, feature flags, dual-write/read, or adapters when risk warrants.
- Classify docs before changing them: authoritative, working, historical, stale, duplicate, temporary, or redundant.
- Merge unique decisions, verification, and user-facing guidance into the authoritative location before deleting duplicate, temporary, or agent-generated docs.
- Verify references and active consumers before archiving or deleting documentation.
- Define completion metrics, rollback, and cleanup criteria.

## Validation
- Run relevant repo tests/lint/build or targeted runtime checks.
- If verification cannot run, state why and give the strongest evidence collected.
