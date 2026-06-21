# Spec: plan2do Skill

## Objective
Build a local `plan2do` skill for Codex users and the primary agent to execute `spec2plan`-generated `plan.md` files with a quality loop: task execution, verification, independent review, primary-agent rework direction, bounded fixes, and final execution reporting.

## Users
- Primary user: the primary Codex agent operating in `/data/lcq/.codex/skills`.
- Secondary user: local Codex users who invoke `$plan2do` to execute an existing plan.
- Compatibility user: users who explicitly request `codex2codex` execution for worker isolation.

## Problem
The current workflow has `spec2plan` to produce executable plans, but no dedicated skill that reliably executes those plans to completion. This gap leads to incomplete functionality, weak verification, unreviewed quality regressions, over-engineered architecture, and polluted primary-agent context from raw logs, diffs, and worker transcripts.

## Success Criteria
- `plan2do` can consume a `spec2plan` `plan.md` and identify task waves, writable scopes, verification commands, output artifacts, and review expectations.
- Default execution path uses the primary agent unless the user explicitly requests `codex2codex`.
- The `codex2codex` path is supported when requested and keeps worker logs and transcripts outside the primary context.
- Each task completion is judged against acceptance criteria, verification output, changed files, and review findings.
- Functional incompleteness, poor quality, or over-engineered architecture triggers rework instead of a false completion.
- Every rework cycle starts with the primary agent writing concrete rework guidance derived from verification and review evidence.
- Final completion requires passing verification, review PASS, or a documented blocker that prevents completion.
- Large logs, raw diffs, worker outputs, and transcripts are stored as artifacts by path and summarized in the active context.
- The implementation plan and final skill use `/data/lcq/.codex/skills/context-engineering` rules for focused context, quarantine, rehydration, decision packets, and context capsules.

## Scope
### In
- Create a new `plan2do` skill folder under `/data/lcq/.codex/skills/plan2do`.
- Include required `SKILL.md` frontmatter and body.
- Include `agents/openai.yaml` UI metadata.
- Include directly useful references or scripts only when they reduce repeated manual workflow.
- Define the default primary-agent execution workflow.
- Define the explicit `codex2codex` execution workflow.
- Define intake validation for `spec2plan` plans.
- Define quality gates for functionality, verification, architecture simplicity, review, and artifacts.
- Define bounded rework behavior with primary-agent rework guidance before fixes.
- Define context governance using `context-engineering`.
- Add focused validation for the skill artifact.

### Out
- Do not rewrite the original spec or plan.
- Do not choose product direction or re-scope upstream requirements.
- Do not bypass `spec2plan` plan contract.
- Do not auto-deploy production changes.
- Do not delete, reset, or roll back user work without explicit approval.
- Do not silently continue after repeated verification or review failures.
- Do not create a broad project management framework outside Codex skill execution.

## Requirements
### Functional
- `plan2do` must trigger for requests to execute, implement, run, complete, or finish a `spec2plan` plan.
- `plan2do` must require a `plan.md` path or infer the current topic workspace plan when unambiguous.
- `plan2do` must inspect the plan contract fields before execution: task breakdown, dependencies, wave order, writable scope, verification, acceptance criteria, output artifacts, rollback, risks, and execution handoff.
- `plan2do` must default to primary-agent execution.
- `plan2do` must use `codex2codex` only when the user explicitly requests it or names it.
- `plan2do` must execute tasks in dependency order and respect wave write-scope separation.
- `plan2do` must run focused pre-checks and post-checks from the plan when safe.
- `plan2do` must write execution notes, validation summaries, review findings, and final reports under the plan workspace `artifacts/` directory.
- `plan2do` must conduct a quality review before final completion for non-trivial plans.
- `plan2do` must treat missing features, failing verification, material review findings, and unnecessary architectural complexity as failures requiring rework.
- `plan2do` must require the primary agent to write rework guidance before each fix cycle.
- `plan2do` must stop with a blocker report when the same issue repeats after bounded rework cycles or when user input/approval is required.
- `plan2do` must end with a concise final report containing mode, completed tasks, files changed, verification, review verdict, rework cycles, artifacts, blockers, and omitted raw data.

### Non-Functional
- Keep active context small by summarizing large data and linking artifact paths.
- Treat compressed summaries as continuity hints, not evidence.
- Rehydrate from source-of-truth files, plan sections, diffs, and test outputs before risky or final acceptance decisions.
- Prefer simple, boring, maintainable implementation over speculative abstraction.
- Preserve unrelated user work in dirty worktrees.
- Use `apply_patch` for manual edits.
- Use existing local skill patterns and validation scripts rather than inventing a parallel skill system.

## Constraints
- Work happens in `/data/lcq/.codex/skills`.
- Skill output should be discoverable by Codex from `/data/lcq/.codex/skills/plan2do`.
- Must follow local `AGENTS.md` rules for preserving user work and artifact locations.
- Must follow `skill-creator` requirements for required frontmatter, concise body, and `agents/openai.yaml`.
- Must integrate `context-engineering` governance rather than duplicating a weaker context policy.
- Must support `codex2codex` as an explicit compatibility mode, but not as the default.

## Assumptions To Validate
- [ ] A reference file for execution/report contracts is useful enough to avoid bloating `SKILL.md` - validate by reviewing final `SKILL.md` length and clarity.
- [ ] No executable script is needed for v1 beyond existing validators and `codex2codex` scripts - validate during implementation after checking repeated command patterns.
- [ ] `agents/openai.yaml` can be generated or written directly with standard fields - validate with `quick_validate.py`.
- [ ] Existing `codex2codex/scripts/run_plan.py` can serve the explicit multi-agent path - validate with a dry-run command when a sample plan exists.

## Risks
- `plan2do` may duplicate `codex2codex` responsibilities - mitigate by defining `codex2codex` as optional backend and keeping `plan2do` responsible for mode choice, quality gates, rework guidance, and final acceptance.
- The default primary-agent mode may pollute context - mitigate with `context-engineering` focused context packs, artifact quarantine, rehydration, and capsule rules.
- Quality review may be vague - mitigate with explicit failure criteria for functional gaps, verification failures, and over-engineering.
- Rework may loop too long - mitigate with bounded cycles and blocker reports.
- The skill may become too large - mitigate with progressive disclosure and references for detailed contracts.

## Acceptance Checks
- `plan2do/SKILL.md` exists with valid `name` and `description` frontmatter.
- `plan2do/agents/openai.yaml` exists and matches the skill purpose.
- The skill documents default primary-agent execution and explicit `codex2codex` execution.
- The skill documents context-governance gates using `context-engineering`.
- The skill documents quality gates and primary-agent rework guidance before fix cycles.
- The skill validates with `/data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`.
- A manual dry-run review of the skill against this spec confirms no requirement is missing.

## Open Questions
- Exact maximum rework count is not user-confirmed. Proposed default: two fix cycles per failed task or review scope before blocker reporting.
