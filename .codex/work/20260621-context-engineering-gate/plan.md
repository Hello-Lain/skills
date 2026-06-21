# Context Engineering Gate Implementation Plan

Mode: light
Risk level: Medium
Confidence: High

## Goal
将 `/data/lcq/.codex/skills/context-engineering` 改造成更轻、更可执行的上下文治理 skill：`SKILL.md` 小于 10,000 字符，详细策略下沉到 references，新增 stdlib-only `scripts/context_gate.py`，并用自检与 replay 证明 plan 执行默认使用 wave-level pack，只有风险、歧义、失败、跨范围任务才升级到 task-level pack。

## Non-Goals
- 不实现真实 `/compact` actuator。
- 不修改 `spec2plan`、`plan2do`、`debug-skill` 或其他 skill。
- 不引入 LangGraph、Letta、AutoGen、SWE-agent、CUE、Pydantic 或第三方 Python runtime。
- 不删除历史 `.codex/work/20260621-plan-contract-fail-fast/` artifacts。
- 不强制每个任务都写 context artifact。

## Evidence Inspected
- `/data/lcq/.codex/skills/.codex/work/20260621-context-engineering-gate/spec.md`
- `/data/lcq/.codex/skills/.codex/work/20260621-context-engineering-gate/manifest.yaml`
- `/data/lcq/.codex/skills/context-engineering/SKILL.md`
- `/data/lcq/.codex/skills/spec2plan/SKILL.md`
- `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- `/data/lcq/.codex/skills/references/artifact-contract.md`
- `/data/lcq/.codex/skills/plan2do/SKILL.md`
- `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- `/data/lcq/.codex/skills/plan2do/references/failure-policy.md`
- `/data/lcq/.codex/skills/plan2do/references/review-rubric.md`
- `/data/lcq/.codex/skills/edit-orchestration/SKILL.md`
- `/data/lcq/.codex/skills/edit-orchestration/references/route-matrix.md`
- `/data/lcq/.codex/skills/.system/skill-creator/SKILL.md`
- `/data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/context-task1.md`
- `/data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/context-task2.md`
- `/data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/context-task3.md`
- `/data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/context-task4.md`
- `/data/lcq/.codex/skills/.codex/work/20260621-plan-contract-fail-fast/artifacts/context-task5.md`

## Spec Summary
目标 skill 需要保留 `lite`、`full`、`escalate`、Source Hierarchy、Context Starvation Guard、Decision Packet、Context Capsule、compaction safety、anti-pollution、conflict handling，同时减少入口文件负载。新增 gate 必须输出 `internal`、`wave-pack`、`task-pack`、`decision-packet`、`capsule`、`compact-request`，并通过自测覆盖 routine、plan wave、failure、decision-critical、high-pressure phase-boundary 场景。

## Domain Language Check
- 使用现有术语：`lite`、`full`、`escalate`、Source Hierarchy、Context Starvation Guard、Focused Context Pack、Decision Packet、Context Capsule、COMPACT_NOW。
- 新增术语：`context gate` 表示 advisory deterministic policy helper，不替代 agent 判断。
- 外部项目复用为 pattern-only：LangGraph state/checkpoint、Letta working/archive memory、SWE-agent trajectory/replay、AutoGen agent-state/message abstraction。
- 未发现术语冲突。

## Current Context
- `context-engineering/SKILL.md` 当前约 `15262` 字符，超过目标。
- 目标 skill 目录当前只有 `SKILL.md`，没有 `scripts/`、`references/`、`agents/openai.yaml`。
- 工作树已有 `context-engineering/SKILL.md` 修改，执行前必须从磁盘重读并保留现有语义，不做盲目覆盖。
- `.codex/work/20260621-context-engineering-gate/` 是本任务 canonical workspace。

