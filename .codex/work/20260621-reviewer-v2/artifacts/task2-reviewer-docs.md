# Task 2 Reviewer Docs

- Status: complete
- Files changed:
  - `reviewer/SKILL.md`
  - `reviewer/references/review-report-template.md`
  - `reviewer/references/subagent-dispatch.md`
- Result: added reviewer v2 route preflight, lite/heavy/blocked semantics, mandatory isolation, report validation, source-path evidence checks, and subagent cleanup guidance.
- Verification:
  - `python3 reviewer/scripts/validate_review_report.py --self-test` -> `VALID`
  - `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer` -> `Skill is valid!`
  - `grep -R "Alignment Verdict\|Quality Verdict" -n reviewer/SKILL.md reviewer/references/review-report-template.md reviewer/references/subagent-dispatch.md || true` -> no matches.
  - `grep -R "TODO\|\[TODO" -n reviewer/SKILL.md reviewer/references reviewer/scripts || true` -> no matches.
- Post-forward-test hardening: added reviewer subagent wait-budget, cancel, archive/kill, and fallback guidance after one heavy recheck exceeded the useful wait budget.
