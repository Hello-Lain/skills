# reviewer Implementation Plan

Mode: light
Risk level: Medium
Confidence: High

## Goal

Implement the confirmed `reviewer` skill at `reviewer/` so Codex can run on-demand artifact quality reviews with subagent isolation, rubric-first findings, evidence receipts, and `PASS` / `REVISE` / `BLOCK` verdicts.

## Non-Goals

- Do not modify `idea-refine`, `interview-me`, `spec2plan`, or `plan2do`.
- Do not vendor external project code or copy long third-party prompt templates.
- Do not create executable reviewer automation beyond skill instructions and concise references.
- Do not commit git changes.

## Evidence Inspected

- Confirmed spec: `.codex/work/20260621-reviewer/spec.md`.
- Artifact contract: `spec2plan/references/artifact-contract.md`.
- Plan contract: `spec2plan/references/plan-contract.md`.
- Execution contract: `plan2do/references/execution-contract.md`.
- Review rubric: `plan2do/references/review-rubric.md`.
- Skill creation guidance: `.system/skill-creator/SKILL.md`.
- Interface metadata guidance: `.system/skill-creator/references/openai_yaml.md`.
- Existing examples: `debug-skill/agents/openai.yaml`, `edit-orchestration/agents/openai.yaml`.
- Local repo status command: `git status --short`.

## Spec Summary

Create `reviewer`, a general-purpose Codex skill for on-demand quality review of arbitrary artifacts. It must assemble a review packet, prefer an isolated reviewer subagent when available, derive a rubric before findings, produce alignment and quality verdicts, emit evidence-backed findings with revision instructions, support adversarial mode, and remain read-only during review.

## Domain Language Check

- Canonical skill name: `reviewer`.
- Canonical verdicts: `PASS`, `REVISE`, `BLOCK`.
- Required review concepts: review packet, subagent dispatch, rubric, alignment verdict, quality verdict, evidence receipts, revision instructions, recheck plan.
- Known adapters: `idea-refine`, `interview-me`, `spec2plan`, `plan2do`, `skill-creator`.
- No term conflict found between spec and local skill conventions.

## Current Context

The workspace has a confirmed `spec.md` and `manifest.yaml` under `.codex/work/20260621-reviewer/`. The `reviewer/` skill directory does not exist yet. The implementation is docs/skill metadata only and has no runtime data, schema, auth, deployment, or production impact.

## Implementation Map

- Files: `reviewer/SKILL.md` for trigger metadata and core workflow; `reviewer/agents/openai.yaml` for UI metadata; `reviewer/references/review-report-template.md` for the required report shape; `reviewer/references/review-rubrics.md` for reusable domain rubrics; `reviewer/references/subagent-dispatch.md` for isolated reviewer packet guidance; `.codex/work/20260621-reviewer/manifest.yaml` for plan lineage; `.codex/work/20260621-reviewer/artifacts/` for execution evidence.
- Symbols / APIs: skill frontmatter keys `name` and `description`; `agents/openai.yaml` keys `interface.display_name`, `interface.short_description`, `interface.default_prompt`; validator command `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`.
- Tests: `quick_validate.py` skill validation; manual artifact checks for `SKILL.md`, `agents/openai.yaml`, references, and final review report.
- Commands: `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/init_skill.py reviewer --path /data/lcq/.codex/skills --resources references --interface display_name="Reviewer" --interface short_description="Artifact quality review with isolated critique." --interface default_prompt="Use $reviewer to review an artifact against its source goals and return PASS, REVISE, or BLOCK."`; `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`; `git status --short`.
- Data / migration impact: Not applicable because only new skill documentation, references, metadata, and work artifacts are created.

## Assumptions

- The local skill root is `/data/lcq/.codex/skills`.
- The implementation can use `init_skill.py` as the generator required by `skill-creator`.
- Subagent dispatch is instructional in v1; it depends on available subagent tooling at runtime and falls back inline when unavailable.
- Review reference files are useful because the skill spans multiple artifact domains and should keep `SKILL.md` concise.

## User Inputs Needed

No user input is needed before execution because the user explicitly requested `spec2plan`, `plan2do`, implementation, and reviewer-based audit.

## Proposed Approach

Use one generated skill scaffold, replace generated placeholders with concise reviewer workflow instructions, add three direct reference files, validate the skill metadata, then use the newly created `reviewer` skill to review the implementation against the spec.

## Scenario Probes

- Pipeline artifact review: `reviewer` should load the source skill contract and review against mandatory gates.
- Code diff review: `reviewer` should prioritize correctness, regression risk, tests, security, maintainability, and reuse.
- Research idea review: `reviewer` should check problem clarity, novelty, feasibility, data, evaluation, baselines, and falsifiability.
- Subagent unavailable path: `reviewer` should state inline fallback reason and still produce the required schema.
- Adversarial path: `reviewer` should try to falsify plan commands, assumptions, handoff, and evidence before returning `PASS`.

