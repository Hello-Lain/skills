# debug-skill Implementation Plan

Mode: light
Risk level: Low
Confidence: High

## Goal
Create `/data/lcq/.codex/skills/debug-skill` from the confirmed spec at `.codex/work/20260621-debug-skill/spec.md`, then validate and execute the plan through `plan2do`.

## Non-Goals
- Do not auto-modify audited skills from `debug-skill` v1.
- Do not require `dspy`, `gepa`, `openai`, or Hermes runtime installation.
- Do not read private session history by default.
- Do not implement Hermes automatic PR/deploy flow.
- Do not change unrelated dirty files in `/data/lcq/.codex/skills`.

## Evidence Inspected
- `.codex/work/20260621-debug-skill/spec.md`
- `.codex/work/20260621-debug-skill/manifest.yaml`
- `/data/lcq/.codex/skills/spec2plan/SKILL.md`
- `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- `/data/lcq/.codex/skills/plan2do/SKILL.md`
- `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- `/data/lcq/.codex/skills/plan2do/references/review-rubric.md`
- `/data/lcq/.codex/skills/.system/skill-creator/SKILL.md`
- `/data/lcq/.codex/skills/edit-orchestration/SKILL.md`
- `/tmp/hermes-agent-self-evolution/README.md`
- `/tmp/hermes-agent-self-evolution/PLAN.md`
- `/tmp/hermes-agent-self-evolution/evolution/core/dataset_builder.py`
- `/tmp/hermes-agent-self-evolution/evolution/core/fitness.py`
- `/tmp/hermes-agent-self-evolution/evolution/core/constraints.py`
- `/tmp/hermes-agent-self-evolution/evolution/core/external_importers.py`
- `/tmp/hermes-agent-self-evolution/evolution/skills/skill_module.py`
- `/tmp/hermes-agent-self-evolution/evolution/skills/evolve_skill.py`
- `/tmp/hermes-agent-self-evolution/tests/core/test_constraints.py`
- `/tmp/hermes-agent-self-evolution/tests/skills/test_skill_module.py`

## Spec Summary
`debug-skill` audits the real execution trace of a specified Codex skill, judges net effect on task quality and efficiency, performs defect-tied GitHub reuse research, and produces Hermes-inspired candidate improvements without applying patches by default.

## Domain Language Check
- Use `skill audit`, `execution trace`, `experience record`, `defect taxonomy`, `fitness score`, `candidate improvement`, `promotion gate`, and `reuse search`.
- Preserve Codex skill terms: `SKILL.md`, `references/`, `scripts/`, `agents/openai.yaml`, `quick_validate.py`.
- Preserve Hermes source terms only for provenance: `EvalExample`, `EvalDataset`, `ConstraintResult`, `FitnessScore`, `load_skill`, `find_skill`, `reassemble_skill`.

## Current Context
`debug-skill/` does not exist. The topic workspace exists at `.codex/work/20260621-debug-skill/` with a confirmed `spec.md` and `manifest.yaml`. The git worktree contains unrelated modified and untracked files; this plan only writes the new `debug-skill/` skill and the current topic workspace.

