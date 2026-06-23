SPEC2PLAN_ARTIFACT_V1
phase: synthesizer
status: complete
artifact:
# Structural Edit Skill Implementation Plan

Mode: heavy
Risk level: High
Confidence: Medium

## Goal
Implement a new `structural-edit` skill that becomes the default manual-edit entrypoint, makes structure-aware routes primary for supported file classes, keeps a tightly constrained text fallback, migrates `edit-orchestration` into a compatibility shell, and completes validation, production gating, and final review inside `.codex/work/20260623-structural-edit/`.

## Non-Goals
- Do not build a persistent daemon, remote service, or autonomous external editor.
- Do not add first-class v1 support for `C/C++`, `Rust`, or extra speculative language routes.
- Do not mutate system package-manager state, require `sudo`, or write into `/usr`, `/usr/local`, `/bin`, `/etc`, `/var`, or `/opt`.
- Do not delete unrelated skills, logs, auth/state DBs, or user work.
- Do not silently keep `edit-orchestration` and `structural-edit` as competing defaults.

## Evidence Inspected
- Confirmed spec: `.codex/work/20260623-structural-edit/spec.md`
- Workspace manifest: `.codex/work/20260623-structural-edit/manifest.yaml`
- Existing default editing skill: `edit-orchestration/SKILL.md`
- Existing tool-prep script: `edit-orchestration/scripts/prepare_edit_tools.py`
- Existing tool self-check script: `edit-orchestration/scripts/self_check_edit_tools.py`
- Existing editing references tree: `edit-orchestration/references/`
- Skill scaffold tooling: `.system/skill-creator/SKILL.md`
- Skill scaffold script: `.system/skill-creator/scripts/init_skill.py`
- Skill metadata generator/validator: `.system/skill-creator/scripts/generate_openai_yaml.py`, `.system/skill-creator/scripts/quick_validate.py`
- Plan contract: `spec2plan/references/plan-contract.md`
- Heavy-mode contract: `spec2plan/references/heavy-mode.md`
- Artifact contract: `spec2plan/references/artifact-contract.md`
- Execution contract: `plan2do/references/execution-contract.md`
- Failure policy: `plan2do/references/failure-policy.md`
- Review rubric: `plan2do/references/review-rubric.md`
- Reviewer contract/template: `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`
- Skill Production Gate: `skill-tokenless/SKILL.md`, `skill-tokenless/references/testing.md`, `skill-tokenless/references/validation.md`, `skill-tokenless/references/skill-production-gate.md`
- `codex2codex` blocker evidence: `codex2codex/install.sh`; `codex2codex/meight.py doctor --json`; `pip index versions openai-codex`

## Spec Summary
The new skill must replace patch-first editing with a structure-first bus: prefer project-owned generators/formatters when they own output, otherwise prefer structure-aware tools for Python, JS/TS, JSON, YAML, and Markdown, support conditional Java/OpenRewrite, keep a strictly constrained text fallback, and hard-stop with `BLOCK` when the selected structural route should apply but the required toolchain is missing or unhealthy. The migration must leave one authoritative default editing path and include install, self-check, manifest, compatibility, rollback, and validation scenario contracts.

## Upstream Coverage
- Source artifacts: `.codex/work/20260623-structural-edit/spec.md`; `.codex/work/20260623-structural-edit/manifest.yaml`; `edit-orchestration/SKILL.md`; `edit-orchestration/scripts/prepare_edit_tools.py`; `edit-orchestration/scripts/self_check_edit_tools.py`
- Carried forward: replacement-grade default entrypoint, required primary routes for Python/JS/TS/JSON/YAML/Markdown, conditional Java support, strict text fallback, hard-stop on missing structural tooling, migration away from patch-first authority, install/self-check/manifest/version policy, compatibility strategy, validation scenarios, and heavy review gate requirement.
- Added planning detail: exact file list, script CLIs, per-task writable scope, production/report artifact paths, main-thread fallback evidence for blocked `codex2codex`, validator command sequence, and execution ordering.
- Dropped / deferred upstream details: None

