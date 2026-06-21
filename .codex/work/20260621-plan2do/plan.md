# Plan: Build plan2do Skill

Mode: light
Risk level: Medium
Confidence: High

## Goal
Create `/data/lcq/.codex/skills/plan2do` as a local Codex skill that executes `spec2plan` plans with default primary-agent execution, explicit `codex2codex` compatibility, quality review, primary-agent rework guidance, and `context-engineering` context governance.

## Non-Goals
- Do not implement plan execution during this planning step.
- Do not rewrite upstream `spec.md` or `plan.md` artifacts.
- Do not change existing `spec2plan`, `codex2codex`, or `context-engineering` behavior.
- Do not perform production deployment, destructive git operations, or user-work rollback.

## Evidence Inspected
- `.codex/work/20260621-plan2do/spec.md`
- `interview-me/SKILL.md`
- `interview-me/references/spec-quality-rubric.md`
- `references/artifact-contract.md`
- `spec2plan/SKILL.md`
- `spec2plan/references/plan-contract.md`
- `spec2plan/scripts/validate_plan_contract.py`
- `.system/skill-creator/SKILL.md`
- `.system/skill-creator/references/openai_yaml.md`
- `.system/skill-creator/scripts/init_skill.py`
- `context-engineering/SKILL.md`
- `codex2codex/SKILL.md`
- `apply-patch/SKILL.md`

## Spec Summary
The confirmed spec requires a new `plan2do` skill. It must consume `spec2plan` `plan.md` files, default to primary-agent execution, support explicit `codex2codex`, enforce quality gates, require primary-agent rework guidance before fixes, store large evidence under artifacts, and use `context-engineering` to keep active context clean.

## Domain Language Check
- Use `plan.md`, `Task Breakdown`, `Wave`, `Writable scope`, `Verification`, and `Output artifact` consistently with `spec2plan`.
- Use `focused context pack`, `quarantine`, `rehydration`, `decision packet`, and `context capsule` consistently with `context-engineering`.
- Use `run_plan.py`, `review PASS`, `fix wave`, and `validate_execution_complete.py` consistently with `codex2codex`.
- Use `SKILL.md`, `description`, `agents/openai.yaml`, and `quick_validate.py` consistently with `skill-creator`.

## Current Context
The workspace is `/data/lcq/.codex/skills`. There are unrelated dirty files in `skill-tokenless/*` and `git-workflow-and-versioning/*`, plus earlier `spec2plan/*` edits. The `plan2do` skill folder does not exist, so implementation can create it without overwriting user work.