## Implementation Map
- Files: `debug-skill/SKILL.md`, `debug-skill/agents/openai.yaml`, `debug-skill/scripts/skill_audit_core.py`, `debug-skill/references/hermes-reuse.md`, `debug-skill/references/report-template.md`, `.codex/work/20260621-debug-skill/manifest.yaml`, `.codex/work/20260621-debug-skill/plan.md`, `.codex/work/20260621-debug-skill/artifacts/`
- Symbols / APIs: `SkillInfo`, `SkillAuditExample`, `SkillAuditDataset`, `ConstraintResult`, `FitnessScore`, `CandidateScore`, `find_skill`, `load_skill`, `reassemble_skill`, `validate_skill_text`, `score_candidate`, `redact_text`, `build_report_skeleton`
- Tests: `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/debug-skill`, `python3 -m py_compile /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py`, `python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --self-test`
- Commands: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill/plan.md --mode light`, `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill/plan.md`, `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill`
- Data / migration impact: Not applicable; no data store, schema, auth, release, or migration surface is touched.

## Assumptions
- `/tmp/hermes-agent-self-evolution` remains readable during execution; if absent, clone `https://github.com/NousResearch/hermes-agent-self-evolution.git` into `/tmp/hermes-agent-self-evolution` before Task 2.
- `debug-skill` v1 can be a workflow skill plus one deterministic helper script; no required runtime dependency on Hermes packages is needed.
- The audit report defaults to user-facing output; saved audit artifacts are produced when the user or future task asks for saved reports.
- Candidate fitness scores use a 0.00-1.00 numeric scale because it is compact and testable.

## User Inputs Needed
No input needed before execution. The user already confirmed the spec and asked to plan then execute.

## Proposed Approach
Create the skill with the official `skill-creator` scaffold path, then implement a concise `SKILL.md`, a Hermes reuse reference, a report template reference, and a deterministic helper script that adapts Hermes parser/data/constraint/fitness concepts without importing Hermes. Validate the skill, run the helper self-test, perform a sample report-skeleton check, review for scope and over-engineering, and save execution artifacts.

## Scenario Probes
- Audit `context-engineering` with current trace evidence: the report should allow a `net-positive` verdict and identify over-heavy default behavior as a defect.
- Audit a skill with missing trace evidence: the report should allow `inconclusive` and list missing evidence.
- Audit a concrete defect: the workflow should require GitHub/source reuse search before recommending custom changes.
- Run helper script without `dspy` or Hermes installed: self-test should pass.

## Dependency Graph
Task 1 -> Task 2 -> Task 3 -> Task 4 -> Task 5

Task 1 scaffolds the skill directory. Task 2 documents Hermes reuse and implements the helper core. Task 3 writes skill workflow and UI metadata. Task 4 validates behavior and records evidence. Task 5 performs review and final reporting.

## Task Breakdown

### Task 1: Scaffold skill and workspace artifacts

- Description: Create `debug-skill/` with the official skill scaffold, then create the plan artifacts directory.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `debug-skill/SKILL.md` exists; `debug-skill/agents/openai.yaml` exists; `.codex/work/20260621-debug-skill/artifacts/` exists; task artifact records scaffold command and output summary.
- Verification: `test -f /data/lcq/.codex/skills/debug-skill/SKILL.md && test -f /data/lcq/.codex/skills/debug-skill/agents/openai.yaml && test -d /data/lcq/.codex/skills/.codex/work/20260621-debug-skill/artifacts`
- Concrete edits: Run `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/init_skill.py debug-skill --path /data/lcq/.codex/skills --resources scripts,references --interface display_name="Debug Skill" --interface short_description="Audit real skill execution quality" --interface default_prompt="Use $debug-skill to audit a Codex skill execution trace and recommend evidence-backed improvements."`; create `.codex/work/20260621-debug-skill/artifacts/task1-execution.md`.
- Interfaces / contracts changed: New Codex skill directory `debug-skill/` is introduced.
- Test cases: Scaffold command completes; files exist at exact paths.
- Pre-check commands: `test ! -e /data/lcq/.codex/skills/debug-skill`
- Post-check commands: `test -f /data/lcq/.codex/skills/debug-skill/SKILL.md && test -f /data/lcq/.codex/skills/debug-skill/agents/openai.yaml`
- Dependencies: None.
- Files likely touched: `debug-skill/SKILL.md`; `debug-skill/agents/openai.yaml`; `.codex/work/20260621-debug-skill/artifacts/task1-execution.md`
- Writable scope: `debug-skill/`; `.codex/work/20260621-debug-skill/artifacts/task1-execution.md`
- Output artifact: `.codex/work/20260621-debug-skill/artifacts/task1-execution.md`
- Estimated scope: S