## Domain Language Check
- Canonical new skill: `structural-edit`
- Compatibility shell: `edit-orchestration`
- Primary route terms: `generator-owned`, `ast-grep`, `jscodeshift`, `jq`, `yq`, `remark`, `openrewrite`, `strict text fallback`, `BLOCK`
- Governance terms: `toolchain manifest`, `self-check`, `route matrix`, `validation scenarios`, `production report`
- No blocking terminology conflict found, but old `edit-orchestration` copy uses `apply_patch` fast path as default and must be downgraded.

## Current Context
- Context state: focused
- Context artifact: `.codex/work/20260623-structural-edit/artifacts/context-wave1.md`
- Main repo root: `/data/lcq/.codex/skills`
- Current workspace contains only `spec.md` and `manifest.yaml`.
- `structural-edit/` does not exist yet.
- `codex2codex` heavy worker backend is currently unavailable because `codex2codex/install.sh` pins `openai-codex==0.1.0b3`, and current package indexes do not expose that distribution, so the required subagent route cannot be used for this run.
- Execution therefore proceeds in the main thread with explicit blocker evidence, while still preserving heavy-grade planning, validation, and review artifacts.

## Implementation Map
- Files:
  - `structural-edit/SKILL.md` — new default skill contract and routing entrypoint.
  - `structural-edit/agents/openai.yaml` — UI metadata aligned to the new default role.
  - `structural-edit/references/route-matrix.md` — required primary routes, fallback predicates, BLOCK cases.
  - `structural-edit/references/tooling.md` — install roots, per-tool install methods, manifest schema, version policy.
  - `structural-edit/references/fallback-policy.md` — strict fallback and hard-stop rules.
  - `structural-edit/references/migration.md` — migration from `edit-orchestration`, compatibility shell, rollback.
  - `structural-edit/references/compatibility.md` — repo/tooling compatibility behavior.
  - `structural-edit/references/validation-scenarios.md` — scenario gate expectations and commands.
  - `structural-edit/scripts/route_decision.py` — deterministic route classifier for validation and reuse.
  - `structural-edit/scripts/prepare_structural_tools.py` — user-root install/prep helper.
  - `structural-edit/scripts/self_check_structural_tools.py` — required tool readiness checks.
  - `structural-edit/scripts/manifest_report.py` — manifest/report helper.
  - `structural-edit/scripts/validate_structural_routes.py` — scenario gate validator.
  - `edit-orchestration/SKILL.md` — compatibility-shell rewrite that delegates to `structural-edit`.
  - `edit-orchestration/agents/openai.yaml` — compatibility metadata narrowing if needed.
  - `edit-orchestration/references/route-matrix.md` and `edit-orchestration/references/tooling.md` — downgrade patch-first language and redirect to `structural-edit`.
  - `.codex/work/20260623-structural-edit/manifest.yaml` — canonical plan/stage updates.
  - `.codex/work/20260623-structural-edit/artifacts/production-report.md` — Skill Production Gate artifact.
  - `.codex/work/20260623-structural-edit/review.md` — final reviewer report.
  - `.codex/work/20260623-structural-edit/artifacts/final-report.md` — final execution summary.
- Symbols / APIs:
  - `.system/skill-creator/scripts/init_skill.py:init_skill`
  - `.system/skill-creator/scripts/quick_validate.py:validate_skill`
  - `edit-orchestration/scripts/prepare_edit_tools.py:prepare`
  - `edit-orchestration/scripts/self_check_edit_tools.py:check_tool`
  - New CLI entrypoints: `prepare_structural_tools.py`, `self_check_structural_tools.py`, `manifest_report.py`, `validate_structural_routes.py`
- Tests:
  - `.system/skill-creator/scripts/quick_validate.py structural-edit`
  - `.system/skill-creator/scripts/quick_validate.py edit-orchestration`
  - `python3 structural-edit/scripts/self_check_structural_tools.py --tool <tool> --json`
  - `python3 structural-edit/scripts/prepare_structural_tools.py --list`
  - `python3 structural-edit/scripts/validate_structural_routes.py`
  - `python3 reviewer/scripts/validate_review_report.py .codex/work/20260623-structural-edit/review.md`
  - `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-structural-edit/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft|final`
  - `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260623-structural-edit --stage draft --require-production-report --require-final-report`
  - `python3 plan2do/scripts/validate_execution.py .codex/work/20260623-structural-edit`