## Implementation Map
- Files: `/data/lcq/.codex/skills/plan2do/SKILL.md` for the skill workflow; `/data/lcq/.codex/skills/plan2do/agents/openai.yaml` for UI metadata; `/data/lcq/.codex/skills/plan2do/references/execution-contract.md` for detailed execution and report contracts.
- Symbols / APIs: YAML frontmatter keys `name` and `description`; `quick_validate.py`; `context-engineering` focused context pack, rehydration, decision packet, context capsule; `codex2codex/scripts/run_plan.py`; `codex2codex/scripts/validate_execution_complete.py`.
- Tests: `/data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`; manual review against `.codex/work/20260621-plan2do/spec.md`; grep checks for required mode and quality terms.
- Commands: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`; `rg "primary-agent|codex2codex|Context Capsule|rework guidance|Verdict" /data/lcq/.codex/skills/plan2do`.
- Data / migration impact: Not applicable because the implementation creates a new skill folder and planning artifacts only.

## Assumptions
- A default maximum of two fix cycles per failed task or review scope is acceptable unless the user later changes it.
- A reference file is justified because the execution contract is detailed and should not bloat `SKILL.md`.
- `plan2do` should not include executable scripts in v1 unless implementation discovers repeated deterministic parsing that belongs in a script.

## User Inputs Needed
None before implementation. The only unconfirmed tuning value is the rework cycle limit, and the plan records a safe default assumption.

## Proposed Approach
Create a concise workflow skill with progressive disclosure. Keep `SKILL.md` focused on triggers, mode choice, workflow, quality gates, and context hygiene. Put detailed execution/report contracts in `references/execution-contract.md`. Add `agents/openai.yaml`. Validate with `quick_validate.py`, targeted grep checks, and manual acceptance against the confirmed spec.

## Scenario Probes
- Primary-agent default: user says `用 plan2do 执行 .codex/work/x/plan.md`; skill must keep execution in the main agent and use artifacts to avoid context bloat.
- Explicit multi-agent: user says `用 codex2codex 执行这个 plan`; skill must route through `codex2codex` and still own final quality acceptance.
- Review failure: verification passes but review finds incomplete functionality or over-engineered design; skill must require primary-agent rework guidance and fix cycle.
- Repeated failure: the same issue fails after bounded fixes; skill must stop with blocker report and avoid false completion.
- Risky action: plan includes destructive, production, schema, or public API work; skill must rehydrate evidence and use a decision packet before acting.

## Dependency Graph
- Task 1 creates the skill skeleton and metadata.
- Task 2 depends on Task 1 and writes the execution contract reference.
- Task 3 depends on Tasks 1 and 2 and fills `SKILL.md` with workflow links to the reference.
- Task 4 depends on Tasks 1 through 3 and validates the skill.
- Task 5 depends on Task 4 and performs independent review.
- Task 6 depends on Task 5 only if review fails or finds quality gaps.

## Task Breakdown
### Task 1: Create plan2do skill skeleton

- Description: Create the new `plan2do` skill directory with required metadata files.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `/data/lcq/.codex/skills/plan2do/SKILL.md` exists with `name: plan2do`; `/data/lcq/.codex/skills/plan2do/agents/openai.yaml` exists; no existing skill files are overwritten.
- Verification: `test -f /data/lcq/.codex/skills/plan2do/SKILL.md && test -f /data/lcq/.codex/skills/plan2do/agents/openai.yaml`
- Concrete edits: Add `/data/lcq/.codex/skills/plan2do/SKILL.md` and `/data/lcq/.codex/skills/plan2do/agents/openai.yaml` using either `init_skill.py` or `apply_patch`.
- Interfaces / contracts changed: New discoverable skill name `plan2do` and UI metadata for `$plan2do`.
- Test cases: File existence check and YAML frontmatter review.
- Pre-check commands: `test ! -e /data/lcq/.codex/skills/plan2do`
- Post-check commands: `test -f /data/lcq/.codex/skills/plan2do/SKILL.md && test -f /data/lcq/.codex/skills/plan2do/agents/openai.yaml`
- Dependencies: None.
- Files likely touched: `/data/lcq/.codex/skills/plan2do/SKILL.md`; `/data/lcq/.codex/skills/plan2do/agents/openai.yaml`
- Writable scope: `/data/lcq/.codex/skills/plan2do/`
- Output artifact: `.codex/work/20260621-plan2do/artifacts/task1-skeleton.md`
- Estimated scope: S

### Task 2: Define execution contract reference

- Description: Write the detailed plan intake, execution modes, quality gates, rework loop, artifact layout, final report, and failure policy into a reference file.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `/data/lcq/.codex/skills/plan2do/references/execution-contract.md` defines primary-agent mode, explicit `codex2codex` mode, review gates, rework guidance, context artifact quarantine, and final report fields.
- Verification: `rg "Primary-agent|codex2codex|rework guidance|Context Capsule|Final report|Blocker" /data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- Concrete edits: Add `/data/lcq/.codex/skills/plan2do/references/execution-contract.md` with sections for intake, modes, gates, artifacts, rework, and reporting.
- Interfaces / contracts changed: New internal reference contract for `plan2do` behavior.
- Test cases: Grep confirms required contract headings and terms.
- Pre-check commands: `test -f /data/lcq/.codex/skills/plan2do/SKILL.md`
- Post-check commands: `rg "Primary-agent|codex2codex|rework guidance|Context Capsule|Final report|Blocker" /data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- Dependencies: Task 1.
- Files likely touched: `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- Writable scope: `/data/lcq/.codex/skills/plan2do/references/`
- Output artifact: `.codex/work/20260621-plan2do/artifacts/task2-execution-contract.md`
- Estimated scope: S

