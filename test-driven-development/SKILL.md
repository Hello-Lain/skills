---
name: test-driven-development
description: Drives development with tests. Use when implementing logic, fixing bugs, changing behavior, adding regressions, or proving acceptance criteria.
---

# TDD workflow

MIT-derived workflow from addyosmani/agent-skills. Keep this entrypoint lean; preserve upstream detail in `references/upstream.md`.

## Use
Read `references/upstream.md` for test pyramid, red/green/refactor, browser testing, and anti-patterns.

## Core Rules
- Write/identify failing test first when feasible.
- Make the smallest change to pass; refactor after green.
- Keep tests behavior-focused, deterministic, and maintainable.

## Validation
- Run relevant repo tests/lint/build or targeted runtime checks.
- If verification cannot run, state why and give the strongest evidence collected.
