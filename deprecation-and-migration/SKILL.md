---
name: deprecation-and-migration
description: Manages deprecation and migration. Use when removing old systems, renaming APIs, changing data models, replacing dependencies, moving users, or retiring behavior safely.
---

# Safe migration

MIT-derived workflow from addyosmani/agent-skills. Keep this entrypoint lean; preserve upstream detail in `references/upstream.md`.

## Use
Read `references/upstream.md` for staged migration plans, comms, and rollback templates.

## Core Rules
- Inventory consumers and compatibility constraints.
- Use expand/contract, feature flags, dual-write/read, or adapters when risk warrants.
- Define completion metrics, rollback, and cleanup criteria.

## Validation
- Run relevant repo tests/lint/build or targeted runtime checks.
- If verification cannot run, state why and give the strongest evidence collected.
