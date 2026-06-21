# Spec: Skill Production Gate

## Objective
Build a production-grade quality gate for Codex skill creation and material skill updates, so future skill work preserves behavior, controls token cost, validates artifacts, and uses `reviewer` as an explicit quality gate before completion.

## Users
- Primary: the main Codex agent maintaining `/data/lcq/.codex/skills`.
- Secondary: reviewer subagents and future agents that create or modify skills using `skill-creator`, `skill-tokenless`, `spec2plan`, and `plan2do`.

## Problem
Recent work on `reviewer`, `edit-orchestration`, `plan2do`, `spec2plan`, and `skill-tokenless` exposed repeated quality-control gaps:

- Skill production relies on the agent remembering optional checks instead of a shared enforced gate.
- `reviewer` heavy subagent lifecycle handling incorrectly treated healthy running time as a timeout condition and allowed inline fallback after transient wait/provider issues.
- Patch failures showed `edit-orchestration` lacks deterministic preflight guidance for complex `apply_patch` payloads.
- `plan2do` and `spec2plan` can validate structure while still missing stronger evidence traceability.
- GitHub-derived best practices are useful but not captured in a reusable local implementation path.

## Success Criteria
- A shared `Skill Production Gate` contract exists under `skill-tokenless/references/`.
- A deterministic validator script exists for production gate reports and has a self-test.
- `skill-tokenless` and `.system/skill-creator` explicitly require the gate for new skills and material skill changes.
- `reviewer` subagent policy states that healthy running subagents are left running; abnormal subagents are diagnosed with exactly 2 polls, 45 seconds each, before `BLOCK`, cleanup, or a narrower retry with user-visible evidence.
- `edit-orchestration` includes patch-payload preflight guidance and a local script to lint common `apply_patch` payload mistakes.
- `plan2do` and `spec2plan` reference the skill production gate where skill work is planned or executed.
- GitHub reuse sources and adoption modes are documented for later planning and maintenance.
- Existing validators pass for changed skills and new scripts.
- Final `reviewer` gate returns `PASS` or valid rework is completed.

## Scope
### In
- Update these targets:
  - `skill-tokenless`
  - `.system/skill-creator`
  - `reviewer`
  - `edit-orchestration`
  - `plan2do`
  - `spec2plan`
- Add production gate reference and validator under `skill-tokenless/`.
- Add patch payload lint helper under `edit-orchestration/`.
- Update docs/contracts only where needed to make the gate discoverable and executable.
- Validate with local self-tests, skill validators, plan/execution validators, and reviewer report validator.

### Out
- Do not rewrite all existing skills.
- Do not force Plandex, Aider, OpenRewrite, ast-grep, or pre-commit as mandatory dependencies.
- Do not run long live evals, production service tests, secret-bearing tests, or expensive external workflows.
- Do not use inline fallback when a heavy reviewer subagent has transient wait/provider/network issues; if it is healthy or making progress, continue waiting instead of canceling or archiving.
- Do not revert unrelated existing dirty changes.

## Requirements
### Functional
- The production gate must define required phases: Behavior Lock, token/read-cost pass, deterministic validators, scenario or mock forward test, reviewer gate, cleanup proof, final production report.
- The production gate validator must check for required production report sections and key evidence fields.
- The validator must support `--self-test`.
- `skill-tokenless` must route new or material skill creation/update work to the production gate.
- `.system/skill-creator` must state that after `quick_validate.py`, material skills run `skill-tokenless` production gate and `reviewer`.
- `reviewer` dispatch docs must encode the explicit health policy: poll only after abnormal signals; poll 2 times, each 45 seconds; do not downgrade to inline because of transient wait/provider/network issues; keep healthy running subagents alive; after confirmed abnormal state return `BLOCK` or relaunch only with a narrower packet after cleanup.
- `edit-orchestration` must document patch preflight checks and provide a lint helper for common malformed `apply_patch` payloads.
- `spec2plan` must plan skill work with production-gate tasks and reviewer gate.
- `plan2do` must require production-gate evidence when executing plans that create or materially modify skills.
- External reuse documentation must list source URL, borrowed idea, adoption mode, and whether a component is direct, optional, adapted, or rejected.

