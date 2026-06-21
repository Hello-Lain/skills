# Skill Production Report

- Skill: reviewer, idea-refine, interview-me, spec2plan, plan2do
- Change Type: material-update
- Verdict: PASS

## Behavior Lock
- Preserved: `reviewer` route preflight, v2 review report shape, lite/heavy/blocked routing, heavy subagent default, verdict semantics, validators, and source-evidence requirements.
- Preserved: `idea-refine` divergent/convergent flow, Mandatory Exit Gate, save confirmation, direction-only handoff, and Not Doing requirements.
- Preserved: `interview-me` one-question protocol, explicit `yes`, spec quality rubric, canonical save behavior, and no-plan-before-spec rule.
- Preserved: `spec2plan` plan contract reading, artifact contract, `validate_plan_contract.py` hard gate, heavy mode rules, and Skill Production Gate requirements.
- Preserved: `plan2do` primary-agent execution, context-engineering use, verification commands, `validate_execution.py`, bounded rework, Skill Production Gate, and false-completion guard.
- Changed intentionally: added centralized `reviewer` lite-gate integration guide and short consumer hooks for `PASS`, `REVISE`, and `BLOCK`.
- Fallbacks: `BLOCK` stops immediately; repeated `REVISE` stops after the contract limit; unsupported reviewer feedback can be pushed back with source evidence.

## Token Budget
- Before: `reviewer/SKILL.md` 156 lines; `idea-refine/SKILL.md` 235 lines; `interview-me/SKILL.md` 179 lines; `spec2plan/SKILL.md` 97 lines; `plan2do/SKILL.md` 78 lines.
- After: `reviewer/SKILL.md` 160 lines; `reviewer/references/lite-gate-integration.md` 66 lines; `idea-refine/SKILL.md` 246 lines; `interview-me/SKILL.md` 188 lines; `spec2plan/SKILL.md` 100 lines; `plan2do/SKILL.md` 81 lines.
- Moved to references: detailed insertion, replacement, packet, route, verdict, and consumer responsibility guidance moved to `reviewer/references/lite-gate-integration.md`.

## Deterministic Validators
- `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-reviewer-lite-gate/plan.md --mode light`: PASS
- `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-reviewer-lite-gate/plan.md --reset-status`: PASS
- `git diff --check -- reviewer idea-refine interview-me spec2plan plan2do .codex/work/20260621-reviewer-lite-gate`: PASS
- `python3 .system/skill-creator/scripts/quick_validate.py reviewer`: PASS
- `python3 .system/skill-creator/scripts/quick_validate.py idea-refine`: PASS
- `python3 .system/skill-creator/scripts/quick_validate.py interview-me`: PASS
- `python3 .system/skill-creator/scripts/quick_validate.py spec2plan`: PASS
- `python3 .system/skill-creator/scripts/quick_validate.py plan2do`: PASS
- `python3 debug-skill/scripts/skill_audit_core.py --self-test`: PASS
- `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`: PASS
- `rg -n "reviewer-lite|PASS|REVISE|lite-gate-integration|Lite Gate Integration" reviewer idea-refine interview-me spec2plan plan2do`: PASS

## Scenario Gate
- Scenario: future agent inserts or replaces a skill-local review step with `reviewer`.
- RED/control: initial target consumer skill contracts had no shared `reviewer-lite` hook and would require local review wording or ad hoc reviewer use.
- GREEN/retest: `reviewer/references/lite-gate-integration.md` defines shared packet and verdict handling; four target consumers reference it with compact hooks.
- Cleanup: not launched; no temp fixture was created.

## Reviewer Gate
- Mode: heavy
- Route: subagent
- Verdict: PASS
- Report: `.codex/work/20260621-reviewer-lite-gate/review.md`
- Cleanup: archive

## Reuse Attribution
| Source | URL | Borrowed idea | Component | Adoption | Target change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- |
| Superpowers | https://github.com/obra/superpowers | review after task and final review handoff | none | pattern-only | reviewer gate and task artifacts | Runtime differs; no dependency needed |
| Plandex | https://github.com/plandex-ai/plandex | review generated changes before acceptance | none | pattern-only | reviewer-lite before artifact readiness | Product architecture differs |
| Aider | https://github.com/Aider-AI/aider | edit/test feedback loop | none | pattern-only | `REVISE` self-repair loop | CLI not required for Markdown edits |
| pre-commit | https://github.com/pre-commit/pre-commit | deterministic hook-style gates | none | pattern-only | hard validators stay outside reviewer lite | Hook framework not needed |
| Hermes Agent Self-Evolution | https://github.com/NousResearch/hermes-agent-self-evolution | candidates, constraints, fitness, promotion gates | none | pattern-only | debug-skill trace optimization candidates | Direct dependency too heavy |

## Changed Files
- `reviewer/SKILL.md`
- `reviewer/references/lite-gate-integration.md`
- `idea-refine/SKILL.md`
- `interview-me/SKILL.md`
- `spec2plan/SKILL.md`
- `plan2do/SKILL.md`
- `.codex/work/20260621-reviewer-lite-gate/spec.md`
- `.codex/work/20260621-reviewer-lite-gate/manifest.yaml`
- `.codex/work/20260621-reviewer-lite-gate/plan.md`
- `.codex/work/20260621-reviewer-lite-gate/execution/tasks.json`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/context-wave1.md`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/task1-reviewer-guide.md`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/task2-idea-refine.md`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/task3-interview-me.md`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/task4-spec2plan.md`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/task5-plan2do.md`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/task6-validation.md`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/debug-skill-trace.md`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md`
- `.codex/work/20260621-reviewer-lite-gate/artifacts/final-report.md`

## Residual Risks
- None known.
