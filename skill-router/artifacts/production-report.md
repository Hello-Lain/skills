# Skill Production Report

- Skill: skill-router
- Change Type: material-update
- Verdict: PASS

## Behavior Lock
- Preserved: one primary route, saved-policy precedence, staleness handling, global soft hook, deterministic fixtures, no shell writes, and `functions.apply_patch` as strict text fallback/execution tool.
- Changed intentionally: `sr-013-manual-file-edit` primary route is now `skill:structural-edit`; `validate_fixtures.py` detects known stale route names, manual-edit priority inversion, missing primary skill path evidence, and can repair encoded known drift with `--repair-known-drift`.
- Fallbacks: `functions.apply_patch` is available only when `structural-edit` classifies the edit as tiny, unique, low-risk strict text fallback; project-owned generators remain fallback when output ownership applies.

## Token Budget
- Before: `SKILL.md` 41 lines, 306 words.
- After: `SKILL.md` 42 lines, 328 words.
- Moved to references: self-update contract documented in `references/policy-schema.md`; route precedence clarified in `references/route-decision.md`.

## Deterministic Validators
- `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/skill-router`: PASS
- `python /data/lcq/.codex/skills/skill-router/scripts/validate_fixtures.py`: PASS
- `python /data/lcq/.codex/skills/skill-router/scripts/validate_fixtures.py --repair-known-drift`: PASS
- `python3 /data/lcq/.codex/skills/structural-edit/scripts/validate_structural_routes.py`: PASS
- `wc -l /data/lcq/.codex/skills/skill-router/SKILL.md /data/lcq/.codex/skills/skill-router/agents/openai.yaml`: PASS
- `wc -w /data/lcq/.codex/skills/skill-router/SKILL.md`: PASS
- `rg "trigger|validation|quick_validate|Hard Stops|references/" /data/lcq/.codex/skills/skill-router`: PASS
- `rtk proxy bash -lc 'test ! -e "$1/.tmp-forward-test"' _ /data/lcq/.codex/skills/skill-router`: PASS
- `python3 /data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py /data/lcq/.codex/skills/skill-router/artifacts/review-report.md --root /data/lcq/.codex/skills`: PASS
- `python3 /data/lcq/.codex/skills/skill-tokenless/scripts/validate_skill_production.py /data/lcq/.codex/skills/skill-router/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`: PASS

## Scenario Gate
- Scenario: detect and repair manual-edit route conflict where a low-level write tool was primary despite `structural-edit` owning edit decisions.
- RED/control: added invariant made pre-fix `validate_fixtures.py` fail with `sr-013-manual-file-edit: manual edits must route first to skill:structural-edit`.
- GREEN/retest: `validate_fixtures.py --repair-known-drift` rewrote `sr-013` and the manual-edit fixture; plain `validate_fixtures.py` then passed with 18 policies and 11 fixtures.
- Cleanup: no temp fixtures created; `.tmp-forward-test` absent.

## Reviewer Gate
- Mode: heavy
- Route: inline
- Verdict: PASS
- Report: `skill-router/artifacts/review-report.md`
- Cleanup: not launched

## Reuse Attribution
| Source | URL | Borrowed idea | Component | Adoption | Target change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- |
| pre-commit | https://github.com/pre-commit/pre-commit | deterministic hook-style quality gates | validator pattern | pattern-only | route drift invariant and repair-gated validation | no dependency needed |
| Aider | https://github.com/Aider-AI/aider | repo-aware edit/test feedback loop | RED/GREEN repair loop | pattern-only | fail on priority drift, repair, retest | no dependency needed |
| ast-grep | https://github.com/ast-grep/ast-grep | structural route before text fallback | edit routing precedence | pattern-only | `structural-edit` primary, `apply_patch` fallback | no dependency needed |

## Changed Files
- `skill-router/SKILL.md`
- `skill-router/references/route-decision.md`
- `skill-router/references/policy-schema.md`
- `skill-router/references/scenario-fixtures.json`
- `skill-router/policies/known-conflicts.json`
- `skill-router/scripts/validate_fixtures.py`
- `skill-router/artifacts/review-report.md`
- `skill-router/artifacts/production-report.md`

## Residual Risks
- Self-repair is intentionally narrow; unknown route conflicts still require a reviewer-backed policy update and a new encoded invariant.