### Task 2: Implement Hermes adapter core and reuse reference

- Description: Implement a deterministic helper script adapting Hermes parser, data, constraint, fitness, and redaction patterns; document the exact Hermes source mapping.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `debug-skill/scripts/skill_audit_core.py` has self-testable parser/data/constraint/fitness helpers; `debug-skill/references/hermes-reuse.md` maps Hermes files to Codex adaptations and rejected components; task artifact records copied/adapted provenance.
- Verification: `python3 -m py_compile /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py && python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --self-test`
- Concrete edits: Write `debug-skill/scripts/skill_audit_core.py` and `debug-skill/references/hermes-reuse.md`; include MIT upstream attribution comments for adapted Hermes concepts.
- Interfaces / contracts changed: Helper CLI provides `--self-test`, `--skill <name-or-path>`, `--json`, and `--report-skeleton <skill>`.
- Test cases: Parse a temporary skill; validate missing frontmatter failure; redact secret-like text; compute candidate score; build report skeleton.
- Pre-check commands: `test -d /tmp/hermes-agent-self-evolution || git clone --depth=1 https://github.com/NousResearch/hermes-agent-self-evolution.git /tmp/hermes-agent-self-evolution`
- Post-check commands: `python3 -m py_compile /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py && python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --self-test`
- Dependencies: Task 1.
- Files likely touched: `debug-skill/scripts/skill_audit_core.py`; `debug-skill/references/hermes-reuse.md`; `.codex/work/20260621-debug-skill/artifacts/task2-execution.md`
- Writable scope: `debug-skill/scripts/skill_audit_core.py`; `debug-skill/references/hermes-reuse.md`; `.codex/work/20260621-debug-skill/artifacts/task2-execution.md`
- Output artifact: `.codex/work/20260621-debug-skill/artifacts/task2-execution.md`
- Estimated scope: M

### Task 3: Author debug-skill workflow and report template

- Description: Replace scaffold text with a concise skill workflow, add a report template reference, and update `agents/openai.yaml` to match the final behavior.
- Worker role: coding
- Wave: 3
- Acceptance criteria: `debug-skill/SKILL.md` frontmatter triggers skill audits; body instructs evidence inventory, execution trace reconstruction, scoring, reuse search, Hermes candidate generation, and no auto-apply default; `debug-skill/references/report-template.md` contains the fixed report format; `debug-skill/agents/openai.yaml` reflects the skill.
- Verification: `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/debug-skill`
- Concrete edits: Replace `debug-skill/SKILL.md`; write `debug-skill/references/report-template.md`; regenerate or edit `debug-skill/agents/openai.yaml`.
- Interfaces / contracts changed: `debug-skill` becomes discoverable through its `name`, `description`, and UI metadata.
- Test cases: Skill validator passes; `SKILL.md` names direct references; default behavior forbids automatic patch application.
- Pre-check commands: `test -f /data/lcq/.codex/skills/debug-skill/SKILL.md && test -f /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py`
- Post-check commands: `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/debug-skill`
- Dependencies: Task 2.
- Files likely touched: `debug-skill/SKILL.md`; `debug-skill/references/report-template.md`; `debug-skill/agents/openai.yaml`; `.codex/work/20260621-debug-skill/artifacts/task3-execution.md`
- Writable scope: `debug-skill/SKILL.md`; `debug-skill/references/report-template.md`; `debug-skill/agents/openai.yaml`; `.codex/work/20260621-debug-skill/artifacts/task3-execution.md`
- Output artifact: `.codex/work/20260621-debug-skill/artifacts/task3-execution.md`
- Estimated scope: M

### Task 4: Validate implementation against spec acceptance checks