## Implementation Map
- Files:
  - `context-engineering/SKILL.md`: 重写为精简入口、路由、gate 使用说明。
  - `context-engineering/references/modes.md`: 保存模式、Source Hierarchy、Starvation Guard、Decision Packet、Capsule、compaction、conflict handling 细节。
  - `context-engineering/references/artifact-policy.md`: 保存 artifact 决策、plan 执行 pack 粒度、anti-pollution、external inspiration pattern-only 说明。
  - `context-engineering/references/replay.md`: 保存 `plan-contract-fail-fast` replay 评估和预期 gate 输出。
  - `context-engineering/scripts/context_gate.py`: stdlib-only policy helper 与 self-test。
  - `.codex/work/20260621-context-engineering-gate/artifacts/`: 保存 context pack、task execution、verification、review、final report。
- Symbols / APIs:
  - `context_gate.py` CLI args: `--self-test`, `--json`, `--scenario`, `--phase`, `--plan-tasks`, `--task-risk`, `--failure`, `--ambiguity`, `--cross-cutting`, `--decision-critical`, `--context-pressure`, `--phase-boundary`, `--compact-ready`.
  - Gate actions: `internal`, `wave-pack`, `task-pack`, `decision-packet`, `capsule`, `compact-request`.
- Tests:
  - `python3 -m py_compile /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py`
  - `python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --self-test`
  - `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/context-engineering`
  - `python3 - <<'PY' ...` character-count check for `SKILL.md`.
- Commands:
  - Pre-check: `git status --short -- context-engineering .codex/work/20260621-context-engineering-gate`
  - Post-checks: validation commands listed in `Validation Plan`.
- Data / migration impact:
  - Not applicable: no app data, DB, schema, secrets, or runtime migration touched.

## Assumptions
- `agents/openai.yaml` absence is acceptable unless quick validation or metadata drift requires creation.
- JSON output is the safest default for tool consumption; text summary remains available for humans.
- Machine-readable replay can live inside `context_gate.py --self-test` and human-readable replay can live in `references/replay.md`.
- Current user approval authorizes writing `plan.md`, skill files, script files, and plan artifacts inside allowed scope.

## User Inputs Needed
Not applicable: the confirmed spec resolves open questions by allowing JSON/text support and replay in references plus self-test.

## Proposed Approach
Use a small entrypoint `SKILL.md` that teaches trigger routing and when to invoke `scripts/context_gate.py`. Move policy depth into three references. Implement a deterministic but advisory Python gate with pure stdlib. Validate by compile, self-test, skill quick validation, character count, replay review, and independent PASS/FAIL review artifact.

## Scenario Probes
- Routine reversible edit: gate returns `internal` unless it is part of a multi-task wave that has not had a wave pack.
- Normal plan execution with multiple tasks: gate returns `wave-pack` once per wave, not per task.
- Failed command or patch miss: gate returns `task-pack` when a focused task context is needed, or `escalate` in explanation when risk plus missing evidence blocks action.
- Destructive/security/API/schema action: gate returns `decision-packet`.
- High context pressure at phase boundary: gate returns `capsule`, and returns `compact-request` after capsule exists or compact-ready flag is set.

## Dependency Graph
- Task 1 depends on current `SKILL.md`, spec, and replay artifact paths.
- Task 2 depends on Task 1 terminology and output action semantics.
- Task 3 depends on Tasks 1 and 2.
- Task 4 depends on Tasks 1-3 and validation evidence.

## Task Breakdown
### Task 1: Split context policy into entrypoint and references

- Description: Rewrite `context-engineering/SKILL.md` below 10,000 characters and add focused reference files preserving removed policy detail.
- Worker role: coding
- Wave: 1
- Acceptance criteria:
  - `context-engineering/SKILL.md` keeps core rule, mode choice, artifact decision rule, escalation triggers, reference routing, and gate command examples.
  - `context-engineering/references/modes.md` preserves Source Hierarchy, Context Starvation Guard, Decision Packet, Context Capsule, compaction safety, conflict handling.
  - `context-engineering/references/artifact-policy.md` states wave-pack default and task-pack escalation triggers.
  - `context-engineering/references/replay.md` documents `plan-contract-fail-fast` replay decision.
