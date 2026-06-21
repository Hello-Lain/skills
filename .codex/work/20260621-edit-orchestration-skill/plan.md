# Edit Orchestration Skill Implementation Plan

Mode: light
Risk level: Medium
Confidence: High

## Goal
实现一个新的 `edit-orchestration` skill，用来替代现有 `apply-patch` 的全局手工编辑职责。它必须默认覆盖所有手工文件编辑任务，通过 fast path 保持小改效率，通过 heavy routes 复用成熟工具思想与组件，并用 tool self-check、diff gate、verification gate 降低误改和失败率。

## Non-Goals
- 不在本计划执行实现、安装工具、改 `apply-patch` 元数据、删除旧 skill。
- 不构建完整 IDE、常驻 agent server、云端服务或全新编码代理。
- 不允许 `sudo`、系统包管理器写入、全局不可审计安装。
- 不允许 selected route 自检失败后静默退回更弱路线。

## Evidence Inspected
- Confirmed spec: `.codex/work/20260621-edit-orchestration-skill/spec.md`
- Workspace manifest: `.codex/work/20260621-edit-orchestration-skill/manifest.yaml`
- Current source skill: `apply-patch/SKILL.md`
- Current skill metadata pattern: `apply-patch/agents/openai.yaml`
- Existing skill scaffold tools: `.system/skill-creator/scripts/init_skill.py`
- Existing skill validator: `.system/skill-creator/scripts/quick_validate.py`
- Existing UI metadata generator: `.system/skill-creator/scripts/generate_openai_yaml.py`
- Plan contract: `spec2plan/references/plan-contract.md`
- Plan validator: `spec2plan/scripts/validate_plan_contract.py`
- Shared artifact contract: `references/artifact-contract.md`
- Existing example with references/scripts: `rtk-doctor/SKILL.md`, `rtk-doctor/references/known-issues.md`, `rtk-doctor/scripts/rtk-doctor.sh`
- Existing orchestration option present in repo: `codex2codex/scripts/run_plan.py`

## Spec Summary
The new skill must classify every manual edit, choose the lightest safe route, keep `apply_patch` for low-risk surgical edits, use mature external helpers for complex edit classes, self-prepare those helpers in user-level paths, pin or record versions, stop on selected-route self-check failure, inspect diffs, run focused verification, and report verification gaps.

## Domain Language Check
- Canonical name in plan: `edit-orchestration`
- Existing old skill: `apply-patch`
- Core route terms: `fast path`, `patch recovery path`, `agent-edit path`, `review-before-apply path`, `structural rewrite path`, `generated-output path`
- Required gates: `preflight`, `tool self-check`, `diff gate`, `verification gate`, `stop path`
- No term conflict found in inspected skill files.

## Current Context
- Context state: focused
- Phase: plan
- Risk: medium, because implementation will affect global editing behavior and may introduce auto tool preparation.
- Source of truth: confirmed spec path and current skill scaffold/validator files listed above.
- Context exclusions: prior web-search narrative and chat discussion are treated as background, not implementation evidence.

## Implementation Map
- Files: `edit-orchestration/SKILL.md` for core workflow; `edit-orchestration/agents/openai.yaml` for UI metadata; `edit-orchestration/references/route-matrix.md` for route decisions; `edit-orchestration/references/tooling.md` for helper tools; `edit-orchestration/references/failure-recovery.md` for patch/retry stop rules; `edit-orchestration/scripts/prepare_edit_tools.py` for lazy user-level tool setup; `edit-orchestration/scripts/self_check_edit_tools.py` for route self-checks; `apply-patch/SKILL.md` only if final validation confirms metadata narrowing is safe.
- Symbols / APIs: `.system/skill-creator/scripts/init_skill.py` command interface; `.system/skill-creator/scripts/quick_validate.py` validation interface; `.system/skill-creator/scripts/generate_openai_yaml.py` metadata interface; `prepare_edit_tools.py --tool <name> --root <path>`; `self_check_edit_tools.py --tool <name> --root <path>`.
- Tests: `.system/skill-creator/scripts/quick_validate.py edit-orchestration`; `python3 edit-orchestration/scripts/prepare_edit_tools.py --help`; `python3 edit-orchestration/scripts/self_check_edit_tools.py --tool ast-grep --check-only`; manual route-table review against `.codex/work/20260621-edit-orchestration-skill/spec.md`.
- Commands: `python3 .system/skill-creator/scripts/init_skill.py edit-orchestration --path /data/lcq/.codex/skills --resources scripts,references --interface display_name="Edit Orchestration" --interface short_description="Route file edits through safe fast and heavy paths." --interface default_prompt="Use this skill when editing files; classify risk, prepare helper tools when selected, inspect diff, verify."`; `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`; `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-edit-orchestration-skill/plan.md --mode light`; `python3 codex2codex/scripts/run_plan.py .codex/work/20260621-edit-orchestration-skill/plan.md --dry-run`.
- Data / migration impact: Not applicable; no database, schema, runtime data, or user secrets are edited by this plan.