### Task 3: Implement SKILL.md workflow

- Description: Replace skeleton text with concise `plan2do` instructions that load `context-engineering`, choose execution mode, execute plan tasks, run review, guide rework, and report completion.
- Worker role: coding
- Wave: 3
- Acceptance criteria: `SKILL.md` frontmatter has a trigger-rich `description`; body states default primary-agent mode; body states explicit `codex2codex` mode; body requires `context-engineering`; body links to `references/execution-contract.md`; body prohibits false completion after failed review or verification.
- Verification: `rg "default.*primary|codex2codex|context-engineering|execution-contract|rework guidance|false completion" /data/lcq/.codex/skills/plan2do/SKILL.md`
- Concrete edits: Update `/data/lcq/.codex/skills/plan2do/SKILL.md` sections: Overview, Resources, Intake, Mode Selection, Context Governance, Execution Loop, Quality Gates, Rework, Completion Report.
- Interfaces / contracts changed: Skill trigger description and required runtime workflow for `$plan2do`.
- Test cases: Grep confirms required workflow terms; manual read confirms concise progressive disclosure.
- Pre-check commands: `test -f /data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- Post-check commands: `rg "default.*primary|codex2codex|context-engineering|execution-contract|rework guidance|false completion" /data/lcq/.codex/skills/plan2do/SKILL.md`
- Dependencies: Tasks 1 and 2.
- Files likely touched: `/data/lcq/.codex/skills/plan2do/SKILL.md`
- Writable scope: `/data/lcq/.codex/skills/plan2do/SKILL.md`
- Output artifact: `.codex/work/20260621-plan2do/artifacts/task3-skill-workflow.md`
- Estimated scope: M

### Task 4: Validate skill structure and trigger metadata

- Description: Run skill validation and inspect `agents/openai.yaml` against `SKILL.md`.
- Worker role: coding
- Wave: 4
- Acceptance criteria: `quick_validate.py` returns success; `agents/openai.yaml` includes display name, short description, and default prompt mentioning `$plan2do`; validation findings are recorded.
- Verification: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`
- Concrete edits: Fix `/data/lcq/.codex/skills/plan2do/SKILL.md` or `/data/lcq/.codex/skills/plan2do/agents/openai.yaml` only if validation fails or metadata mismatches.
- Interfaces / contracts changed: None beyond finalized metadata.
- Test cases: `quick_validate.py` success and manual metadata check.
- Pre-check commands: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`
- Post-check commands: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`
- Dependencies: Task 3.
- Files likely touched: `/data/lcq/.codex/skills/plan2do/SKILL.md`; `/data/lcq/.codex/skills/plan2do/agents/openai.yaml`
- Writable scope: `/data/lcq/.codex/skills/plan2do/`
- Output artifact: `.codex/work/20260621-plan2do/artifacts/task4-validation.md`
- Estimated scope: S

### Task 5: Review for completeness, quality, and over-engineering