- Description: Run skill validation, helper self-test, report skeleton generation, and artifact checks; update execution checklist evidence.
- Worker role: coding
- Wave: 4
- Acceptance criteria: Validation commands pass; a report skeleton for `context-engineering` can be generated without Hermes runtime; task artifact records command outcomes.
- Verification: `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/debug-skill && python3 -m py_compile /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py && python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --self-test && python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --report-skeleton context-engineering`
- Concrete edits: Write `.codex/work/20260621-debug-skill/artifacts/task4-verification.md` with exact commands and summaries.
- Interfaces / contracts changed: No command; manual check confirms no interface change beyond Task 3.
- Test cases: `quick_validate.py`; `py_compile`; `--self-test`; `--report-skeleton context-engineering`.
- Pre-check commands: `test -f /data/lcq/.codex/skills/debug-skill/references/report-template.md && test -f /data/lcq/.codex/skills/debug-skill/references/hermes-reuse.md`
- Post-check commands: `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/debug-skill && python3 -m py_compile /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py && python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --self-test && python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --report-skeleton context-engineering`
- Dependencies: Task 3.
- Files likely touched: `.codex/work/20260621-debug-skill/artifacts/task4-verification.md`
- Writable scope: `.codex/work/20260621-debug-skill/artifacts/task4-verification.md`
- Output artifact: `.codex/work/20260621-debug-skill/artifacts/task4-verification.md`
- Estimated scope: S

### Task 5: Review, finalize artifacts, and validate execution

- Description: Review changed files for functional completeness, scope discipline, architecture simplicity, and spec coverage; write final artifacts.
- Worker role: review
- Wave: 5
- Acceptance criteria: `.codex/work/20260621-debug-skill/artifacts/review.md` contains `Verdict: PASS`; `.codex/work/20260621-debug-skill/artifacts/final-report.md` records mode, status, files, commands, review, and risks; `validate_execution.py` passes after compiled tasks are complete.
- Verification: `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill`
- Concrete edits: Write `.codex/work/20260621-debug-skill/artifacts/review.md` and `.codex/work/20260621-debug-skill/artifacts/final-report.md`; update `.codex/work/20260621-debug-skill/execution/tasks.json` statuses through the plan2do flow.
- Interfaces / contracts changed: No command; review confirms final skill surfaces from Tasks 2 and 3.
- Test cases: Review rubric PASS conditions; execution validator.
- Pre-check commands: `test -f /data/lcq/.codex/skills/.codex/work/20260621-debug-skill/artifacts/task4-verification.md`
- Post-check commands: `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill`
- Dependencies: Task 4.
- Files likely touched: `.codex/work/20260621-debug-skill/artifacts/review.md`; `.codex/work/20260621-debug-skill/artifacts/final-report.md`; `.codex/work/20260621-debug-skill/execution/tasks.json`
- Writable scope: `.codex/work/20260621-debug-skill/artifacts/review.md`; `.codex/work/20260621-debug-skill/artifacts/final-report.md`; `.codex/work/20260621-debug-skill/execution/tasks.json`
- Output artifact: `.codex/work/20260621-debug-skill/artifacts/final-report.md`
- Estimated scope: S