## Assumptions
- `edit-orchestration` is the v1 skill name because it names routing and workflow better than `safe-edit` or `surgical-edit`.
- `apply-patch` remains installed during v1 rollout, then its metadata can be narrowed after `edit-orchestration` validates.
- Helper tools are lazily prepared per route, not installed during skill load.
- `ast-grep` is the first structural rewrite helper to support; `aider`, `jscodeshift`, and OpenRewrite can be represented in tooling references and scripts without eager installation.
- Skill body should stay concise; route/tool details belong in references and scripts.

## User Inputs Needed
No user input is needed before writing the implementation. The plan chooses `edit-orchestration` as the skill name and keeps `apply-patch` until validation passes.

## Proposed Approach
Create `edit-orchestration` as a new skill rather than editing `apply-patch` in place. Use `skill-creator` scaffold for structure and metadata. Put the stable decision protocol in `SKILL.md`, move route tables and tool specifics into references, and add deterministic scripts for user-level tool setup and self-check. Validate the new skill independently, forward-test representative route scenarios, then narrow `apply-patch` trigger text only after the new skill passes validation.

## Scenario Probes
- Low-risk edit: one-line doc/code change with unique nearby anchor should remain `read -> apply_patch -> diff -> verification report`.
- Patch failure: missing hunk or visual-match miss should force raw re-read, one small retry, then stop with evidence if route remains unsafe.
- Structural repeated edit: repeated syntax-aware replacement should select `ast-grep`, run self-check, then proceed or stop on self-check failure.
- Complex multi-file natural-language edit: should select agent-edit or review-before-apply path, prepare selected helper, require pending diff review, then apply only after gate success.
- Generated output: formatter or project generator writes owned files, then skill inspects diff and rejects unrelated churn.

## Dependency Graph
- Task 1 -> Task 2 because scaffold paths and metadata must exist before writing protocol files.
- Task 2 -> Task 3 because route references define the tool setup script contract.
- Task 3 -> Task 4 because tool scripts must exist before examples can cite exact commands.
- Task 2 and Task 3 -> Task 5 because old `apply-patch` metadata should only narrow after the replacement behavior exists.
- Task 1 through Task 5 -> Task 6 because final review needs complete files and validation output.

## Task Breakdown
### Task 1: Scaffold `edit-orchestration`

- Description: Create the new skill directory with script and reference resource folders using the existing skill scaffold command, then record the generated file list.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `edit-orchestration/SKILL.md`, `edit-orchestration/agents/openai.yaml`, `edit-orchestration/scripts/`, and `edit-orchestration/references/` exist; no existing skill directory is overwritten; scaffold output is saved to `.codex/work/20260621-edit-orchestration-skill/artifacts/task1-scaffold.md`.
- Verification: Run `python3 .system/skill-creator/scripts/init_skill.py edit-orchestration --path /data/lcq/.codex/skills --resources scripts,references --interface display_name="Edit Orchestration" --interface short_description="Route file edits through safe fast and heavy paths." --interface default_prompt="Use this skill when editing files; classify risk, prepare helper tools when selected, inspect diff, verify."` followed by `find edit-orchestration -maxdepth 2 -type f -print | sort`.
- Concrete edits: Create `edit-orchestration/SKILL.md`, `edit-orchestration/agents/openai.yaml`, `edit-orchestration/scripts/`, and `edit-orchestration/references/` through `.system/skill-creator/scripts/init_skill.py`.
- Interfaces / contracts changed: Adds a new skill trigger surface via `edit-orchestration/SKILL.md` frontmatter and `edit-orchestration/agents/openai.yaml`.
- Test cases: Confirm `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration` can read the scaffold after creation.
- Pre-check commands: Run `test ! -e /data/lcq/.codex/skills/edit-orchestration`.
- Post-check commands: Run `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`.
- Dependencies: None.
- Files likely touched: `edit-orchestration/SKILL.md`; `edit-orchestration/agents/openai.yaml`; `edit-orchestration/scripts/`; `edit-orchestration/references/`; `.codex/work/20260621-edit-orchestration-skill/artifacts/task1-scaffold.md`.
- Writable scope: `edit-orchestration/`; `.codex/work/20260621-edit-orchestration-skill/artifacts/task1-scaffold.md`.
- Output artifact: `.codex/work/20260621-edit-orchestration-skill/artifacts/task1-scaffold.md`
- Estimated scope: S

