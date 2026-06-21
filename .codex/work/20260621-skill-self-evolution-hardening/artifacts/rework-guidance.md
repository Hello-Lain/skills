# Rework Guidance

- Evidence: reviewer subagent returned `REVISE`; `git diff --stat` shows pre-existing dirty `reviewer/SKILL.md`, `spec2plan/SKILL.md`, and `plan2do/SKILL.md` not inventoried in production report.
- Defect: production evidence did not classify those material dirty files as included or excluded.
- Impact: final reviewer could treat the implementation as complete while behavior-affecting skill frontdoor edits remain undisclosed.
- Required change: classify the three `SKILL.md` files as pre-existing excluded dirty work with evidence, and rerun draft production validation plus `quick_validate.py reviewer/spec2plan/plan2do`.
- Writable scope: `.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md`; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/final-report.md`; `.codex/work/20260621-skill-self-evolution-hardening/artifacts/task5-production-gate-draft.md`.
- Verification: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`; `python3 .system/skill-creator/scripts/quick_validate.py reviewer`; `python3 .system/skill-creator/scripts/quick_validate.py spec2plan`; `python3 .system/skill-creator/scripts/quick_validate.py plan2do`.
- Cycle: 1