## Dependency Graph

Task 1 -> Task 2 -> Task 3 -> Task 4 -> Task 5.

## Task Breakdown

### Task 1: Scaffold reviewer skill

- Description: Create the `reviewer/` skill scaffold with `SKILL.md`, `agents/openai.yaml`, and `references/` using the skill creator initializer.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `reviewer/SKILL.md`, `reviewer/agents/openai.yaml`, and `reviewer/references/` exist under `/data/lcq/.codex/skills`.
- Verification: Run `test -f reviewer/SKILL.md && test -f reviewer/agents/openai.yaml && test -d reviewer/references`.
- Concrete edits: Run the exact `init_skill.py reviewer --path /data/lcq/.codex/skills --resources references --interface ...` command from Implementation Map, then record scaffold output in `.codex/work/20260621-reviewer/artifacts/task1-scaffold.md`.
- Interfaces / contracts changed: New skill folder `reviewer/` becomes available for explicit skill invocation after placeholder content is replaced by following tasks.
- Test cases: Manual check that no scaffold examples are left in `reviewer/references/` after following tasks complete.
- Pre-check commands: Run `test ! -e reviewer && git status --short`.
- Post-check commands: Run `find reviewer -maxdepth 2 -type f | sort`.
- Dependencies: None.
- Files likely touched: `reviewer/SKILL.md`; `reviewer/agents/openai.yaml`; `reviewer/references/`
- Writable scope: `reviewer/SKILL.md`; `reviewer/agents/openai.yaml`; `reviewer/references/`; `.codex/work/20260621-reviewer/artifacts/task1-scaffold.md`
- Output artifact: `.codex/work/20260621-reviewer/artifacts/task1-scaffold.md`
- Estimated scope: S

### Task 2: Write core SKILL.md workflow

- Description: Replace scaffold placeholder content with concise `reviewer` instructions covering trigger metadata, packet assembly, subagent isolation, rubric-first review, verdict mapping, adapters, and read-only constraints.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `reviewer/SKILL.md` has valid YAML frontmatter with `name: reviewer`, broad quality-review trigger description, no scaffold placeholders, and direct links to each reference file.
- Verification: Run `grep -n "name: reviewer" reviewer/SKILL.md && ! grep -R "TO""DO\\|\\[TO""DO" -n reviewer/SKILL.md`.
- Concrete edits: Edit `reviewer/SKILL.md` with `apply_patch` to implement the workflow from `.codex/work/20260621-reviewer/spec.md`.
- Interfaces / contracts changed: Defines the callable skill behavior and required review output schema.
- Test cases: Manual check that the workflow states subagent default, inline fallback reason, no nested reviewer subagents, read-only mode, and `PASS` / `REVISE` / `BLOCK` verdict semantics.
- Pre-check commands: Run `sed -n '1,220p' reviewer/SKILL.md`.
- Post-check commands: Run `sed -n '1,260p' reviewer/SKILL.md`.
- Dependencies: Task 1.
- Files likely touched: `reviewer/SKILL.md`
- Writable scope: `reviewer/SKILL.md`; `.codex/work/20260621-reviewer/artifacts/task2-skill.md`
- Output artifact: `.codex/work/20260621-reviewer/artifacts/task2-skill.md`
- Estimated scope: M

### Task 3: Add reviewer reference files

- Description: Add direct reference files for report template, reusable rubrics, and subagent dispatch so `SKILL.md` stays concise while review behavior remains stable.
- Worker role: coding
- Wave: 3
- Acceptance criteria: `reviewer/references/review-report-template.md`, `reviewer/references/review-rubrics.md`, and `reviewer/references/subagent-dispatch.md` exist, are linked from `SKILL.md`, and contain no placeholder text.
- Verification: Run `test -f reviewer/references/review-report-template.md && test -f reviewer/references/review-rubrics.md && test -f reviewer/references/subagent-dispatch.md && ! grep -R "TO""DO\\|\\[TO""DO" -n reviewer/references`.
- Concrete edits: Use `apply_patch` to create concise markdown references for output schema, domain rubrics, and isolated subagent packet handling.
- Interfaces / contracts changed: Adds reusable reference contracts that `reviewer/SKILL.md` can load conditionally.
- Test cases: Manual check that references cover pipeline artifacts, code quality, research idea feasibility, docs/process, and execution-result acceptance.
- Pre-check commands: Run `find reviewer/references -maxdepth 1 -type f | sort`.
- Post-check commands: Run `find reviewer/references -maxdepth 1 -type f -maxdepth 1 | sort`.
- Dependencies: Task 2.
- Files likely touched: `reviewer/references/review-report-template.md`; `reviewer/references/review-rubrics.md`; `reviewer/references/subagent-dispatch.md`
- Writable scope: `reviewer/references/review-report-template.md`; `reviewer/references/review-rubrics.md`; `reviewer/references/subagent-dispatch.md`; `.codex/work/20260621-reviewer/artifacts/task3-references.md`
- Output artifact: `.codex/work/20260621-reviewer/artifacts/task3-references.md`
- Estimated scope: M