### Task 2: Write core workflow and route references

- Description: Replace scaffold placeholder content with the core `edit-orchestration` protocol and three concise reference files for route selection, tooling rules, and failure recovery.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `SKILL.md` describes all trigger contexts in frontmatter; body includes preflight, route selection, gates, and stop rules; references are linked directly from `SKILL.md`; `SKILL.md` stays under 500 lines.
- Verification: Run `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration` and `wc -l edit-orchestration/SKILL.md edit-orchestration/references/route-matrix.md edit-orchestration/references/tooling.md edit-orchestration/references/failure-recovery.md`.
- Concrete edits: Edit `edit-orchestration/SKILL.md`; add `edit-orchestration/references/route-matrix.md`; add `edit-orchestration/references/tooling.md`; add `edit-orchestration/references/failure-recovery.md`.
- Interfaces / contracts changed: Defines route names, mandatory gates, selected-route self-check behavior, and final response requirements for all future manual edits.
- Test cases: Manual review: compare route coverage against `.codex/work/20260621-edit-orchestration-skill/spec.md` Success Criteria, Scope, Requirements, and Acceptance Checks.
- Pre-check commands: Run `sed -n '1,220p' .codex/work/20260621-edit-orchestration-skill/spec.md`.
- Post-check commands: Run `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`.
- Dependencies: Task 1.
- Files likely touched: `edit-orchestration/SKILL.md`; `edit-orchestration/references/route-matrix.md`; `edit-orchestration/references/tooling.md`; `edit-orchestration/references/failure-recovery.md`; `.codex/work/20260621-edit-orchestration-skill/artifacts/task2-protocol.md`.
- Writable scope: `edit-orchestration/SKILL.md`; `edit-orchestration/references/route-matrix.md`; `edit-orchestration/references/tooling.md`; `edit-orchestration/references/failure-recovery.md`; `.codex/work/20260621-edit-orchestration-skill/artifacts/task2-protocol.md`.
- Output artifact: `.codex/work/20260621-edit-orchestration-skill/artifacts/task2-protocol.md`
- Estimated scope: M

### Task 3: Add user-level tool preparation and self-check scripts

- Description: Implement deterministic helper scripts that prepare selected tools in user-level paths, record versions, and perform route self-checks without mutating system package state.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `prepare_edit_tools.py` supports `--tool ast-grep`, `--tool aider`, `--tool jscodeshift`, `--tool openrewrite`, `--root`, `--check-only`, and `--list`; `self_check_edit_tools.py` verifies the selected tool or exits nonzero with a stop message; both scripts refuse `sudo` and system install locations.
- Verification: Run `python3 edit-orchestration/scripts/prepare_edit_tools.py --help`, `python3 edit-orchestration/scripts/self_check_edit_tools.py --help`, and `python3 edit-orchestration/scripts/prepare_edit_tools.py --list`.
- Concrete edits: Add `edit-orchestration/scripts/prepare_edit_tools.py`; add `edit-orchestration/scripts/self_check_edit_tools.py`; add a tool manifest output convention under `$CODEX_HOME/tools/edit-orchestration/manifest.json` documented in `edit-orchestration/references/tooling.md`.
- Interfaces / contracts changed: Introduces script CLIs `prepare_edit_tools.py` and `self_check_edit_tools.py`; introduces user-level tool manifest path `$CODEX_HOME/tools/edit-orchestration/manifest.json`.
- Test cases: `--help` exits 0; `--list` prints supported tool ids; `--check-only --tool ast-grep` exits 0 when installed and nonzero with a stop message when absent; no script writes outside the supplied `--root` during check-only mode.
- Pre-check commands: Run `python3 --version`.
- Post-check commands: Run `python3 edit-orchestration/scripts/prepare_edit_tools.py --list`.
- Dependencies: Task 1.
- Files likely touched: `edit-orchestration/scripts/prepare_edit_tools.py`; `edit-orchestration/scripts/self_check_edit_tools.py`; `edit-orchestration/references/tooling.md`; `.codex/work/20260621-edit-orchestration-skill/artifacts/task3-tooling.md`.
- Writable scope: `edit-orchestration/scripts/prepare_edit_tools.py`; `edit-orchestration/scripts/self_check_edit_tools.py`; `.codex/work/20260621-edit-orchestration-skill/artifacts/task3-tooling.md`.
- Output artifact: `.codex/work/20260621-edit-orchestration-skill/artifacts/task3-tooling.md`
- Estimated scope: M