- Commands:
  - `python3 .system/skill-creator/scripts/init_skill.py structural-edit --path /data/lcq/.codex/skills --resources scripts,references --interface display_name="Structural Edit" --interface short_description="Use structure-first manual editing with hard-stop fallback rules." --interface default_prompt="Use this skill for manual file edits; choose generator-owned or structural routes first, then enforce strict fallback rules."`
  - `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260623-structural-edit/plan.md --mode heavy`
  - `python3 plan2do/scripts/compile_execution.py .codex/work/20260623-structural-edit/plan.md`
- Data / migration impact: No runtime/user data migration. Skill/documentation migration only; compatibility shell and rollback note required.

## Assumptions
- Main-thread fallback is acceptable for this run because the required heavy subagent backend is unavailable and the blocker is recorded explicitly.
- The migration path will keep `edit-orchestration` as a compatibility shell instead of deleting it outright, minimizing disruption while still leaving one authoritative default path.
- Tool preparation can rely on user-root npm, Python venv, or downloaded user-root binaries without mutating system package-manager state.
- Route-choice evidence via deterministic validators and scenario probes is sufficient for this skill-layer implementation; real editing via external tools remains a runtime use of the skill, not a build-time code generation task.

## User Inputs Needed
Not applicable. The confirmed spec already defines required routes, fallback rules, migration outcome, and review gate. Repo evidence is sufficient to proceed.

## Proposed Approach
- Reuse `edit-orchestration` scaffolding patterns for tool manifests and self-check flow, but invert the default so structure-aware routing is primary.
- Create a dedicated `structural-edit` skill with central route classification and toolchain scripts.
- Keep install/prep and self-check deterministic and user-root only.
- Move route-specific policy and migration details into `references/` to keep `SKILL.md` concise.
- Downgrade `edit-orchestration` into a compatibility shell that redirects to `structural-edit`, removes patch-first authority, and preserves rollback clarity.
- Validate plan, compile execution state, execute tasks in order, write production/final reports, then run inline-heavy reviewer fallback because the reviewer subagent backend is unavailable for the same `codex2codex` dependency reason.

## Scenario Probes
- Probe 1: Python semantic edit should classify to `ast-grep`, not `apply_patch`.
- Probe 2: JS/TS migration should classify to `jscodeshift` first, with `ast-grep` secondary only when the change is simpler.
- Probe 3: JSON/YAML path operations should classify to `jq`/`yq` and return `BLOCK` if the route should apply but the tool is unavailable.
- Probe 4: Markdown section rewrite should classify to `remark`; a tiny unique prose fix may use strict text fallback.
- Probe 5: Generated file request should classify to generator-owned route.
- Probe 6: Java request without valid OpenRewrite context should `BLOCK`.
- Probe 7: Old `edit-orchestration` invocation should redirect to `structural-edit` rather than reintroduce patch-first authority.

## Dependency Graph
- Task 1 scaffold and workspace updates -> Task 2 toolchain/runtime scripts -> Task 3 skill contracts and migration docs -> Task 4 validation/report artifacts -> Task 5 final review and execution validation

## Task Breakdown
### Task 1: Scaffold structural-edit workspace and metadata

- Description: Create the new `structural-edit` skill scaffold, workspace artifact directories, and canonical manifest updates without yet writing the full route/tool policy.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `structural-edit/` exists with `SKILL.md`, `agents/`, `references/`, and `scripts/`; `.codex/work/20260623-structural-edit/manifest.yaml` records canonical `plan.md`; no unrelated files are touched.
- Verification: `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/structural-edit`
- Concrete edits: Run the scaffold generator or equivalent minimal file creation; add workspace `artifacts/` and `review.md` placeholders only when needed; update manifest stage/plan path.
- Interfaces / contracts changed: New default editing skill package path and metadata contract.
- Test cases: Scaffold validator pass; generated metadata files exist.
- Pre-check commands: `test ! -e /data/lcq/.codex/skills/structural-edit`
- Post-check commands: `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/structural-edit`
- Dependencies: none
- Files likely touched: `structural-edit/`; `.codex/work/20260623-structural-edit/manifest.yaml`
- Writable scope: `structural-edit/`, `.codex/work/20260623-structural-edit/manifest.yaml`
- Output artifact: `.codex/work/20260623-structural-edit/artifacts/task1-scaffold.md`
- Estimated scope: S