### Task 4: Finalize skill metadata

- Description: Ensure `reviewer/agents/openai.yaml` matches the implemented skill and supports explicit invocation.
- Worker role: coding
- Wave: 4
- Acceptance criteria: `reviewer/agents/openai.yaml` contains `display_name: "Reviewer"`, a 25-64 character short description, and a default prompt mentioning `$reviewer`.
- Verification: Run `grep -n "display_name: \"Reviewer\"" reviewer/agents/openai.yaml && grep -n "\\$reviewer" reviewer/agents/openai.yaml`.
- Concrete edits: Use `apply_patch` to update `reviewer/agents/openai.yaml` only if the generated content is stale or invalid.
- Interfaces / contracts changed: Updates user-facing skill metadata only.
- Test cases: Manual check that metadata matches `reviewer/SKILL.md` and contains quoted string values.
- Pre-check commands: Run `sed -n '1,80p' reviewer/agents/openai.yaml`.
- Post-check commands: Run `sed -n '1,80p' reviewer/agents/openai.yaml`.
- Dependencies: Task 3.
- Files likely touched: `reviewer/agents/openai.yaml`
- Writable scope: `reviewer/agents/openai.yaml`; `.codex/work/20260621-reviewer/artifacts/task4-metadata.md`
- Output artifact: `.codex/work/20260621-reviewer/artifacts/task4-metadata.md`
- Estimated scope: XS

### Task 5: Validate and review reviewer

- Description: Run skill validation, compile execution validation, and use the newly created `reviewer` skill to review the implementation against the spec.
- Worker role: review
- Wave: 5
- Acceptance criteria: `quick_validate.py` passes, `reviewer` review artifact contains exactly one top-level `Verdict: PASS` or concrete `REVISE` findings, and plan execution artifacts record commands and outcomes.
- Verification: Run `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer` and `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer`.
- Concrete edits: Write `.codex/work/20260621-reviewer/review.md` with the `reviewer` audit and `.codex/work/20260621-reviewer/artifacts/task5-validation.md` with validation outcomes.
- Interfaces / contracts changed: No runtime interface change; this task verifies the completed skill contract.
- Test cases: Review checks exact spec requirements for subagent default, rubric-first output, adapters, validation, read-only behavior, and metadata.
- Pre-check commands: Run `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`.
- Post-check commands: Run `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer`.
- Dependencies: Task 4.
- Files likely touched: `.codex/work/20260621-reviewer/review.md`; `.codex/work/20260621-reviewer/artifacts/task5-validation.md`; `.codex/work/20260621-reviewer/artifacts/final-report.md`
- Writable scope: `.codex/work/20260621-reviewer/review.md`; `.codex/work/20260621-reviewer/artifacts/task5-validation.md`; `.codex/work/20260621-reviewer/artifacts/final-report.md`
- Output artifact: `.codex/work/20260621-reviewer/review.md`
- Estimated scope: S

## Step-by-Step Plan

1. Run `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/init_skill.py reviewer --path /data/lcq/.codex/skills --resources references --interface display_name="Reviewer" --interface short_description="Artifact quality review with isolated critique." --interface default_prompt="Use $reviewer to review an artifact against its source goals and return PASS, REVISE, or BLOCK."` to create `reviewer/`.
2. Read `reviewer/SKILL.md` and replace template content with the workflow anchored to `.codex/work/20260621-reviewer/spec.md`.
3. Create `reviewer/references/review-report-template.md` with the exact report skeleton and verdict rules.
4. Create `reviewer/references/review-rubrics.md` with concise adapters for pipeline artifacts, code, research ideas, docs/process, and execution results.
5. Create `reviewer/references/subagent-dispatch.md` with packet shape, read-only constraints, no nested subagents, and fallback semantics.
6. Check `reviewer/agents/openai.yaml` and update it if it differs from the metadata required by Task 4.
7. Run `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`.
8. Use `reviewer` to review `reviewer/SKILL.md`, `reviewer/references/`, `reviewer/agents/openai.yaml`, and `.codex/work/20260621-reviewer/spec.md`, saving `.codex/work/20260621-reviewer/review.md`.
9. Run `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer`.

## Parallelization