### Task 4: Add route examples and validation checklist

- Description: Add compact examples that demonstrate the fast path, patch recovery path, structural rewrite path, agent-edit path, review-before-apply path, and generated-output path.
- Worker role: coding
- Wave: 3
- Acceptance criteria: Examples are concise, use exact route names, include stop behavior for self-check failure, and avoid duplicating the full protocol from `SKILL.md`.
- Verification: Run `grep -R "fast path\\|patch recovery path\\|structural rewrite path\\|agent-edit path\\|review-before-apply path\\|generated-output path" -n edit-orchestration`.
- Concrete edits: Add `edit-orchestration/references/examples.md`; update `edit-orchestration/SKILL.md` to read examples only when behavior is ambiguous or forward-testing is needed.
- Interfaces / contracts changed: Adds examples as optional reference material; no CLI contract change.
- Test cases: Manual check that each example maps to one route and contains a preflight, gate, stop, or verification signal.
- Pre-check commands: Run `test -f edit-orchestration/SKILL.md`.
- Post-check commands: Run `grep -R "selected route" -n edit-orchestration`.
- Dependencies: Task 2 and Task 3.
- Files likely touched: `edit-orchestration/references/examples.md`; `edit-orchestration/SKILL.md`; `.codex/work/20260621-edit-orchestration-skill/artifacts/task4-examples.md`.
- Writable scope: `edit-orchestration/references/examples.md`; `.codex/work/20260621-edit-orchestration-skill/artifacts/task4-examples.md`.
- Output artifact: `.codex/work/20260621-edit-orchestration-skill/artifacts/task4-examples.md`
- Estimated scope: S

### Task 5: Stage old `apply-patch` coexistence policy

- Description: Decide and apply the minimal coexistence change after the new skill validates: keep `apply-patch` installed, narrow its description to low-level patch grammar support, and avoid deleting user-visible history.
- Worker role: coding
- Wave: 4
- Acceptance criteria: `apply-patch/SKILL.md` remains available; its metadata no longer competes as the default all-edit trigger after `edit-orchestration` passes validation; `apply-patch/agents/openai.yaml` remains consistent if metadata is changed.
- Verification: Run `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/apply-patch` and `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`.
- Concrete edits: Edit `apply-patch/SKILL.md` frontmatter description only after `edit-orchestration` validates; regenerate or manually align `apply-patch/agents/openai.yaml` if its short description conflicts with the narrowed role.
- Interfaces / contracts changed: Changes skill trigger routing: `edit-orchestration` becomes default manual-edit skill; `apply-patch` becomes a low-level patch-format support skill.
- Test cases: Manual trigger review: a request to edit files should match `edit-orchestration`; a request about patch grammar or failed hunk syntax should still match `apply-patch`.
- Pre-check commands: Run `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`.
- Post-check commands: Run `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/apply-patch`.
- Dependencies: Task 2, Task 3, and Task 4.
- Files likely touched: `apply-patch/SKILL.md`; `apply-patch/agents/openai.yaml`; `.codex/work/20260621-edit-orchestration-skill/artifacts/task5-coexistence.md`.
- Writable scope: `apply-patch/SKILL.md`; `apply-patch/agents/openai.yaml`; `.codex/work/20260621-edit-orchestration-skill/artifacts/task5-coexistence.md`.
- Output artifact: `.codex/work/20260621-edit-orchestration-skill/artifacts/task5-coexistence.md`
- Estimated scope: S

