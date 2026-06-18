---
name: debugging-and-error-recovery
description: Guides systematic root-cause debugging. Use when tests fail, builds break, runtime behavior is unexpected, incidents occur, or prior fixes did not hold.
---

# Root-cause debug

MIT-derived workflow from addyosmani/agent-skills. Keep this entrypoint lean; preserve upstream detail in `references/upstream.md`.

## Use
Read `references/upstream.md` for detailed triage patterns and anti-rationalization checks.

## Core Rules
- Reproduce -> localize -> reduce -> fix -> guard.
- Change one variable at a time; record evidence.
- Add regression coverage or monitoring so the same bug is caught next time.

## Validation
- Run relevant repo tests/lint/build or targeted runtime checks.
- If verification cannot run, state why and give the strongest evidence collected.
