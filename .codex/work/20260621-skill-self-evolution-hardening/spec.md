# Spec: Skill Self-Evolution Hardening

## Objective
Fix the four concrete skill-chain defects exposed by the reviewer-lite integration run, and enhance `debug-skill` so future skill optimization follows an evidence-driven self-evolution loop inspired by Hermes Agent Self-Evolution while remaining human-approved and safe.

## Users
- Primary: Codex agents maintaining `/data/lcq/.codex/skills` and executing skill-production workflows.
- Secondary: the user, who needs stable skill optimization workflows with clear evidence, bounded self-repair, and reusable self-evolution protocols.

## Problem
The prior `reviewer-lite` integration completed successfully but exposed avoidable workflow friction:

- `reviewer` subagent review used the wrong workspace root and produced a false missing-artifact finding.
- `spec2plan` and `plan2do` allowed an invalid mental model where non-review finalization tasks could remain pending before pre-review readiness.
- `skill-tokenless/scripts/validate_skill_production.py` scanned status words too broadly and treated `BLOCK` inside a command string as a blocked validator outcome.
- `debug-skill` captured useful trace evidence, but continuous tracking was manual and lacked a lightweight in-run protocol separate from deep audit.

Hermes Agent Self-Evolution provides reusable ideas: evaluation datasets, execution traces, constraints, fitness scoring, candidate variants, guardrails, and human review. This project should adapt those protocols without importing heavy dependencies or enabling uncontrolled self-modification.

## Success Criteria
- `reviewer` review packets require enough path evidence to prevent cwd/root confusion, and a fixture or scenario proves missing-artifact findings use the correct workspace.
- `spec2plan` and `plan2do` explicitly state that draft pre-review readiness requires all non-review tasks complete; finalization after reviewer is coordinator acceptance, not a pending non-review task.
- `skill-tokenless` production-report validation parses deterministic validator outcomes structurally and no longer fails because a command string contains `BLOCK`.
- `debug-skill` supports two documented modes:
  - lightweight in-run trace mode for continuous skill trajectory capture;
  - deep audit mode for reuse search, candidate scoring, and promotion recommendations.
- `debug-skill` includes Hermes-inspired protocol fields for evaluation examples, constraints, fitness dimensions, candidate improvements, promotion gates, redaction, and human approval.
- All changed skills/scripts pass their existing validators and any new or updated self-tests.
- Final execution includes Skill Production Gate and reviewer `PASS`.

## Scope
### In
- Update `reviewer/references/subagent-dispatch.md` or adjacent reviewer guidance to require cwd-relative and absolute artifact paths, path existence checks, and cwd recording before declaring evidence missing.
- Update `spec2plan/references/plan-contract.md` and `plan2do/references/execution-contract.md` so plan authors and executors model final review readiness correctly.
- Update `skill-tokenless/scripts/validate_skill_production.py` and its self-tests so deterministic validator status detection ignores status words inside command text or prose unless they are explicit outcomes.
- Update `debug-skill/SKILL.md`, `debug-skill/references/hermes-reuse.md`, and `debug-skill/scripts/skill_audit_core.py` only as needed to add the lightweight trace/deep audit split and Hermes-inspired candidate promotion protocol.
- Add or update tests/fixtures that reproduce each prior defect and prove the fix.

### Out
- Do not let `debug-skill` automatically edit, commit, or deploy skill changes.
- Do not import DSPy, GEPA, Hermes SessionDB, Darwinian Evolver, or other heavy Hermes dependencies in v1.
- Do not rewrite all skill workflows or modify unrelated skills.
- Do not bypass `reviewer`, Skill Production Gate, `quick_validate.py`, or existing plan/execution validators.
- Do not mine private session history unless a future user explicitly approves it.

## Requirements
### Functional
- Reviewer path hardening:
  - Reviewer dispatch packets must include both cwd-relative and absolute artifact paths for workspace artifacts when available.
  - Reviewer instructions must require `pwd` and path existence checks before reporting a missing local artifact.
  - Reviewer reports must cite the checked path form when evidence is missing.
- Pre-review readiness modeling:
  - `spec2plan` plan contract must warn that pre-review draft readiness allows only review tasks to remain pending.
  - `plan2do` execution contract must state that coordinator finalization after reviewer is not an executable pending task before reviewer launch.
  - A fixture or validation scenario must fail before the wording/logic fix and pass after it.