### Task 6: Validate, forward-test, and review

- Description: Run structural validation, script smoke checks, route scenario review, and an independent review pass before treating the new skill as ready.
- Worker role: review
- Wave: 5
- Acceptance criteria: Skill validator passes for `edit-orchestration` and `apply-patch`; plan dry-run passes if `codex2codex/scripts/run_plan.py` accepts this plan; forward-test notes cover at least four route scenarios; review artifact states `PASS` or `FAIL`.
- Verification: Run `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`, `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/apply-patch`, `python3 codex2codex/scripts/run_plan.py .codex/work/20260621-edit-orchestration-skill/plan.md --dry-run`, and `python3 edit-orchestration/scripts/prepare_edit_tools.py --list`.
- Concrete edits: Write validation results to `.codex/work/20260621-edit-orchestration-skill/review.md`; write route forward-test notes to `.codex/work/20260621-edit-orchestration-skill/artifacts/task6-forward-test.md`.
- Interfaces / contracts changed: No production interface change; this task validates the new trigger and route contracts.
- Test cases: Fast path request, patch failure request, structural rewrite request, selected-route self-check failure request, generated-output request.
- Pre-check commands: Run `git status --short`.
- Post-check commands: Run `git diff -- edit-orchestration apply-patch .codex/work/20260621-edit-orchestration-skill`.
- Dependencies: Task 1, Task 2, Task 3, Task 4, and Task 5.
- Files likely touched: `.codex/work/20260621-edit-orchestration-skill/review.md`; `.codex/work/20260621-edit-orchestration-skill/artifacts/task6-forward-test.md`.
- Writable scope: `.codex/work/20260621-edit-orchestration-skill/review.md`; `.codex/work/20260621-edit-orchestration-skill/artifacts/task6-forward-test.md`.
- Output artifact: `.codex/work/20260621-edit-orchestration-skill/review.md`
- Estimated scope: M

## Step-by-Step Plan
1. Run `test ! -e /data/lcq/.codex/skills/edit-orchestration` to protect existing skill state.
2. Run `python3 .system/skill-creator/scripts/init_skill.py edit-orchestration --path /data/lcq/.codex/skills --resources scripts,references --interface display_name="Edit Orchestration" --interface short_description="Route file edits through safe fast and heavy paths." --interface default_prompt="Use this skill when editing files; classify risk, prepare helper tools when selected, inspect diff, verify."`.
3. Save scaffold evidence to `.codex/work/20260621-edit-orchestration-skill/artifacts/task1-scaffold.md`.
4. Edit `edit-orchestration/SKILL.md` so frontmatter triggers on all manual file-edit tasks and body defines `preflight`, route selection, `diff gate`, `verification gate`, and `stop path`.
5. Add `edit-orchestration/references/route-matrix.md` with route predicates for `fast path`, `patch recovery path`, `agent-edit path`, `review-before-apply path`, `structural rewrite path`, and `generated-output path`.
6. Add `edit-orchestration/references/tooling.md` with user-level install roots `$CODEX_HOME/tools`, `~/.local/bin`, and project `.codex/tools`.
7. Add `edit-orchestration/references/failure-recovery.md` with raw whitespace reads using `sed -n '120,150l' file` and `nl -ba file | sed -n '120,150p'`.
8. Add `edit-orchestration/scripts/prepare_edit_tools.py` with CLI flags `--tool`, `--root`, `--check-only`, and `--list`.
9. Add `edit-orchestration/scripts/self_check_edit_tools.py` with CLI flags `--tool`, `--root`, and `--json`.
10. Run `python3 edit-orchestration/scripts/prepare_edit_tools.py --help`.
11. Run `python3 edit-orchestration/scripts/self_check_edit_tools.py --help`.
12. Run `python3 edit-orchestration/scripts/prepare_edit_tools.py --list`.
13. Add `edit-orchestration/references/examples.md` with one compact example per route.
14. Run `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`.
15. If `edit-orchestration` validation passes, edit `apply-patch/SKILL.md` frontmatter to narrow it to patch grammar and failure recovery support.
16. Run `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/apply-patch`.
17. Run `python3 codex2codex/scripts/run_plan.py .codex/work/20260621-edit-orchestration-skill/plan.md --dry-run`.
18. Write final review verdict to `.codex/work/20260621-edit-orchestration-skill/review.md`.