- Description: Independently review the new skill against the confirmed spec and flag missing requirements, weak gates, context-pollution risks, and unnecessary complexity.
- Worker role: review
- Wave: 5
- Acceptance criteria: Review artifact includes `Verdict: PASS` or `Verdict: FAIL`; FAIL findings include file path, issue, impact, and required fix.
- Verification: `rg "Verdict: (PASS|FAIL)" /data/lcq/.codex/skills/.codex/work/20260621-plan2do/review-plan2do.md`
- Concrete edits: Write only `/data/lcq/.codex/skills/.codex/work/20260621-plan2do/review-plan2do.md`.
- Interfaces / contracts changed: None.
- Test cases: Review checks every acceptance item from `.codex/work/20260621-plan2do/spec.md`.
- Pre-check commands: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`
- Post-check commands: `rg "Verdict: (PASS|FAIL)" /data/lcq/.codex/skills/.codex/work/20260621-plan2do/review-plan2do.md`
- Dependencies: Task 4.
- Files likely touched: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do/review-plan2do.md`
- Writable scope: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do/review-plan2do.md`
- Output artifact: `.codex/work/20260621-plan2do/review-plan2do.md`
- Estimated scope: S

### Task 6: Apply bounded rework if review fails

- Description: If Task 5 returns `Verdict: FAIL`, the primary agent writes rework guidance, applies focused fixes, reruns validation, and updates review status.
- Worker role: coding
- Wave: 6
- Acceptance criteria: Rework guidance exists before fixes; each FAIL finding is addressed or recorded as a blocker; `quick_validate.py` passes after fixes; follow-up review returns `Verdict: PASS` or blocker report.
- Verification: `test -f /data/lcq/.codex/skills/.codex/work/20260621-plan2do/artifacts/rework-guidance.md && python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`
- Concrete edits: Write `/data/lcq/.codex/skills/.codex/work/20260621-plan2do/artifacts/rework-guidance.md`; patch only files named by FAIL findings inside `/data/lcq/.codex/skills/plan2do/`.
- Interfaces / contracts changed: Only the deficient parts identified by review.
- Test cases: Re-run `quick_validate.py`, grep checks from Tasks 2 and 3, and scoped review.
- Pre-check commands: `rg "Verdict: FAIL" /data/lcq/.codex/skills/.codex/work/20260621-plan2do/review-plan2do.md`
- Post-check commands: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`
- Dependencies: Task 5 with `Verdict: FAIL`.
- Files likely touched: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do/artifacts/rework-guidance.md`; `/data/lcq/.codex/skills/plan2do/SKILL.md`; `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`; `/data/lcq/.codex/skills/plan2do/agents/openai.yaml`
- Writable scope: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do/artifacts/rework-guidance.md`; `/data/lcq/.codex/skills/plan2do/`
- Output artifact: `.codex/work/20260621-plan2do/artifacts/task6-rework.md`
- Estimated scope: M

## Step-by-Step Plan
1. Create `/data/lcq/.codex/skills/plan2do/SKILL.md` and `/data/lcq/.codex/skills/plan2do/agents/openai.yaml`.
2. Add `/data/lcq/.codex/skills/plan2do/references/execution-contract.md` with plan intake, execution modes, quality gates, rework, artifacts, and final report contract.
3. Update `/data/lcq/.codex/skills/plan2do/SKILL.md` to require `context-engineering` and link `references/execution-contract.md`.
4. Run `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`.
5. Run `rg "default.*primary|codex2codex|context-engineering|rework guidance|false completion" /data/lcq/.codex/skills/plan2do/SKILL.md`.
6. Write `/data/lcq/.codex/skills/.codex/work/20260621-plan2do/review-plan2do.md` with `Verdict: PASS` or `Verdict: FAIL`.
7. If review fails, write `/data/lcq/.codex/skills/.codex/work/20260621-plan2do/artifacts/rework-guidance.md`, patch named files, and rerun `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`.
8. Write final execution summary to `/data/lcq/.codex/skills/.codex/work/20260621-plan2do/artifacts/final-summary.md`.

## Parallelization
Wave 1 runs alone because it creates the shared skill directory. Wave 2 and Wave 3 are sequential because `SKILL.md` links to the reference contract. Wave 4 follows implementation. Wave 5 is independent review and writes only the review artifact. Wave 6 runs only on review failure and may touch the skill files named by findings.