- Verification:
  - `python3 - <<'PY'` char-count snippet confirms `context-engineering/SKILL.md` is below `10000`.
  - Manual review compares removed policy areas against new references.
- Concrete edits:
  - Create `context-engineering/references/modes.md`.
  - Create `context-engineering/references/artifact-policy.md`.
  - Create `context-engineering/references/replay.md`.
  - Replace `context-engineering/SKILL.md` with slim entrypoint.
- Interfaces / contracts changed:
  - Skill loading contract remains same name and description.
  - New optional reference routing paths are introduced.
- Test cases:
  - Manual preservation check for Source Hierarchy, Starvation Guard, Decision Packet, Capsule, compaction safety, anti-pollution, conflict handling.
- Pre-check commands:
  - `git status --short -- context-engineering .codex/work/20260621-context-engineering-gate`
  - `sed -n '1,260p' /data/lcq/.codex/skills/context-engineering/SKILL.md`
- Post-check commands:
  - `python3 - <<'PY'
from pathlib import Path
p=Path("/data/lcq/.codex/skills/context-engineering/SKILL.md")
print(len(p.read_text()))
assert len(p.read_text()) < 10000
PY`
- Dependencies:
  - None.
- Files likely touched:
  - `context-engineering/SKILL.md`
  - `context-engineering/references/modes.md`
  - `context-engineering/references/artifact-policy.md`
  - `context-engineering/references/replay.md`
  - `.codex/work/20260621-context-engineering-gate/artifacts/context-task1.md`
  - `.codex/work/20260621-context-engineering-gate/artifacts/task1-execution.md`
- Writable scope:
  - `context-engineering/SKILL.md`
  - `context-engineering/references/modes.md`
  - `context-engineering/references/artifact-policy.md`
  - `context-engineering/references/replay.md`
  - `.codex/work/20260621-context-engineering-gate/artifacts/context-task1.md`
  - `.codex/work/20260621-context-engineering-gate/artifacts/task1-execution.md`
- Output artifact:
  - `.codex/work/20260621-context-engineering-gate/artifacts/task1-execution.md`
- Estimated scope: M

### Task 2: Add deterministic context gate

- Description: Add stdlib-only `context_gate.py` with deterministic advisory action selection and built-in self-tests.
- Worker role: coding
- Wave: 2
- Acceptance criteria:
  - CLI supports `--self-test` and direct scenario flags.
  - Direct outputs include `internal`, `wave-pack`, `task-pack`, `decision-packet`, `capsule`, `compact-request`.
  - Self-test covers routine, multi-task plan, failure, decision-critical, and high-pressure phase-boundary cases.
  - Script has no third-party imports.
- Verification:
  - `python3 -m py_compile /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py`
  - `python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --self-test`
- Concrete edits:
  - Create `context-engineering/scripts/context_gate.py`.
  - Add executable-style CLI help text and JSON/text output.
- Interfaces / contracts changed:
  - New local helper CLI under skill resources.
- Test cases:
  - Routine reversible scenario.
  - Multi-task plan execution scenario.
  - Failed command or patch miss scenario.
  - Destructive/security/API/schema scenario.
  - High context pressure with phase boundary scenario.
- Pre-check commands:
  - `test ! -e /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py || sed -n '1,260p' /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py`
- Post-check commands:
  - `python3 -m py_compile /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py`
  - `python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --self-test`
- Dependencies:
  - Task 1.
- Files likely touched:
  - `context-engineering/scripts/context_gate.py`
  - `.codex/work/20260621-context-engineering-gate/artifacts/context-task2.md`
  - `.codex/work/20260621-context-engineering-gate/artifacts/task2-execution.md`
- Writable scope:
  - `context-engineering/scripts/context_gate.py`
  - `.codex/work/20260621-context-engineering-gate/artifacts/context-task2.md`
  - `.codex/work/20260621-context-engineering-gate/artifacts/task2-execution.md`