## Step-by-Step Plan
1. Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill/plan.md --mode light`.
2. Run `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill/plan.md`.
3. Run `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/init_skill.py debug-skill --path /data/lcq/.codex/skills --resources scripts,references --interface display_name="Debug Skill" --interface short_description="Audit real skill execution quality" --interface default_prompt="Use $debug-skill to audit a Codex skill execution trace and recommend evidence-backed improvements."`.
4. Create `.codex/work/20260621-debug-skill/artifacts/task1-execution.md`.
5. Write `debug-skill/scripts/skill_audit_core.py` with `SkillInfo`, `SkillAuditExample`, `SkillAuditDataset`, `ConstraintResult`, `FitnessScore`, `CandidateScore`, `find_skill`, `load_skill`, `reassemble_skill`, `validate_skill_text`, `score_candidate`, `redact_text`, and `build_report_skeleton`.
6. Write `debug-skill/references/hermes-reuse.md` mapping `/tmp/hermes-agent-self-evolution/evolution/core/dataset_builder.py`, `/tmp/hermes-agent-self-evolution/evolution/core/fitness.py`, `/tmp/hermes-agent-self-evolution/evolution/core/constraints.py`, `/tmp/hermes-agent-self-evolution/evolution/core/external_importers.py`, `/tmp/hermes-agent-self-evolution/evolution/skills/skill_module.py`, and `/tmp/hermes-agent-self-evolution/evolution/skills/evolve_skill.py`.
7. Run `python3 -m py_compile /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py`.
8. Run `python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --self-test`.
9. Write `debug-skill/SKILL.md` with workflow steps and reference routing.
10. Write `debug-skill/references/report-template.md`.
11. Update `debug-skill/agents/openai.yaml`.
12. Run `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/debug-skill`.
13. Run `python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --report-skeleton context-engineering`.
14. Write `.codex/work/20260621-debug-skill/artifacts/review.md` with `Verdict: PASS` or `Verdict: FAIL`.
15. Write `.codex/work/20260621-debug-skill/artifacts/final-report.md`.
16. Run `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill`.

## Parallelization
No parallel implementation waves are planned. Tasks are sequential because Task 2 writes helper APIs consumed by Task 3, Task 4 validates Task 3 output, and Task 5 reviews all prior artifacts. Same-wave write overlap does not occur.

## Files / Components Likely Affected
- `debug-skill/SKILL.md`
- `debug-skill/agents/openai.yaml`
- `debug-skill/scripts/skill_audit_core.py`
- `debug-skill/references/hermes-reuse.md`
- `debug-skill/references/report-template.md`
- `.codex/work/20260621-debug-skill/manifest.yaml`
- `.codex/work/20260621-debug-skill/plan.md`
- `.codex/work/20260621-debug-skill/execution/tasks.json`
- `.codex/work/20260621-debug-skill/artifacts/task1-execution.md`
- `.codex/work/20260621-debug-skill/artifacts/task2-execution.md`
- `.codex/work/20260621-debug-skill/artifacts/task3-execution.md`
- `.codex/work/20260621-debug-skill/artifacts/task4-verification.md`
- `.codex/work/20260621-debug-skill/artifacts/review.md`
- `.codex/work/20260621-debug-skill/artifacts/final-report.md`

## Owners / Responsibilities
- Main agent: plan generation, implementation, verification, review, final report.
- `skill-creator`: skill scaffold and validation standards.
- `edit-orchestration`: manual edit safety and diff review.
- `context-engineering`: focused context and final rehydration.
- `plan2do`: task execution checklist, review, and final execution validation.

## Validation Plan
- Validate plan: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill/plan.md --mode light`
- Compile execution: `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill/plan.md`
- Validate skill: `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/debug-skill`
- Compile helper: `python3 -m py_compile /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py`
- Self-test helper: `python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --self-test`
- Smoke helper: `python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --report-skeleton context-engineering`
- Validate execution: `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill`

## Rollout Plan
Local-only rollout. The new skill becomes available from `/data/lcq/.codex/skills/debug-skill` after validation passes. No deployment, release, package publish, or git commit is part of this plan.

## Monitoring / Observability
Not applicable for runtime monitoring; this is a local Codex skill. Observability is via validation command output, task artifacts, review verdict, and final report under `.codex/work/20260621-debug-skill/artifacts/`.

## Documentation / ADR Updates
ADR: Not needed

Documentation changes are contained in `debug-skill/SKILL.md`, `debug-skill/references/hermes-reuse.md`, `debug-skill/references/report-template.md`, and `.codex/work/20260621-debug-skill/artifacts/final-report.md`.