## Files / Components Likely Affected
- `/data/lcq/.codex/skills/plan2do/SKILL.md`
- `/data/lcq/.codex/skills/plan2do/agents/openai.yaml`
- `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- `/data/lcq/.codex/skills/.codex/work/20260621-plan2do/review-plan2do.md`
- `/data/lcq/.codex/skills/.codex/work/20260621-plan2do/artifacts/*.md`

## Owners / Responsibilities
- coding: create skill files, write reference contract, validate metadata.
- review: inspect against spec, quality gates, context hygiene, and over-engineering risk.
- primary agent: decide rework guidance before any fix cycle and own final acceptance.

## Validation Plan
- Run `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`.
- Run `rg "default.*primary|codex2codex|context-engineering|execution-contract|rework guidance|false completion" /data/lcq/.codex/skills/plan2do/SKILL.md`.
- Run `rg "Primary-agent|codex2codex|rework guidance|Context Capsule|Final report|Blocker" /data/lcq/.codex/skills/plan2do/references/execution-contract.md`.
- Review `.codex/work/20260621-plan2do/spec.md` acceptance checks against the completed skill.

## Rollout Plan
Keep the new skill local under `/data/lcq/.codex/skills/plan2do`. Use it on the next plan-execution request. Do not modify global skill routing beyond adding the skill folder and metadata.

## Monitoring / Observability
Record validation output, review verdict, rework guidance, and final summary under `.codex/work/20260621-plan2do/artifacts/` and `.codex/work/20260621-plan2do/review-plan2do.md`. Final response should cite artifact paths and omit raw logs.

## Documentation / ADR Updates
ADR: Not needed. This is a local skill addition with its own `SKILL.md`, `agents/openai.yaml`, and reference contract.

## Rollback / Recovery Plan
If the skill is invalid or rejected, remove only `/data/lcq/.codex/skills/plan2do/` after confirming no user edits landed there, or move it to `.codex/work/20260621-plan2do/revisions/plan2do-rejected/` if preservation is desired. Leave existing unrelated dirty files untouched.

## Abort Criteria
- Abort before editing if `/data/lcq/.codex/skills/plan2do` appears with user content.
- Abort if `quick_validate.py` cannot pass after focused fixes.
- Abort if review reports unresolved functional gaps after two fix cycles.
- Abort and ask the user if implementation requires destructive git operations, production deployment, or rollback of unrelated user work.

## Risks
- The skill could overfit this single workflow and become too rigid; mitigate by keeping `SKILL.md` concise and reference contract procedural.
- The skill could duplicate `codex2codex`; mitigate by making `codex2codex` an explicit backend and keeping `plan2do` responsible for acceptance and rework governance.
- The skill could under-specify context hygiene; mitigate by requiring `context-engineering` source-of-truth rehydration and artifact quarantine.
- Review may be skipped under time pressure; mitigate by treating missing review as incomplete for non-trivial plans.

## Open Questions
- The rework cycle limit is assumed to be two per failed task or review scope. The user can tune this after v1.

## Plan Self-Review
- writable scope is exact for each task; same-wave writes do not overlap because each implementation wave is sequential or review-only.
- coverage includes `quick_validate.py`, grep checks, manual spec acceptance review, and review verdict.
- unknown handling is explicit in `Assumptions` and `Open Questions`.
- rollback and abort criteria are specific to this medium-risk local skill addition.
- Task 1 can be executed by a fresh agent from this plan without raw transcript context.

## Execution Decision
Ready for implementation when the user asks to execute. This step generated only planning artifacts and did not implement the `plan2do` skill.

## Execution Handoff

- Goal: Build `/data/lcq/.codex/skills/plan2do` to execute `spec2plan` plans with quality and context controls.
- Current state: Confirmed spec and executable plan are saved in `.codex/work/20260621-plan2do/`.
- Authoritative artifacts: `.codex/work/20260621-plan2do/spec.md`; `.codex/work/20260621-plan2do/plan.md`
- Decisions: Default primary-agent execution; explicit `codex2codex` mode; mandatory `context-engineering`; primary-agent rework guidance before fixes.
- Verification: Run `python /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do/plan.md --mode light`.
- Remaining risks: Rework cycle limit is assumed; implementation may adjust if user clarifies.
- Next action: Execute Task 1 from the plan.
- Suggested skills: plan2do after creation; apply-patch; skill-creator; context-engineering; codex2codex only if explicitly requested.
- Redactions / omitted raw data: Raw interview transcript and tool outputs are omitted; use saved spec and plan paths.