### Task 2: Implement route and toolchain scripts

- Description: Build deterministic route-decision, tool self-check, tool preparation, and manifest/report helpers covering the required v1 route set and hard-stop rules.
- Worker role: coding
- Wave: 2
- Acceptance criteria: Route classifier covers Python, JS/TS, JSON, YAML, Markdown, generated-output, Java/OpenRewrite, and strict text fallback; self-check reports per-tool readiness; prep script enforces user-root-only install roots; manifest helper emits stable JSON/summary.
- Verification: `python3 structural-edit/scripts/prepare_structural_tools.py --list`; `python3 structural-edit/scripts/self_check_structural_tools.py --tool ast-grep --json`; `python3 structural-edit/scripts/manifest_report.py --help`
- Concrete edits: Adapt and generalize logic from `edit-orchestration` scripts into new `structural-edit` scripts; add support for `jq`, `yq`, `remark`, and route metadata.
- Interfaces / contracts changed: New script CLIs and manifest schema for `structural-edit`.
- Test cases: Existing tool on PATH; missing tool yields `BLOCK`-grade reason; forbidden root rejected.
- Pre-check commands: `python3 structural-edit/scripts/self_check_structural_tools.py --help`
- Post-check commands: `python3 structural-edit/scripts/prepare_structural_tools.py --list`
- Dependencies: Task 1
- Files likely touched: `structural-edit/scripts/prepare_structural_tools.py`, `structural-edit/scripts/self_check_structural_tools.py`, `structural-edit/scripts/route_decision.py`, `structural-edit/scripts/manifest_report.py`
- Writable scope: `structural-edit/scripts/`
- Output artifact: `.codex/work/20260623-structural-edit/artifacts/task2-toolchain.md`
- Estimated scope: M

### Task 3: Write skill contracts and migrate edit-orchestration

- Description: Finalize `structural-edit` docs/metadata/references and rewrite `edit-orchestration` as a compatibility shell that delegates to `structural-edit`.
- Worker role: coding
- Wave: 3
- Acceptance criteria: `structural-edit/SKILL.md` is concise and authoritative; required references exist; `edit-orchestration` no longer claims patch-first default authority and clearly delegates to `structural-edit`; rollback path is documented.
- Verification: `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/structural-edit`; `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`
- Concrete edits: Write `structural-edit/references/route-matrix.md`, `tooling.md`, `fallback-policy.md`, `migration.md`, `compatibility.md`, and `validation-scenarios.md`; update `structural-edit/agents/openai.yaml`; rewrite `edit-orchestration/SKILL.md` and selected references to redirect to `structural-edit`.
- Interfaces / contracts changed: Default edit-entry skill contract and compatibility-shell behavior.
- Test cases: Trigger descriptions remain searchable; compatibility shell explicitly delegates; no silent fallback wording remains.
- Pre-check commands: `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`
- Post-check commands: `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/structural-edit && python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`
- Dependencies: Task 2
- Files likely touched: `structural-edit/SKILL.md`, `structural-edit/agents/openai.yaml`, `structural-edit/references/`, `edit-orchestration/SKILL.md`, `edit-orchestration/agents/openai.yaml`, `edit-orchestration/references/route-matrix.md`, `edit-orchestration/references/tooling.md`
- Writable scope: `structural-edit/`, `edit-orchestration/SKILL.md`, `edit-orchestration/agents/openai.yaml`, `edit-orchestration/references/route-matrix.md`, `edit-orchestration/references/tooling.md`
- Output artifact: `.codex/work/20260623-structural-edit/artifacts/task3-migration.md`
- Estimated scope: M

### Task 4: Add scenario validation and draft production artifacts