## Parallelization
- Wave 1 is sequential because scaffold creates shared directories.
- Wave 2 can split Task 2 and Task 3 if workers coordinate only through documented contracts: Task 2 writes `SKILL.md` and reference docs; Task 3 writes script files and appends only the script contract section to `tooling.md` after Task 2 creates it.
- Wave 3 waits for Wave 2 because examples must cite stable routes and script flags.
- Wave 4 waits for validation because old trigger narrowing is unsafe before the replacement exists.
- Wave 5 is review-only and can run after all implementation tasks complete.

## Files / Components Likely Affected
- `edit-orchestration/SKILL.md`
- `edit-orchestration/agents/openai.yaml`
- `edit-orchestration/references/route-matrix.md`
- `edit-orchestration/references/tooling.md`
- `edit-orchestration/references/failure-recovery.md`
- `edit-orchestration/references/examples.md`
- `edit-orchestration/scripts/prepare_edit_tools.py`
- `edit-orchestration/scripts/self_check_edit_tools.py`
- `apply-patch/SKILL.md`
- `apply-patch/agents/openai.yaml`
- `.codex/work/20260621-edit-orchestration-skill/artifacts/task1-scaffold.md`
- `.codex/work/20260621-edit-orchestration-skill/artifacts/task2-protocol.md`
- `.codex/work/20260621-edit-orchestration-skill/artifacts/task3-tooling.md`
- `.codex/work/20260621-edit-orchestration-skill/artifacts/task4-examples.md`
- `.codex/work/20260621-edit-orchestration-skill/artifacts/task5-coexistence.md`
- `.codex/work/20260621-edit-orchestration-skill/artifacts/task6-forward-test.md`
- `.codex/work/20260621-edit-orchestration-skill/review.md`

## Owners / Responsibilities
- Coding worker: Task 1 scaffold, Task 2 protocol, Task 3 scripts, Task 4 examples, Task 5 coexistence metadata.
- Review worker: Task 6 validation, forward-test assessment, `PASS` or `FAIL` verdict.
- Main agent: consolidate artifacts, inspect final diff, report verification status, and stop if selected-route self-check or validation fails.

## Validation Plan
- Run `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-edit-orchestration-skill/plan.md --mode light` before executing the plan.
- Run `python3 codex2codex/scripts/run_plan.py .codex/work/20260621-edit-orchestration-skill/plan.md --dry-run` before delegating workers.
- Run `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration` after creating or editing the new skill.
- Run `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/apply-patch` after narrowing old metadata.
- Run `python3 edit-orchestration/scripts/prepare_edit_tools.py --list`.
- Run `python3 edit-orchestration/scripts/self_check_edit_tools.py --help`.
- Run `git diff -- edit-orchestration apply-patch .codex/work/20260621-edit-orchestration-skill` and inspect diff against the spec.

## Rollout Plan
- Phase 1: Add `edit-orchestration` beside `apply-patch`.
- Phase 2: Validate skill structure and scripts.
- Phase 3: Forward-test route behavior on representative prompts without editing production code outside the skill workspace.
- Phase 4: Narrow `apply-patch` metadata after `edit-orchestration` validates.
- Phase 5: Report final status and keep rollback simple by leaving old skill files available.

## Monitoring / Observability
- Record task outputs under `.codex/work/20260621-edit-orchestration-skill/artifacts/`.
- Record final review under `.codex/work/20260621-edit-orchestration-skill/review.md`.
- Record tool versions in `$CODEX_HOME/tools/edit-orchestration/manifest.json` when tool preparation runs during future use.
- Monitor future user-visible incidents through the existing Skill Monitor convention in `AGENTS.md`.

## Documentation / ADR Updates
ADR: Needed

Add an ADR-style note inside `edit-orchestration/references/tooling.md` or `edit-orchestration/references/route-matrix.md` explaining why the system chooses route orchestration plus lazy user-level tooling instead of replacing Codex with a full external agent.