### Non-Functional
- Keep always-loaded `SKILL.md` files compact; put long schemas and examples in references.
- Avoid mandatory new third-party runtime dependencies.
- Prefer deterministic scripts over prose-only checks.
- Keep subagent raw transcripts out of main context; keep only synthesized reports and cleanup status.
- Preserve compatibility with current `quick_validate.py`, `validate_review_report.py`, `validate_plan_contract.py`, and `validate_execution.py`.

## Constraints
- Manual edits must use `apply_patch`.
- Workspace root is `/data/lcq/.codex/skills`.
- Existing dirty/untracked work must be preserved.
- Reviewer heavy subagent health policy is binding: healthy `running` with activity continues; abnormal diagnosis uses `2` polls, `45s` each, with no automatic inline downgrade.
- If required reviewer isolation cannot produce a valid report after confirmed abnormal diagnosis, completion is blocked or requires an explicit retry/narrower packet, not silent fallback.

## GitHub Reuse Sources
- `obra/superpowers`: borrow subagent-per-task, per-task review, final review, file handoffs, progress ledger. Adoption: adapted pattern.
- `plandex-ai/plandex`: borrow cumulative diff review sandbox concept. Adoption: pattern-only for review-before-apply.
- `Aider-AI/aider`: borrow repo-map plus edit/test feedback loop. Adoption: pattern-only.
- `pre-commit/pre-commit`: borrow deterministic hook-style quality gates. Adoption: optional/direct for users who want hooks, not required.
- `ast-grep/ast-grep`: borrow structural rewrite route. Adoption: optional direct helper.
- `openrewrite/rewrite`: borrow recipe/dry-run large rewrite pattern. Adoption: optional JVM-specific helper.
- `NousResearch/hermes-agent-self-evolution`: borrow dataset/constraint/fitness/promotion-gate thinking already mapped in `debug-skill`. Adoption: adapted pattern.

## Assumptions To Validate
- [ ] A lightweight production report schema is enough for v1. Validate by self-test and one mock report.
- [ ] Existing skill validators remain compatible after docs/script additions. Validate with `quick_validate.py`.
- [ ] Reviewer report validation still passes after lifecycle doc changes. Validate with `validate_review_report.py --self-test`.
- [ ] Plan/execution validators still pass for the implementation workspace. Validate with `validate_plan_contract.py` and `validate_execution.py`.

## Risks
- Over-gating small edits could waste tokens. Mitigation: require gate only for new skills, material skill changes, validator scripts, or workflow/safety changes.
- Subagent waiting can still consume time. Mitigation: diagnose only abnormal subagents with `2 x 45s`; continue healthy running work; then `BLOCK` or narrower relaunch only after confirmed abnormal state and cleanup.
- Validator can become too shallow. Mitigation: include self-test fixtures and required evidence fields.
- Patch lint helper could imply false safety. Mitigation: describe it as preflight, not replacement for `apply_patch` failure recovery and diff inspection.

## Acceptance Checks
- `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`
- `python3 edit-orchestration/scripts/lint_apply_patch_payload.py --self-test`
- `python3 reviewer/scripts/validate_review_report.py --self-test`
- `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-production-gate/plan.md --mode light`
- `python3 plan2do/scripts/compile_execution.py .codex/work/20260621-skill-production-gate/plan.md`
- `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-skill-production-gate`
- `python3 .system/skill-creator/scripts/quick_validate.py skill-tokenless`
- `python3 .system/skill-creator/scripts/quick_validate.py reviewer`
- `python3 .system/skill-creator/scripts/quick_validate.py edit-orchestration`
- `python3 .system/skill-creator/scripts/quick_validate.py plan2do`
- `python3 .system/skill-creator/scripts/quick_validate.py spec2plan`
- `python3 .system/skill-creator/scripts/quick_validate.py .system/skill-creator`
- Final reviewer gate report exists and validates.

## Open Questions
- None for v1.