- Description: Add deterministic validation scenarios, produce draft production/final execution artifacts, compile execution state, and prove reviewer-launch readiness.
- Worker role: coding
- Wave: 4
- Acceptance criteria: Scenario validator passes the required cases; production report draft exists and passes draft validation; execution/tasks state exists; pre-review readiness passes.
- Verification: `python3 structural-edit/scripts/validate_structural_routes.py`; `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-structural-edit/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`; `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260623-structural-edit --stage draft --require-production-report --require-final-report`
- Concrete edits: Implement scenario validator; write draft `production-report.md`; write draft `final-report.md`; run `compile_execution.py` and update task artifacts.
- Interfaces / contracts changed: Validation/report artifacts only.
- Test cases: Each required scenario maps to expected route or `BLOCK`; draft report contains required sections.
- Pre-check commands: `python3 plan2do/scripts/compile_execution.py .codex/work/20260623-structural-edit/plan.md`
- Post-check commands: `python3 structural-edit/scripts/validate_structural_routes.py`
- Dependencies: Task 3
- Files likely touched: `structural-edit/scripts/validate_structural_routes.py`, `.codex/work/20260623-structural-edit/artifacts/production-report.md`, `.codex/work/20260623-structural-edit/artifacts/final-report.md`, `.codex/work/20260623-structural-edit/execution/tasks.json`
- Writable scope: `structural-edit/scripts/validate_structural_routes.py`, `.codex/work/20260623-structural-edit/artifacts/`, `.codex/work/20260623-structural-edit/execution/`
- Output artifact: `.codex/work/20260623-structural-edit/artifacts/task4-validation.md`
- Estimated scope: M

### Task 5: Review, finalize reports, and validate execution

- Description: Run final reviewer gate, fix critical/major findings if any, finalize production report, and validate execution completion.
- Worker role: review
- Wave: 5
- Acceptance criteria: Reviewer report is saved and validated; production report final validation passes; execution validator passes; final report records blocker/fallback evidence for unavailable `codex2codex` subagent route.
- Verification: `python3 reviewer/scripts/validate_review_report.py .codex/work/20260623-structural-edit/review.md`; `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-structural-edit/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`; `python3 plan2do/scripts/validate_execution.py .codex/work/20260623-structural-edit`
- Concrete edits: Write `review.md`; patch reviewed artifacts if needed; update final report and production report cleanup/reviewer sections.
- Interfaces / contracts changed: Review/final acceptance artifacts only.
- Test cases: Review verdict present; final report cites exact commands/outcomes; execution validator sees all tasks complete.
- Pre-check commands: `python3 reviewer/scripts/validate_review_report.py --self-test`
- Post-check commands: `python3 plan2do/scripts/validate_execution.py .codex/work/20260623-structural-edit`
- Dependencies: Task 4
- Files likely touched: `.codex/work/20260623-structural-edit/review.md`, `.codex/work/20260623-structural-edit/artifacts/production-report.md`, `.codex/work/20260623-structural-edit/artifacts/final-report.md`, `.codex/work/20260623-structural-edit/execution/tasks.json`
- Writable scope: `.codex/work/20260623-structural-edit/review.md`, `.codex/work/20260623-structural-edit/artifacts/`, `.codex/work/20260623-structural-edit/execution/`
- Output artifact: `.codex/work/20260623-structural-edit/review.md`
- Estimated scope: S

## Step-by-Step Plan
- Step 1: Create `.codex/work/20260623-structural-edit/artifacts/` and save the wave pack at `.codex/work/20260623-structural-edit/artifacts/context-wave1.md`.
- Step 2: Scaffold `structural-edit/` with `scripts/` and `references/`, then update `.codex/work/20260623-structural-edit/manifest.yaml` to record canonical `plan.md`.
- Step 3: Implement `structural-edit/scripts/route_decision.py` with a deterministic route classifier covering all required file classes and `BLOCK` conditions.
- Step 4: Implement `structural-edit/scripts/self_check_structural_tools.py`, `prepare_structural_tools.py`, and `manifest_report.py` using user-root-only install semantics.
- Step 5: Write `structural-edit/SKILL.md` plus required reference docs, keeping tool details in `references/`.
- Step 6: Rewrite `edit-orchestration/SKILL.md` and selected references so old entrypoints delegate to `structural-edit`.
- Step 7: Add `structural-edit/scripts/validate_structural_routes.py` and encode the required scenario matrix.
- Step 8: Run `python3 .system/skill-creator/scripts/quick_validate.py` for both `structural-edit` and `edit-orchestration`.
- Step 9: Run `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260623-structural-edit/plan.md --mode heavy` and `python3 plan2do/scripts/compile_execution.py .codex/work/20260623-structural-edit/plan.md`.
- Step 10: Write `.codex/work/20260623-structural-edit/artifacts/production-report.md` and `.codex/work/20260623-structural-edit/artifacts/final-report.md`, then run draft validation/readiness checks.
- Step 11: Produce `.codex/work/20260623-structural-edit/review.md` with inline-heavy reviewer fallback reasoning, validate it, patch critical/major findings, and rerun focused checks.
- Step 12: Run final production-report validation and `python3 plan2do/scripts/validate_execution.py .codex/work/20260623-structural-edit`.

