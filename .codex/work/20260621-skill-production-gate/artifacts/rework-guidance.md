# Rework Guidance

- Evidence: `.codex/work/20260621-skill-production-gate/review.md` returned `BLOCK`.
- Defect: Final acceptance evidence was missing: production report, task 5 artifacts, final report, and completed execution state.
- Impact: The plan could not prove Skill Production Gate completion or plan2do final acceptance.
- Required change: Add the missing final artifacts, validate the production report, update execution state only after evidence exists, rerun reviewer recheck, and rerun execution validation.
- Writable scope: `.codex/work/20260621-skill-production-gate/artifacts/production-report.md`, `.codex/work/20260621-skill-production-gate/artifacts/task5-execution.md`, `.codex/work/20260621-skill-production-gate/artifacts/task5-verification.md`, `.codex/work/20260621-skill-production-gate/artifacts/final-report.md`, `.codex/work/20260621-skill-production-gate/execution/tasks.json`, `.codex/work/20260621-skill-production-gate/review.md`.
- Verification: Production report validator, reviewer report validator, execution validator.
- Cycle: 1