## Rollback / Recovery Plan
- If scaffold is wrong before old metadata changes, delete the newly created `edit-orchestration/` directory and leave `apply-patch/` untouched.
- If script validation fails, revert only `edit-orchestration/scripts/prepare_edit_tools.py` and `edit-orchestration/scripts/self_check_edit_tools.py`, then rerun `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration`.
- If `apply-patch` narrowing causes trigger regressions, restore the prior `apply-patch/SKILL.md` description from git diff or the pre-change artifact `.codex/work/20260621-edit-orchestration-skill/artifacts/task5-coexistence.md`.
- If forward-test review fails, keep `edit-orchestration` installed but do not narrow `apply-patch` until review findings are fixed.

## Abort Criteria
- `edit-orchestration/` already exists before Task 1.
- `python3 .system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/edit-orchestration` fails after one focused fix attempt.
- Tool preparation script requires `sudo`, system package manager writes, or non-user-level paths.
- Selected-route self-check failure is hidden behind fallback behavior.
- `git diff -- edit-orchestration apply-patch` shows unrelated changes outside the planned files.
- Review artifact `.codex/work/20260621-edit-orchestration-skill/review.md` says `FAIL`.

## Risks
- Trigger conflict between `edit-orchestration` and `apply-patch`: mitigate by creating the new skill first, validating, then narrowing old metadata.
- Toolchain bloat: mitigate by lazy route-specific setup and `--check-only` support.
- Network install instability: mitigate by pinned or recorded versions and stop-on-failure behavior.
- Overcomplicated skill body: mitigate by keeping route/tool details in references and checking `wc -l edit-orchestration/SKILL.md`.
- False-positive route confidence: mitigate through route examples and forward-test review.

## Open Questions
- Whether OpenRewrite should be fully script-supported in v1 or documented as a deferred route helper.
- Whether `aider` invocation should be scripted in v1 or limited to documented route preparation until a real complex edit needs it.
- Whether the old `apply-patch` `agents/openai.yaml` should be regenerated or manually aligned after frontmatter narrowing.

## Plan Self-Review
- Writable scope check: all tasks list exact paths; same-wave implementation tasks have non-overlapping scopes except the `tooling.md` contract note, which is controlled by Task 2 creating docs and Task 3 writing scripts.
- Coverage check: behavior changes have skill validator checks, script smoke checks, route manual checks, plan dry-run, and review artifact.
- Unknown check: OpenRewrite, `aider` invocation depth, and old metadata regeneration are explicit Open Questions.
- Rollback check: rollback names exact directories, files, commands, and artifacts.
- Task 1 check: a fresh agent can start with `test ! -e /data/lcq/.codex/skills/edit-orchestration` and the scaffold command without raw transcript context.

## Execution Decision
Do not execute implementation yet. This plan is ready for review, `spec2plan` validation, and optional conversion into worker tasks through `codex2codex/scripts/run_plan.py --dry-run`.

## Execution Handoff

- Goal: Build and validate `edit-orchestration` as the new default manual-edit orchestration skill.
- Current state: Confirmed spec exists; implementation has not started; `edit-orchestration/` was absent when inspected.
- Authoritative artifacts: `.codex/work/20260621-edit-orchestration-skill/spec.md`; `.codex/work/20260621-edit-orchestration-skill/plan.md`; `apply-patch/SKILL.md`; `.system/skill-creator/scripts/init_skill.py`; `.system/skill-creator/scripts/quick_validate.py`.
- Decisions: Use light planning mode; skill name `edit-orchestration`; create new skill before narrowing `apply-patch`; use user-level lazy tool preparation; stop on selected-route self-check failure.
- Verification: Run `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-edit-orchestration-skill/plan.md --mode light` and `python3 codex2codex/scripts/run_plan.py .codex/work/20260621-edit-orchestration-skill/plan.md --dry-run`.
- Remaining risks: Trigger overlap, helper tool bloat, network install failure, and overcomplicated SKILL.md.
- Next action: Validate this plan, then implement Task 1.
- Suggested skills: `context-engineering`, `skill-creator`, `apply-patch`, `test-driven-development`, `codex-agent-team:team-review-cycle`.
- Redactions / omitted raw data: Prior web-search details and long chat reasoning omitted; use confirmed spec and inspected file paths as source of truth.