- Output artifact:
  - `.codex/work/20260621-context-engineering-gate/artifacts/task2-execution.md`
- Estimated scope: M

### Task 3: Validate skill package and replay behavior

- Description: Run full acceptance checks, store verification evidence, and update metadata only if validation proves it necessary.
- Worker role: coding
- Wave: 3
- Acceptance criteria:
  - `quick_validate.py` passes.
  - `context_gate.py --self-test` passes.
  - `py_compile` passes.
  - Character count is below 10,000.
  - Replay reference and self-test confirm wave-pack default for normal plan execution.
- Verification:
  - `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/context-engineering`
  - `python3 -m py_compile /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py`
  - `python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --self-test`
  - `python3 - <<'PY'
from pathlib import Path
p=Path("/data/lcq/.codex/skills/context-engineering/SKILL.md")
print(len(p.read_text()))
assert len(p.read_text()) < 10000
PY`
- Concrete edits:
  - Write `.codex/work/20260621-context-engineering-gate/artifacts/task3-verification.md`.
  - Create or update `context-engineering/agents/openai.yaml` only if a validator demands it.
- Interfaces / contracts changed: Not applicable - validation does not change external skill contract.
- Test cases:
  - All script self-test cases from Task 2.
  - Skill folder validation.
- Pre-check commands:
  - `find /data/lcq/.codex/skills/context-engineering -maxdepth 3 -type f | sort`
- Post-check commands:
  - `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/context-engineering`
  - `python3 -m py_compile /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py`
  - `python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --self-test`
- Dependencies:
  - Task 2.
- Files likely touched:
  - `.codex/work/20260621-context-engineering-gate/artifacts/context-task3.md`
  - `.codex/work/20260621-context-engineering-gate/artifacts/task3-verification.md`
  - `context-engineering/agents/openai.yaml`
- Writable scope:
  - `.codex/work/20260621-context-engineering-gate/artifacts/context-task3.md`
  - `.codex/work/20260621-context-engineering-gate/artifacts/task3-verification.md`
  - `context-engineering/agents/openai.yaml`
- Output artifact:
  - `.codex/work/20260621-context-engineering-gate/artifacts/task3-verification.md`
- Estimated scope: S

### Task 4: Review and final execution report

- Description: Perform PASS/FAIL review against acceptance criteria, check diff scope, validate execution checklist, and write final report.
- Worker role: review
- Wave: 4
- Acceptance criteria: Review artifact has a terminal verdict, final report lists changed files and command outcomes, and execution validation passes.
  - Review artifact contains exactly one terminal `Verdict: PASS` or `Verdict: FAIL`.
  - Final report lists changed files, commands, outcomes, review verdict, artifacts, and residual risks.
  - `validate_execution.py` passes after compiled tasks are complete.
- Verification:
  - `git diff -- context-engineering .codex/work/20260621-context-engineering-gate`
  - `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-context-engineering-gate`
- Concrete edits:
  - Write `.codex/work/20260621-context-engineering-gate/review.md`.
  - Write `.codex/work/20260621-context-engineering-gate/artifacts/final-report.md`.
- Interfaces / contracts changed: Not applicable - review/report artifacts only.
- Test cases:
  - Review rubric PASS/FAIL conditions.
  - Execution checklist validation.
- Pre-check commands:
  - `git diff --stat -- context-engineering .codex/work/20260621-context-engineering-gate`
- Post-check commands:
  - `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-context-engineering-gate`
- Dependencies:
  - Task 3.
- Files likely touched:
  - `.codex/work/20260621-context-engineering-gate/review.md`
  - `.codex/work/20260621-context-engineering-gate/artifacts/final-report.md`
- Writable scope:
  - `.codex/work/20260621-context-engineering-gate/review.md`
  - `.codex/work/20260621-context-engineering-gate/artifacts/final-report.md`
