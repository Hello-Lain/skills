# Skill Production Report

- Skill: skill production workflow (`skill-tokenless`, `skill-creator`, `reviewer`, `edit-orchestration`, `spec2plan`, `plan2do`)
- Change Type: material-update
- Verdict: PASS

## Behavior Lock
- Preserved: skill trigger discovery, `quick_validate.py` validation, reviewer report validation, plan validation, plan2do execution validation, apply_patch as the manual edit route, and preservation of unrelated dirty work.
- Changed intentionally: added a Skill Production Gate contract and validator, integrated the gate into skill creation/planning/execution docs, added apply_patch payload preflight linting, and corrected reviewer subagent lifecycle semantics.
- Fallbacks: missing production evidence blocks final success; heavy reviewer waits do not downgrade to inline; abnormal reviewer subagents are diagnosed with `2 x 45s`; healthy running reviewer subagents continue; no nested reviewer subagents.

## Token Budget
- Before: no shared production gate; `skill-tokenless/SKILL.md` did not route final skill production reports.
- After: `skill-tokenless/SKILL.md` remains compact and routes detailed gate behavior to `skill-tokenless/references/skill-production-gate.md`.
- Moved to references: production report schema, GitHub reuse matrix, reviewer health policy, validation commands, and detailed gate phases.

## Deterministic Validators
- `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`: PASS
- `python3 edit-orchestration/scripts/lint_apply_patch_payload.py --self-test`: PASS
- `python3 reviewer/scripts/validate_review_report.py --self-test`: PASS
- `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-production-gate/plan.md --mode light`: PASS
- `for d in skill-tokenless reviewer edit-orchestration plan2do spec2plan .system/skill-creator; do python3 .system/skill-creator/scripts/quick_validate.py "$d" || exit 1; done`: PASS

## Scenario Gate
- Scenario: material skill workflow update must preserve behavior while adding deterministic production gating.
- RED/control: reviewer gate first returned `BLOCK` because final acceptance evidence was missing.
- GREEN/retest: missing production report, task 5 artifacts, final report, and execution completion state were added; focused reviewer recheck overwrote `.codex/work/20260621-skill-production-gate/review.md` with `PASS`.
- Cleanup: prior malformed reviewer attempt was canceled and archived after violating no-nested reviewer rules; final focused reviewer subagent was archived after report collection.

## Reviewer Gate
- Mode: heavy
- Route: subagent
- Verdict: PASS
- Report: `.codex/work/20260621-skill-production-gate/review.md`
- Cleanup: archive

## Reuse Attribution
| Source | URL | Borrowed idea | Component | Adoption | Target change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- |
| Superpowers | https://github.com/obra/superpowers | task-local review, final review, progress ledger | workflow pattern | adapted | production gate phases, reviewer gate, execution artifacts | direct runtime not used because local skill system differs |
| Plandex | https://github.com/plandex-ai/plandex | pending/cumulative diff review before apply | review-before-apply pattern | pattern-only | edit-orchestration route guidance | dependency rejected to avoid mandatory external runtime |
| Aider | https://github.com/Aider-AI/aider | edit/test feedback loop | repo-map/edit loop pattern | pattern-only | validator and diff-inspection discipline | dependency rejected to keep local gate deterministic |
| pre-commit | https://github.com/pre-commit/pre-commit | deterministic hook-style quality gates | optional hook model | pattern-only | production report validator and script self-tests | direct mandatory hooks rejected |
| ast-grep | https://github.com/ast-grep/ast-grep | AST-aware rewrite route | optional helper | pattern-only | edit-orchestration route matrix | direct dependency remains optional |
| OpenRewrite | https://github.com/openrewrite/rewrite | recipe/dry-run large rewrite discipline | optional helper | pattern-only | edit-orchestration large rewrite guidance | JVM-specific runtime rejected for this local change |
| Hermes self-evolution | https://github.com/NousResearch/hermes-agent-self-evolution | constraints, fitness, promotion gates | evaluation pattern | adapted | production gate acceptance and reviewer rework loop | direct dataset pipeline rejected as out of scope |

## Changed Files
- `.system/skill-creator/SKILL.md`
- `skill-tokenless/SKILL.md`
- `skill-tokenless/references/skill-production-gate.md`
- `skill-tokenless/references/testing.md`
- `skill-tokenless/references/validation.md`
- `skill-tokenless/scripts/validate_skill_production.py`
- `reviewer/SKILL.md`
- `reviewer/references/subagent-dispatch.md`
- `edit-orchestration/references/apply-patch.md`
- `edit-orchestration/references/route-matrix.md`
- `edit-orchestration/scripts/lint_apply_patch_payload.py`
- `spec2plan/SKILL.md`
- `spec2plan/references/plan-contract.md`
- `plan2do/SKILL.md`
- `plan2do/references/execution-contract.md`
- `.codex/work/20260621-skill-production-gate/spec.md`
- `.codex/work/20260621-skill-production-gate/plan.md`
- `.codex/work/20260621-skill-production-gate/execution/tasks.json`
- `.codex/work/20260621-skill-production-gate/review.md`
- `.codex/work/20260621-skill-production-gate/artifacts/rework-guidance.md`
- `.codex/work/20260621-skill-production-gate/artifacts/production-report.md`
- `.codex/work/20260621-skill-production-gate/artifacts/task1-execution.md`
- `.codex/work/20260621-skill-production-gate/artifacts/task1-verification.md`
- `.codex/work/20260621-skill-production-gate/artifacts/task2-execution.md`
- `.codex/work/20260621-skill-production-gate/artifacts/task2-verification.md`
- `.codex/work/20260621-skill-production-gate/artifacts/task3-execution.md`
- `.codex/work/20260621-skill-production-gate/artifacts/task3-verification.md`
- `.codex/work/20260621-skill-production-gate/artifacts/task4-execution.md`
- `.codex/work/20260621-skill-production-gate/artifacts/task4-verification.md`
- `.codex/work/20260621-skill-production-gate/artifacts/task5-execution.md`
- `.codex/work/20260621-skill-production-gate/artifacts/task5-verification.md`
- `.codex/work/20260621-skill-production-gate/artifacts/final-report.md`

## Residual Risks
- Actual provider/status anomaly behavior cannot be fully simulated locally; docs now encode the required policy and the nested reviewer violation was found and fixed during execution.
