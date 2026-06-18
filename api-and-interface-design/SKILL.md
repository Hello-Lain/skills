---
name: api-and-interface-design
description: Guides stable API and interface design. Use when designing APIs, module boundaries, public contracts, SDKs, schemas, error semantics, versioning, or integration surfaces.
---

# Design stable interfaces

MIT-derived workflow from addyosmani/agent-skills. Keep this entrypoint lean; preserve upstream detail in `references/upstream.md`.

## Use
Read `references/upstream.md` before changing public contracts or when compatibility/versioning risk exists.

## Core Rules
- Define consumers, invariants, request/response/schema, error semantics, auth, limits, versioning, deprecation.
- Prefer contract tests and backward-compatible evolution.
- Validate boundary inputs; document examples and failure modes.

## Validation
- Run relevant repo tests/lint/build or targeted runtime checks.
- If verification cannot run, state why and give the strongest evidence collected.