- Output artifact:
  - `.codex/work/20260621-context-engineering-gate/review.md`
- Estimated scope: S

## Step-by-Step Plan
1. Run `git status --short -- context-engineering .codex/work/20260621-context-engineering-gate`.
2. Create `.codex/work/20260621-context-engineering-gate/artifacts/context-task1.md`.
3. Re-read `/data/lcq/.codex/skills/context-engineering/SKILL.md`.
4. Create `context-engineering/references/modes.md`.
5. Create `context-engineering/references/artifact-policy.md`.
6. Create `context-engineering/references/replay.md`.
7. Replace `context-engineering/SKILL.md` with slim routing entrypoint.
8. Run the `SKILL.md` character-count Python snippet.
9. Write `.codex/work/20260621-context-engineering-gate/artifacts/task1-execution.md`.
10. Create `.codex/work/20260621-context-engineering-gate/artifacts/context-task2.md`.
11. Create `context-engineering/scripts/context_gate.py`.
12. Run `python3 -m py_compile /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py`.
13. Run `python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --self-test`.
14. Write `.codex/work/20260621-context-engineering-gate/artifacts/task2-execution.md`.
15. Create `.codex/work/20260621-context-engineering-gate/artifacts/context-task3.md`.
16. Run `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/context-engineering`.
17. Re-run `py_compile`, `--self-test`, and char-count checks.
18. Write `.codex/work/20260621-context-engineering-gate/artifacts/task3-verification.md`.
19. Review `git diff -- context-engineering .codex/work/20260621-context-engineering-gate`.
20. Write `.codex/work/20260621-context-engineering-gate/review.md`.
21. Write `.codex/work/20260621-context-engineering-gate/artifacts/final-report.md`.
22. Run `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-context-engineering-gate`.

## Parallelization
Sequential execution is safest. Task 1 defines the reference vocabulary, Task 2 depends on those semantics, Task 3 depends on the script and docs, and Task 4 depends on all validation evidence. No same-wave writable scopes overlap because each wave has one task.

## Files / Components Likely Affected
- `context-engineering/SKILL.md`
- `context-engineering/references/modes.md`
- `context-engineering/references/artifact-policy.md`
- `context-engineering/references/replay.md`
- `context-engineering/scripts/context_gate.py`
- `.codex/work/20260621-context-engineering-gate/plan.md`
- `.codex/work/20260621-context-engineering-gate/manifest.yaml`
- `.codex/work/20260621-context-engineering-gate/artifacts/context-task1.md`
- `.codex/work/20260621-context-engineering-gate/artifacts/context-task2.md`
- `.codex/work/20260621-context-engineering-gate/artifacts/context-task3.md`
- `.codex/work/20260621-context-engineering-gate/artifacts/task1-execution.md`
- `.codex/work/20260621-context-engineering-gate/artifacts/task2-execution.md`
- `.codex/work/20260621-context-engineering-gate/artifacts/task3-verification.md`
- `.codex/work/20260621-context-engineering-gate/review.md`
- `.codex/work/20260621-context-engineering-gate/artifacts/final-report.md`

## Owners / Responsibilities
- Main agent: primary-agent implementation, validation, review, artifacts, final acceptance.
- `spec2plan`: owns this `plan.md` and plan validation.
- `plan2do`: owns execution discipline after plan validation and compilation.
- User: no input required unless scope changes, destructive action appears, or validation blocks.