No implementation tasks are parallelized because all tasks depend on the generated `reviewer/` scaffold or write review artifacts in the same topic workspace. Sequential waves avoid overlapping writable scope.

## Files / Components Likely Affected

- `reviewer/SKILL.md`
- `reviewer/agents/openai.yaml`
- `reviewer/references/review-report-template.md`
- `reviewer/references/review-rubrics.md`
- `reviewer/references/subagent-dispatch.md`
- `.codex/work/20260621-reviewer/manifest.yaml`
- `.codex/work/20260621-reviewer/plan.md`
- `.codex/work/20260621-reviewer/execution/tasks.json`
- `.codex/work/20260621-reviewer/review.md`
- `.codex/work/20260621-reviewer/artifacts/*.md`

## Owners / Responsibilities

- Primary agent: create the plan, execute tasks, preserve user work, run validation, and report final status.
- `reviewer` skill: perform the final artifact quality review after the skill exists.
- User: no action during execution unless validation or review surfaces a blocking product decision.

## Validation Plan

- Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer/plan.md --mode light` before execution.
- Run `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer/plan.md` before task execution.
- Run `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer` after implementation.
- Run `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer` before final success.
- Manual review: inspect `.codex/work/20260621-reviewer/review.md` for a standalone `Verdict: PASS` or concrete revision findings.

## Rollout Plan

No deployment rollout is needed. The skill becomes available locally when `reviewer/SKILL.md` and `reviewer/agents/openai.yaml` exist under `/data/lcq/.codex/skills`.

## Monitoring / Observability

Use local verification artifacts under `.codex/work/20260621-reviewer/artifacts/`, `quick_validate.py` output, `validate_execution.py` output, and `.codex/work/20260621-reviewer/review.md` as observability evidence.

## Documentation / ADR Updates

ADR: Not needed. The change adds one local skill and its reference docs without changing shared architecture, APIs, runtime behavior, or policy defaults.

## Rollback / Recovery Plan

If implementation fails before final acceptance, remove only files created by this plan under `reviewer/` and `.codex/work/20260621-reviewer/execution/` after confirming no user edits exist in those paths. If validation fails, patch the smallest failing file and rerun the failing command before broader checks.

## Abort Criteria

- Abort if `reviewer/` already exists with user-authored content before Task 1.
- Abort if `quick_validate.py` reports a structural issue that cannot be fixed without changing the confirmed spec.
- Abort if the final `reviewer` audit returns `BLOCK`.
- Abort if git status shows unrelated user edits inside `reviewer/` during execution.

## Risks

- The skill can become too broad and vague; mitigate with rubric-first review, explicit output schema, and direct reference routing.
- Subagent behavior is tool-dependent; mitigate with explicit fallback reason and instruction-only v1 contract.
- Review findings can become subjective; mitigate with evidence receipts and separate alignment and quality verdicts.
- Overlong `SKILL.md` can waste context; mitigate by moving reusable detail into the three reference files.

## Open Questions

No open questions block implementation. Future v2 decisions about mandatory hooks into the four upstream skills remain outside this plan.

## Plan Self-Review

- Writable scope: every task has exact writable scope; same-wave tasks do not overlap because waves are sequential.
- Coverage: behavior is covered by `quick_validate.py`, manual schema checks, `reviewer` self-review, and `validate_execution.py`.
- Unknown: runtime subagent availability remains an assumption and is handled by inline fallback semantics.
- Rollback: rollback is limited to new `reviewer/` files and generated execution artifacts after checking for user edits.
- Task 1: a fresh agent can execute Task 1 from the exact `init_skill.py` command and writable scope above.

## Execution Decision

Proceed with primary-agent `plan2do` execution because the user explicitly requested implementation, the plan touches only new local skill files and work artifacts, and rollback is straightforward.

## Execution Handoff

- Goal: Implement local `reviewer` skill from `.codex/work/20260621-reviewer/spec.md`.
- Current state: Confirmed spec exists; `reviewer/` skill directory is not yet implemented.
- Authoritative artifacts: `.codex/work/20260621-reviewer/spec.md`; `.codex/work/20260621-reviewer/plan.md`; `.codex/work/20260621-reviewer/manifest.yaml`.
- Decisions: Use light plan mode, primary-agent execution, generated scaffold, three concise references, one final `reviewer` audit.
- Verification: Plan validator, execution compiler, skill quick validator, execution validator, and saved `reviewer` review.
- Remaining risks: Subagent tooling availability is runtime-dependent; inline fallback is allowed with explicit reason.
- Next action: Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer/plan.md --mode light`.
- Suggested skills: `plan2do`, `context-engineering`, `edit-orchestration`, `skill-creator`, `reviewer`.
- Redactions / omitted raw data: External project raw docs and long validator internals are omitted from active context; paths and command names are retained.