## Rollback / Recovery Plan
- If scaffold generation fails, remove only the incomplete `debug-skill/` directory after confirming it was created by this execution, then rerun Task 1.
- If helper validation fails, patch only `debug-skill/scripts/skill_audit_core.py` and rerun `python3 -m py_compile /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py && python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --self-test`.
- If skill validation fails, patch `debug-skill/SKILL.md` or `debug-skill/agents/openai.yaml` and rerun `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/debug-skill`.
- If review fails, write `.codex/work/20260621-debug-skill/artifacts/rework-guidance.md`, perform one scoped fix, and rerun the failed check.
- To roll back after completion, delete only `debug-skill/` and `.codex/work/20260621-debug-skill/execution/` plus generated task artifacts from this execution; preserve `spec.md`, `plan.md`, and `manifest.yaml` unless the user requests removal.

## Abort Criteria
- Abort if `debug-skill/` already exists with user work before Task 1.
- Abort if `init_skill.py` fails and leaves an ambiguous partial skill directory.
- Abort if a required validation command fails twice with the same error after scoped rework.
- Abort if the plan would require reading private history without explicit user approval.
- Abort if implementation requires mandatory `dspy`, `gepa`, `openai`, or Hermes runtime dependency.

## Risks
- Helper script could over-engineer a workflow skill; mitigate by limiting it to parser/data/constraint/fitness helpers.
- GitHub reuse could become cargo-culting; mitigate by documenting each adapted or rejected Hermes component in `debug-skill/references/hermes-reuse.md`.
- Skill may be too verbose; mitigate by moving detail to references and keeping `SKILL.md` procedural.
- Current conversation evidence cannot be programmatically accessed by the helper; mitigate by making trace ingestion a workflow step rather than a false automated claim.

## Open Questions
No blocker questions remain for v1 execution.

## Plan Self-Review
- Every task has exact writable scope and same-wave writes do not overlap.
- Behavior change coverage is present through `quick_validate.py`, `py_compile`, `--self-test`, and `--report-skeleton context-engineering`.
- Every unknown is listed under `Assumptions` or `Open Questions`.
- Rollback and abort criteria are specific for this low-risk local skill addition.
- A fresh agent can execute Task 1 using the exact `init_skill.py` command without raw transcript context.

## Execution Decision
Proceed with primary-agent `plan2do` execution after this plan passes `validate_plan_contract.py --mode light`.

## Execution Handoff

- Goal: Create and validate `/data/lcq/.codex/skills/debug-skill`.
- Current state: Confirmed spec exists at `.codex/work/20260621-debug-skill/spec.md`; `debug-skill/` is absent before execution.
- Authoritative artifacts: `.codex/work/20260621-debug-skill/spec.md`; `.codex/work/20260621-debug-skill/plan.md`; `/tmp/hermes-agent-self-evolution/README.md`; `/tmp/hermes-agent-self-evolution/PLAN.md`; `/tmp/hermes-agent-self-evolution/evolution/core/dataset_builder.py`; `/tmp/hermes-agent-self-evolution/evolution/core/fitness.py`; `/tmp/hermes-agent-self-evolution/evolution/core/constraints.py`; `/tmp/hermes-agent-self-evolution/evolution/core/external_importers.py`; `/tmp/hermes-agent-self-evolution/evolution/skills/skill_module.py`; `/tmp/hermes-agent-self-evolution/evolution/skills/evolve_skill.py`
- Decisions: Use light mode; create workflow skill plus helper script; adapt Hermes components without mandatory Hermes runtime; default to no auto-apply.
- Verification: Run plan validation, execution compilation, skill validation, helper compilation, helper self-test, report skeleton smoke, review PASS, and execution validation.
- Remaining risks: Helper may be broader than the workflow needs; keep it limited to deterministic primitives.
- Next action: Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill/plan.md --mode light`.
- Suggested skills: `plan2do`, `context-engineering`, `skill-creator`, `edit-orchestration`.
- Redactions / omitted raw data: Raw git status and full Hermes source are omitted from the plan body; paths are cited instead.