## Validation Plan
- Plan validation: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-context-engineering-gate/plan.md --mode light`
- Execution compile: `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-context-engineering-gate/plan.md`
- Skill validation: `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/context-engineering`
- Script compile: `python3 -m py_compile /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py`
- Script self-test: `python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --self-test`
- Character count: Python snippet with `assert len(SKILL.md text) < 10000`.
- Execution validation: `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-context-engineering-gate`

## Rollout Plan
Local skill files are updated in place under `/data/lcq/.codex/skills/context-engineering`. After validation, future Codex turns discover the same skill name and load the leaner `SKILL.md`; references and script are available on demand.

## Monitoring / Observability
- Validation artifacts under `.codex/work/20260621-context-engineering-gate/artifacts/` record commands and outcomes.
- `context_gate.py --self-test` acts as regression smoke test.
- `references/replay.md` records the expected behavior for the prior over-artifact scenario.
- Future `debug-skill` audits can compare actual plan executions against gate recommendations.

## Documentation / ADR Updates
ADR: Not needed. This is a local skill workflow change with self-contained references. Documentation updates happen inside `context-engineering/SKILL.md` and `context-engineering/references/*.md`.

## Rollback / Recovery Plan
- If `SKILL.md` loses critical behavior, restore missing semantics from the current file content preserved in this plan's inspected evidence and new references.
- If `context_gate.py` fails self-test, patch only `context-engineering/scripts/context_gate.py`, then rerun `py_compile` and `--self-test`.
- If `quick_validate.py` fails, patch frontmatter or folder structure only, then rerun skill validation.
- If final review fails, write rework guidance under `.codex/work/20260621-context-engineering-gate/artifacts/rework-guidance.md` and run one bounded fix cycle.
- If scope would expand outside allowed paths, stop with `SCOPE_VIOLATION`.

## Abort Criteria
- `context-engineering/SKILL.md` cannot be reduced below 10,000 characters without removing required semantics.
- `context_gate.py --self-test` cannot pass without third-party dependencies.
- `quick_validate.py` reports a structural failure that requires changing Codex skill discovery rules.
- Current target files conflict with user changes in a way that makes preservation unsafe.
- Required edits would touch files outside `context-engineering/` and `.codex/work/20260621-context-engineering-gate/` except validator-required metadata inside `context-engineering/agents/openai.yaml`.

## Risks
- Over-compression hides safety semantics. Mitigation: preserve details in references and manually verify named core semantics.
- Gate becomes rigid. Mitigation: keep output advisory and include escalation reasons.
- Agents skip references. Mitigation: `SKILL.md` routes by trigger and names exact reference files.
- Artifact policy under-captures failures. Mitigation: task-pack triggers include failure, ambiguity, confidence loss, risk, and cross-cutting scope.

## Open Questions
Not applicable: implementation proceeds with JSON plus text output and replay in both `references/replay.md` and `context_gate.py --self-test`.

## Plan Self-Review
- Every task has exact writable scope and no same-wave overlap.
- Every behavior change has compile, self-test, quick validation, replay, character-count, and review coverage.
- Unknowns are listed in `Assumptions` or resolved in `User Inputs Needed`.
- Rollback, abort criteria, and monitoring are specific enough for local skill edits.
- A fresh agent can execute Task 1 from this plan using source paths and commands above.

## Execution Decision
Proceed with primary-agent `plan2do` execution after this plan passes light validation and `compile_execution.py` succeeds.

## Execution Handoff

- Goal: Implement the confirmed Context Engineering Gate spec.
- Current state: Spec exists; plan generated; target skill has only `SKILL.md` and exceeds target size.
- Authoritative artifacts: `.codex/work/20260621-context-engineering-gate/spec.md`, `.codex/work/20260621-context-engineering-gate/plan.md`, `context-engineering/SKILL.md`.
- Decisions: Use light spec2plan, primary-agent plan2do, stdlib-only script, reference split, no third-party runtime.
- Verification: Run plan validator, compile execution, quick_validate, py_compile, self-test, char count, review, validate_execution.
- Remaining risks: Preserve safety semantics while shrinking entrypoint; avoid overfitting gate to one replay.
- Next action: Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-context-engineering-gate/plan.md --mode light`.
- Suggested skills: `plan2do`, `context-engineering`, `edit-orchestration`, `skill-creator`.
- Redactions / omitted raw data: Raw command output and diffs stay in artifacts, not in final response.