## Parallelization
- Task 2 and Task 3 remain sequential because docs must match the script interfaces actually implemented.
- Within Task 4, report drafting and scenario validator authoring can alternate, but the draft readiness gate must wait for both.
- Final review stays isolated to Wave 5 to avoid mixing acceptance with implementation edits.

## Files / Components Likely Affected
- `structural-edit/`
- `edit-orchestration/SKILL.md`
- `edit-orchestration/agents/openai.yaml`
- `edit-orchestration/references/route-matrix.md`
- `edit-orchestration/references/tooling.md`
- `.codex/work/20260623-structural-edit/manifest.yaml`
- `.codex/work/20260623-structural-edit/plan.md`
- `.codex/work/20260623-structural-edit/artifacts/`
- `.codex/work/20260623-structural-edit/execution/`

## Owners / Responsibilities
- Main agent: scaffold skill, implement scripts/docs, run validators, maintain execution artifacts, and integrate review findings.
- Reviewer gate: inspect alignment with the spec, fallback safety, migration clarity, validator coverage, and production-gate completeness.
- No `codex2codex` worker ownership this run because the backend is blocked by unavailable pinned SDK distribution.

## Validation Plan
- Plan validation: `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260623-structural-edit/plan.md --mode heavy`
- Execution compile: `python3 plan2do/scripts/compile_execution.py .codex/work/20260623-structural-edit/plan.md`
- Skill shape: `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/structural-edit`
- Compatibility-shell shape: `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`
- Tool script smoke: `python3 structural-edit/scripts/prepare_structural_tools.py --list`
- Tool self-check smoke: `python3 structural-edit/scripts/self_check_structural_tools.py --tool ast-grep --json`
- Scenario gate: `python3 structural-edit/scripts/validate_structural_routes.py`
- Draft production gate: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-structural-edit/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
- Draft readiness: `python3 plan2do/scripts/pre_review_ready.py .codex/work/20260623-structural-edit --stage draft --require-production-report --require-final-report`
- Reviewer report validation: `python3 reviewer/scripts/validate_review_report.py .codex/work/20260623-structural-edit/review.md`
- Final production gate: `python3 skill-tokenless/scripts/validate_skill_production.py .codex/work/20260623-structural-edit/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`
- Final execution validation: `python3 plan2do/scripts/validate_execution.py .codex/work/20260623-structural-edit`

## Rollout Plan
- Phase 1: Land `structural-edit` beside `edit-orchestration`.
- Phase 2: Redirect `edit-orchestration` into compatibility-shell mode.
- Phase 3: Validate routes/reports/review artifacts.
- Phase 4: Treat `structural-edit` as the new authoritative default in future sessions.

## Monitoring / Observability
- Save per-task artifacts under `.codex/work/20260623-structural-edit/artifacts/`.
- Save execution checklist under `.codex/work/20260623-structural-edit/execution/tasks.json`.
- Record reviewer verdict in `.codex/work/20260623-structural-edit/review.md`.
- Record production gate cleanup and fallback evidence in `.codex/work/20260623-structural-edit/artifacts/production-report.md`.

## Documentation / ADR Updates
ADR: Needed

Document, within `structural-edit/references/migration.md` and `structural-edit/references/tooling.md`, why the environment now uses a structure-first editing bus with strict fallback rather than a patch-first default.