- Production-report validator:
  - Deterministic validator outcomes must be parsed from explicit result positions such as `: PASS`, `: BLOCK`, or `: SKIPPED`.
  - A command like ``rg -n "PASS|REVISE|BLOCK" ...`: PASS`` must validate as `PASS`, not fail due to the command token `BLOCK`.
  - Self-tests must include the prior false-positive case.
- Debug-skill self-evolution:
  - `debug-skill` must document lightweight trace mode for in-run capture of trigger, loaded skills, decisions, actions, failures, recovery, validators, outcome, and optimization hints.
  - `debug-skill` must keep deep audit mode for full report template, external reuse search, Hermes-style candidates, and recommendation.
  - `debug-skill` must distinguish candidate recommendation from execution; auto-modification remains forbidden without explicit user approval.
  - `skill_audit_core.py` should expose deterministic primitives or report skeleton support for trace/candidate fields if doing so reduces manual drift.

### Non-Functional
- Safety: no autonomous skill edits from `debug-skill`; all modifications still require user-approved `spec2plan`/`plan2do` or equivalent.
- Reliability: every prior defect has a direct regression check.
- Decoupling: improvements should harden shared contracts and validators instead of embedding one-off rules in unrelated skills.
- Cost: Hermes ideas are adapted as local protocols and small scripts, not heavy runtime dependencies.
- Privacy: any future session-history mining remains opt-in and must redact secrets before use.

## Constraints
- Work occurs under `/data/lcq/.codex/skills`.
- Preserve current public skill trigger behavior unless the spec explicitly requires a clearer trigger for debug trace/deep audit.
- Use `apply_patch` for manual edits.
- Material skill/script changes require Skill Production Gate, reviewer gate, and final validation.
- Follow current AGENTS.md cleanup policy; preserve existing `.codex/work/20260621-reviewer-lite-gate/` evidence.

## Hermes Ideas To Adapt
- Evaluation examples and dataset splits from `evolution/core/dataset_builder.py`: use as inspiration for small audit scenarios or fixtures, not as a required DSPy dataset.
- Constraint gate shape from `evolution/core/constraints.py`: use explicit pass/fail checks with names, messages, and severity.
- Fitness scoring from `evolution/core/fitness.py`: use multi-dimensional candidate scoring such as quality, efficiency, evidence, context, tooling, verification, user friction, reuse, and safety.
- External importer redaction from `evolution/core/external_importers.py`: keep secret redaction and no private-history mining by default.
- Evolution orchestration from `evolution/skills/evolve_skill.py`: load target, build evidence, generate candidates, validate constraints, compare candidates, and require human review.
- Skill module parsing from `evolution/skills/skill_module.py`: preserve frontmatter and body boundaries when reasoning about skill changes.

## Assumptions To Validate
- [ ] `reviewer` path confusion can be prevented with packet/checklist wording alone - validate with a reviewer packet fixture or scenario.
- [ ] `pre_review_ready.py` already enforces the desired draft-state behavior - validate whether docs-only updates are sufficient or script tests should be added.
- [ ] Production-report outcome parsing can be fixed without weakening detection of real `BLOCK` outcomes - validate with positive and negative self-test cases.
- [ ] `debug-skill` can support lightweight trace mode mostly through docs and helper skeletons - validate by generating a trace artifact in a fixture.
- [ ] Hermes protocols can be adapted without adding dependencies - validate by keeping imports unchanged unless a local stdlib-only helper is needed.

## Risks
- Reviewer path-hardening may add packet verbosity - mitigate with a compact checklist and only require absolute paths when local artifacts are cited.
- Pre-review readiness docs may not be enough for future agents - mitigate with fixture tests or explicit plan-contract examples.
- Validator parsing may become too strict and miss real blocked validators - mitigate with self-tests for both command-token false positives and explicit `: BLOCK` outcomes.
- Debug-skill self-evolution wording may encourage autonomous edits - mitigate with repeated human-approval and no-auto-modification gates.
- Hermes-inspired terminology may bloat `debug-skill` - mitigate by moving protocol detail to references and keeping `SKILL.md` concise.

## Acceptance Checks
- `python3 skill-tokenless/scripts/validate_skill_production.py --self-test` passes and includes a false-positive regression where a command contains `BLOCK` but outcome is `PASS`.
- `python3 plan2do/scripts/pre_review_ready.py --self-test` passes, and either its tests or docs demonstrate non-review pending tasks block draft readiness.
- `python3 debug-skill/scripts/skill_audit_core.py --self-test` passes after any helper changes.
- `python3 reviewer/scripts/validate_review_report.py <review-report>` passes for the final reviewer report.
- `python3 .system/skill-creator/scripts/quick_validate.py reviewer`, `debug-skill`, `spec2plan`, `plan2do`, and `skill-tokenless` pass where those directories are changed.
- `git diff --check -- reviewer spec2plan plan2do skill-tokenless debug-skill .codex/work/20260621-skill-self-evolution-hardening` passes.
- A Skill Production Gate report validates at draft and final stages.
- Final reviewer verdict is `PASS`.

## Open Questions
- None blocking. Exact fixture locations and whether `skill_audit_core.py` needs code changes can be decided during planning from the smallest reliable implementation.
