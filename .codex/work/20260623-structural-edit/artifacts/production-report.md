# Skill Production Report

- Skill: `structural-edit`
- Change Type: new-skill
- Verdict: PASS

## Behavior Lock
- Preserved: structure-first routing, user-controlled tool roots, deterministic validators, explicit migration outcome, no silent downgrade when a structural route should apply.
- Changed intentionally: introduced `structural-edit` as the default manual-edit entrypoint; downgraded `edit-orchestration` to compatibility-shell status.
- Fallbacks: strict text fallback only for tiny unique low-risk edits; inline-heavy reviewer fallback only because heavy subagent backend is unavailable in this environment.

## Token Budget
- Before: `structural-edit` absent; `edit-orchestration/SKILL.md` at HEAD = 81 lines / 586 words.
- After: `structural-edit/SKILL.md` = 52 lines / 356 words; `edit-orchestration/SKILL.md` = 44 lines / 224 words.
- Moved to references: route matrix, tooling/install policy, fallback policy, migration, compatibility, validation scenarios under `structural-edit/references/`.

## Deterministic Validators
- `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/structural-edit`: PASS
- `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`: PASS
- `python3 structural-edit/scripts/prepare_structural_tools.py --list`: PASS
- `python3 structural-edit/scripts/self_check_structural_tools.py --tool ast-grep --json`: PASS (deterministic missing-tool readiness report; nonzero exit is expected for absent local tool)
- `python3 structural-edit/scripts/manifest_report.py --summary`: PASS
- `python3 structural-edit/scripts/validate_structural_routes.py`: PASS
- `python3 reviewer/scripts/validate_review_report.py --self-test`: PASS
- `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`: PASS

## Scenario Gate
- Scenario: replace patch-first editing with structure-first routing plus compatibility-shell migration.
- RED/control: `git show HEAD:edit-orchestration/SKILL.md` still exposed the old default manual-edit entrypoint and patch-first framing, so the pre-change baseline failed the spec requirement.
- GREEN/retest: `python3 structural-edit/scripts/validate_structural_routes.py` passes all required scenarios; both skills pass `quick_validate.py`; `edit-orchestration` now delegates to `structural-edit`.
- Cleanup: not launched

## Reviewer Gate
- Mode: heavy
- Route: inline
- Verdict: PASS
- Report: `.codex/work/20260623-structural-edit/review.md`
- Cleanup: unavailable because `codex2codex` backend is blocked by missing pinned dependency `openai-codex==0.1.0b3`

## Reuse Attribution
| Source | URL | Borrowed idea | Component | Adoption | Target change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- |
| Superpowers | https://github.com/obra/superpowers | explicit review gate after task completion | production/review workflow | adapted | draft+final gating | local runtime differs |
| ast-grep | https://github.com/ast-grep/ast-grep | AST-aware rewrite default | Python + secondary JS/TS route | adapted | route matrix + tooling refs | no direct dependency vendoring |
| OpenRewrite | https://github.com/openrewrite/rewrite | build-context-gated Java rewrites | Java route policy | adapted | `BLOCK` without valid build context | plugin/runtime not bundled |

## Changed Files
- `structural-edit/SKILL.md`
- `structural-edit/agents/openai.yaml`
- `structural-edit/scripts/route_decision.py`
- `structural-edit/scripts/prepare_structural_tools.py`
- `structural-edit/scripts/self_check_structural_tools.py`
- `structural-edit/scripts/manifest_report.py`
- `structural-edit/scripts/validate_structural_routes.py`
- `structural-edit/references/route-matrix.md`
- `structural-edit/references/tooling.md`
- `structural-edit/references/fallback-policy.md`
- `structural-edit/references/migration.md`
- `structural-edit/references/compatibility.md`
- `structural-edit/references/validation-scenarios.md`
- `edit-orchestration/SKILL.md`
- `edit-orchestration/agents/openai.yaml`
- `edit-orchestration/references/route-matrix.md`
- `edit-orchestration/references/tooling.md`
- `.codex/work/20260623-structural-edit/manifest.yaml`
- `.codex/work/20260623-structural-edit/plan.md`
- `.codex/work/20260623-structural-edit/execution/tasks.json`
- `.codex/work/20260623-structural-edit/artifacts/context-wave1.md`
- `.codex/work/20260623-structural-edit/artifacts/task1-scaffold.md`
- `.codex/work/20260623-structural-edit/artifacts/task2-toolchain.md`
- `.codex/work/20260623-structural-edit/artifacts/task3-migration.md`
- `.codex/work/20260623-structural-edit/artifacts/task4-validation.md`
- `.codex/work/20260623-structural-edit/artifacts/production-report.md`
- `.codex/work/20260623-structural-edit/artifacts/final-report.md`
- `.codex/work/20260623-structural-edit/subagents/planner.md`
- `.codex/work/20260623-structural-edit/subagents/reviewer.md`
- `.codex/work/20260623-structural-edit/subagents/synthesizer.md`

## Residual Risks
- Heavy reviewer isolation is simulated inline because `codex2codex` is currently blocked in this environment.
- Scenario validator proves route selection and hard-stop policy, not end-to-end live rewrites with each external tool installed.