## Rollback / Recovery Plan
- If `structural-edit/` scaffold is wrong before migration, remove only `structural-edit/` and restore `.codex/work/20260623-structural-edit/manifest.yaml`.
- If tool scripts are invalid, revert only `structural-edit/scripts/` and rerun quick validation.
- If compatibility-shell edits misroute future users, restore the previous `edit-orchestration` files from the current diff and keep `structural-edit/` non-default until fixed.
- If reviewer finds critical migration or fallback defects, stop final acceptance and keep artifacts plus blocker evidence.
- If the `codex2codex` backend becomes installable later, future re-planning may re-enable true heavy subagent routing without changing implemented skill behavior.

## Abort Criteria
- `structural-edit/` already exists with user-owned content that conflicts with scaffold assumptions.
- Any script route requires system package-manager writes, `sudo`, or forbidden roots.
- `edit-orchestration` still claims default patch-first authority after migration edits.
- Required scenario validator cannot prove `BLOCK` on missing structural tool routes.
- Draft or final production report validation fails after one focused repair attempt.
- Reviewer finds silent-downgrade behavior or ambiguous default-entry routing and the fix would exceed confirmed scope.
- Final execution validation fails with unresolved task or artifact gaps.

## Risks
- Tool preparation for `jq`, `yq`, or `remark` may be platform-fragile; mitigate with explicit self-check reason strings and hard-stop behavior.
- Compatibility shell could accidentally leave two defaults alive; mitigate by making `edit-orchestration` purely delegating language.
- Overly verbose `SKILL.md` could bloat every session; mitigate by moving route detail into `references/`.
- Scenario validator may test route selection more than real edits; mitigate by documenting this limit in residual risks while still proving deterministic route choice and `BLOCK` policy.
- Reviewer subagent unavailability weakens isolation; mitigate by recording explicit inline-heavy fallback reason and using deterministic validators first.

## Open Questions
- None blocking for this implementation pass. Residual uncertainty about future `codex2codex` repair remains operational, not a skill-design blocker.

## Plan Self-Review
- Writable scope: tasks use exact paths and keep same-wave writes non-overlapping at the task level.
- Coverage: plan includes scaffold validation, route validation, production gate, reviewer gate, and final execution validation.
- Unknown handling: `codex2codex` backend blocker is explicit, evidenced, and kept out of implementation scope.
- Rollback: rollback names exact skill/workspace files and stop conditions.
- Fresh-agent handoff: Task 1 can start from the plan, spec, and current absence of `structural-edit/` without rereading chat history.

## Execution Decision
Proceed immediately in the main thread after plan validation and execution compilation. Heavy worker routing is blocked by unavailable `codex2codex` SDK dependency, so this run uses explicit fallback while preserving all required validation and review gates.

## Execution Handoff
- Goal: Build `structural-edit` as the structure-first default editing skill and migrate `edit-orchestration` into a compatibility shell.
- Current state: Spec confirmed; workspace has plan/context artifacts only; `structural-edit/` not yet implemented.
- Authoritative artifacts: `.codex/work/20260623-structural-edit/spec.md`; `.codex/work/20260623-structural-edit/plan.md`; `.codex/work/20260623-structural-edit/manifest.yaml`; `.codex/work/20260623-structural-edit/artifacts/context-wave1.md`
- Decisions: Use `structural-edit` as the new default; keep strict text fallback; preserve `edit-orchestration` as compatibility shell; use inline heavy review fallback because `codex2codex` subagent backend is unavailable.
- Verification: Run the exact commands in `## Validation Plan`, plus per-task artifact updates under `.codex/work/20260623-structural-edit/artifacts/`.
- Remaining risks: platform-specific tool install behavior, compatibility-shell wording drift, reviewer isolation fallback, and route-scenario coverage limits.
- Next action: Validate `plan.md`, compile execution state, then execute Task 1.
- Suggested skills: `context-engineering`, `skill-creator`, `skill-tokenless`, `reviewer`, `edit-orchestration`
- Redactions / omitted raw data: No raw command transcripts, large download logs, or stale worker transcripts included; `codex2codex` blocker is summarized from local command evidence only.
SPEC2PLAN_ARTIFACT_END
