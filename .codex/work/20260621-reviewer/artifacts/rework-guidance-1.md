# Rework Guidance

- Evidence: `.codex/work/20260621-reviewer/review.md` returned `Verdict: REVISE`.
- Defect: `reviewer` lacked explicit adversarial mode, review options, and feedback-validity guidance; dry-review acceptance checks were not evidenced.
- Impact: final acceptance could overclaim spec compliance and weaken high-risk artifact review.
- Required change: patch current skill instructions to add these mechanisms; run saved dry reviews or document deferral; rerun validation and review.
- Writable scope: `reviewer/SKILL.md`, `.codex/work/20260621-reviewer/artifacts/*`, `.codex/work/20260621-reviewer/review*.md`, `execution/tasks.json`.
- Verification: `quick_validate.py`, dry-review artifacts, reviewer recheck, `validate_execution.py`.
- Cycle: 1 of 2.
