SPEC2PLAN_ARTIFACT_V1
phase: planner
status: complete
artifact:
# codex2codex 上下文防火墙执行协议重构计划

## Goal

- Mode: heavy
- Risk level: High
- Confidence: High
- 目标：将 `codex2codex` 从“worker runner”重构为“context firewall execution protocol”，让未来 lead/main agent 默认只读取有界 `run-capsule.json` / `run-capsule.md`，显著降低主线程上下文 token，同时保持或增强实现、审查、验证质量。
- 计划输出路径：`/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/plan.md`
- 任务输出 artifact 路径：`.codex/work/20260620-codex2codex-context-firewall/artifacts/`
- Review artifact 路径：`.codex/work/20260620-codex2codex-context-firewall/review*.md`

## Non-Goals

- 不实现代码；本计划仅供后续 `$codex2codex` 执行。
- 不删除现有 raw worker artifacts、`result.md`、`events.log` 或 `execution-state.json`；只改变 lead 默认消费面。
- 不用 capsule 替代独立 review；review PASS 仍是质量门。
- 不让 lead 合成缺失 worker/review 工作；缺失即失败或 fix wave。
- 不把 blackboard/council 默认用于所有任务；仅复杂/高风险任务启用。
- 不优先做 Dashboard/UI；协议、schema、validator、runner 输出优先。

## Evidence Inspected

- `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/idea.md`
- `/data/lcq/.codex/skills/codex2codex/SKILL.md`
- `/data/lcq/.codex/skills/codex2codex/ARCHITECTURE.md`
- `/data/lcq/.codex/skills/codex2codex/scripts/run_plan.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/run_wave.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/plan_to_tasks.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/prepare_wave.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/execution_state.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/validate_execution_complete.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/validate_wave.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/validate_result_contract.py`
- `/data/lcq/.codex/skills/codex2codex/scripts/test_execution_completion.py`
- `/data/lcq/.codex/skills/codex2codex/roles/_defaults.yaml`
- `/data/lcq/.codex/skills/codex2codex/roles/coding.yaml`
- `/data/lcq/.codex/skills/codex2codex/roles/review.yaml`
- `/data/lcq/.codex/skills/codex2codex/roles/consult.yaml`
- `/data/lcq/.codex/skills/codex2codex/roles/sa.yaml`
- `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- `/data/lcq/.codex/skills/spec2plan/references/heavy-mode.md`
- `/data/lcq/.codex/skills/references/artifact-contract.md`

## Spec Summary

- 推荐方向：把 `codex2codex` 明确建模为上下文防火墙执行协议。
- Lead 默认读取 bounded capsule：intent、waves、workers、artifacts、changed files、verification、review verdicts、risks、blockers、evidence ledger、cleanup。
- Raw worker transcript、长结果、fix-loop 细节保留在磁盘 artifact 后，通过路径/hash 引用，不进入主上下文。
- 质量保障两层：
  - 语义层：reviewer/gatekeeper workers 读取 raw detail，发现实现/测试/安全/接口问题。
  - 结构层：validators 校验 receipts、artifacts、review PASS、provenance、cleanup、capsule consistency、no raw transcript leakage。
- 复杂任务可启用 structured blackboard，让 worker 间共享风险、决策、问题、证据，而不是让 lead 中转所有细节。
- MVP 必须包含 canonical `run-capsule.json`、`run-capsule.md`、capsule validator、runner 集成、final execution validator 扩展、role prompt contract、context budget limits。

## Domain Language Check

- Canonical terms:
  - `lead agent` / `main agent`：统一指主编排 agent；文档中优先用 `lead agent`。
  - `worker` / `subagent`：统一指由 `meight`/`codex2codex` 启动的执行 agent；文档中优先用 `worker`，必要时括注 subagent。
  - `context firewall`：lead 默认只消费 capsule + evidence links，raw detail 留在 worker artifacts。
  - `run-capsule.json`：机器可验证摘要，validators 的主对象。
  - `run-capsule.md`：lead-facing 人类/agent 可读摘要，从 JSON 派生。
  - `evidence ledger`：capsule 中每个 claim 对应 artifact path、hash、validator、receipt。
  - `blackboard`：复杂模式中 worker 之间共享的结构化问题/风险/决策/证据区。
  - `review PASS/FAIL`：质量 gate，不被 dry-run 或 capsule 替代。
- Term conflicts:
  - `dry-run` 已明确是 compile-only，不得称为质量 gate。
  - `review-summary.md` 不是新 capsule；它可作为 evidence，但不是 lead-facing primary result。
  - `Handoff Capsule` 是旧 worker result contract；本计划的新 `run-capsule.*` 是 runner-level execution capsule。

## Current Context

- `run_plan.py` 当前负责编译 plan、顺序运行 waves、记录 plan compile/result；输出仍偏过程型，未生成 canonical run capsule。
- `run_wave.py` 当前负责 prepare/start/wait/validate/shutdown、recovery、fix wave、execution-state receipt；已有 context hygiene，但 lead-facing 结果不是 bounded capsule。
- `execution_state.py` 当前记录 plan/wave receipts、workers、cleanup；适合作为 capsule evidence 源，但缺少 capsule manifest/hash/budget 字段。
- `validate_execution_complete.py` 当前校验 execution-state、waves、artifacts、review PASS、summary_path、cleanup；未校验 capsule 一致性和 raw transcript 泄漏。
- `validate_wave.py` 当前校验 worker terminal state、output artifact、review artifact、implementation evidence；可扩展为 wave capsule/evidence consistency gate。
- `prepare_wave.py` 当前生成 role/profile-aware briefs；可注入 capsule/blackboard 规则和 raw-output 禁止规则。
- `roles/*.yaml` 已有 minimal context、review PASS/FAIL、skills policy；需加入 context firewall contract 和 concise artifact budgets。
- `plan_to_tasks.py` 从 `### Task N` 解析 role/wave/scope/verification/output；本计划任务字段按该 contract 编写，same-wave implementation scope 不重叠。

## Assumptions

- 用户已明确要求从 confirmed direction 直接进入 `spec2plan`，因此跳过 `interview-me`；缺失项以假设记录，不阻塞计划。
- 默认 capsule budget 假设：`run-capsule.md` 目标 ≤ 4k tokens，硬上限 ≤ 8k tokens；`run-capsule.json` 可略大但必须 bounded。
- PASS 场景下 lead 可只读 capsule；FAIL/blocker 场景 capsule 可包含更具体的 compact failure detail，但仍不粘贴 raw transcript。
- Capsule 由 deterministic runner code 生成，review/gatekeeper worker 提供语义质量判断；不让 LLM 独自生成不可验证 capsule。
- Blackboard 仅在 `--complex`、高风险、multi-wave、review FAIL fix loop、或显式 opt-in 时启用；普通任务保持低延迟。
- 现有 `.codex/specs/<slug>/` execution layout 保持兼容；本计划自身 task artifacts 放在 `.codex/work/20260620-codex2codex-context-firewall/`。
- 后续实现可新增小型 Python modules/scripts；不引入外部依赖，除非实现者证明 stdlib 不足。
- 旧 raw artifacts 继续保留，便于 debug/replay；rollback 可关闭 capsule enforcement 而不丢失执行证据。

## User Inputs Needed

- None blocking before implementation.
- 可后续调参：capsule token hard limit、complex-mode 启发式阈值、失败场景是否自动暴露更多 compact detail。
- 可后续决策：是否单独新增 ADR 文件；本计划默认在 `codex2codex/ARCHITECTURE.md` 记录 ADR 级决策。

## Proposed Approach

- 新增 capsule contract：
  - `run-capsule.json` 是 source of truth，包含 schema version、plan/wave ids、workers、artifacts、review verdicts、verification、changed files、risks、blockers、cleanup、evidence ledger、budget metrics。
  - `run-capsule.md` 从 JSON 派生，固定短 sections，作为 lead 默认阅读入口。
- 新增 capsule validator：
  - artifact 存在且非空；
  - review PASS 不可缺失或伪造；
  - dry-run 不可标记 complete；
  - 每个 capsule claim 必须链接 evidence；
  - 禁止 raw transcript/event dump 泄漏；
  - capsule budget 超限 fail 或 warning，按 mode 决定。
- Runner 集成：
  - `run_wave.py` 在每个 wave 完成后写/更新 wave capsule fragments、blackboard updates、execution-state capsule refs。
  - `run_plan.py` 汇总 wave capsules，最终输出 capsule path，减少 lead stdout。
  - `validate_execution_complete.py` 将 capsule consistency 纳入最终 gate。
- Meaningful worker interaction：
  - 普通模式：workers 不直接互聊；通过 artifacts、review、execution-state 间接交接。
  - Complex mode：runner 维护 structured blackboard，后续 worker briefs 只注入 compact blackboard digest；worker 可添加 risks/questions/decisions/evidence。
  - Reviewer/gatekeeper 读取 raw artifacts + blackboard，验证 capsule 是否隐藏 material risk。
- Compatibility/rollback：
  - 初期 additive：保留旧 artifacts 和 validators；
  - enforcement 可由 CLI flag/validator mode 控制；
  - 旧 plan/wave execution 不因缺少 capsule 被不可恢复破坏，除非显式启用新 final gate。

## Scenario Probes

- Simple PASS：单 wave coding + review PASS；lead stdout 只给 capsule paths，`validate_execution_complete.py` PASS。
- Missing artifact：worker terminal completed 但 output artifact 缺失；capsule validator FAIL，final validator FAIL。
- Review FAIL：review artifact `Verdict: FAIL`；capsule 必须显示 FAIL/blocker，不得总结为 success。
- Dry-run misuse：`run_plan.py --dry-run` 生成 compile-only output；capsule 不得声明 quality complete。
- Raw leak：worker `events.log` 或完整 `result.md` 内容进入 capsule；validator 必须 FAIL。
- Seeded defect：实现 artifact 声称通过但测试/changed files 不匹配；review/gatekeeper 或 validator 必须 FAIL。
- Complex blackboard：multi-wave task 中 worker A 记录风险，worker B/reviewer 能读取 compact digest 并响应，不需要 lead 中转 raw transcript。
- Budget pressure：长 fix loop 后 capsule 仍 bounded；evidence ledger 链接 raw artifacts，lead token 不随 loop 线性增长。
- Legacy compatibility：未启用 enforcement 的旧 spec dir 仍可用现有 artifacts debug；新 final gate 清晰提示缺 capsule。

## Dependency Graph

```text
Task 1 ─┬─> Task 3 ─┬─> Task 5 ─┬─> Task 7 ─┬─> Task 8 ─┬─> Task 10 ─┬─> Task 12 ─> Task 13
        │           │           │           │           └─> Task 9 ─┘            │
Task 2 ─┘           │           │           └───────────────────────> Task 10 ───┘
                    │           │
Task 4 ─────────────┴─> Task 6 ─┘
Task 11 depends on Task 7, Task 8, Task 9 and can run with Task 10.
```

- Gate A：Task 1-2 完成后锁定 capsule/blackboard contract。
- Gate B：Task 3-4 validators/tests 完成后才接 runner。
- Gate C：Task 7-9 完成后必须跑 focused unit tests。
- Gate D：Task 12 必须跑 plan dry-run、capsule validators、final execution validator。
- Gate E：Task 13 independent review 必须 PASS 才可交付。

## Task Breakdown

### Task 1: 确认上下文防火墙边界

- Description: 只读审查现有 runner、validators、roles、direction artifact，输出 capsule/lead/worker 边界建议和不能破坏的质量门。
- Worker role: consult
- Wave: 1
- Acceptance criteria:
  - 明确 lead 默认读取内容、raw evidence 保留位置、FAIL/blocker 展示规则。
  - 标出与现有 `SKILL.md` / `ARCHITECTURE.md` 的一致点和冲突点。
  - 给出 capsule schema 最小字段建议。
- Verification: `test -s .codex/work/20260620-codex2codex-context-firewall/artifacts/task-1-boundary.md`
- Dependencies: None
- Files likely touched: `codex2codex/SKILL.md`, `codex2codex/ARCHITECTURE.md`, `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/validate_execution_complete.py`
- Writable scope: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-1-boundary.md`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-1-boundary.md`
- Estimated scope: S

### Task 2: 设计验证与回放探针

- Description: 只读设计 regression probes、seeded defect cases、token budget checks、legacy compatibility checks。
- Worker role: consult
- Wave: 1
- Acceptance criteria:
  - 覆盖 PASS、FAIL、missing artifact、dry-run misuse、raw leak、blackboard complex mode。
  - 指定每类 probe 对应的 unit test 文件和 validator 命令。
  - 说明哪些 probe 必须 fail closed。
- Verification: `test -s .codex/work/20260620-codex2codex-context-firewall/artifacts/task-2-probes.md`
- Dependencies: None
- Files likely touched: `codex2codex/scripts/test_execution_completion.py`, `codex2codex/scripts/test_run_wave_recovery.py`, `codex2codex/scripts/test_worker_recovery_contracts.py`
- Writable scope: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-2-probes.md`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-2-probes.md`
- Estimated scope: S

### Task 3: 实现 capsule schema 与 validator

- Description: 新增 stdlib-only capsule module 和 CLI validator，定义 `run-capsule.json` / `run-capsule.md` schema、budget、evidence ledger、raw leak checks。
- Worker role: coding
- Wave: 2
- Acceptance criteria:
  - `capsule.py` 可构建、渲染、hash、token-estimate capsule。
  - `validate_capsule.py` 校验 schema version、required fields、artifact existence、review verdict consistency、budget、raw transcript leakage。
  - Unit tests 覆盖 valid capsule、missing evidence、raw leak、dry-run false PASS。
- Verification: `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_capsule_validator.py`
- Dependencies: Task 1, Task 2
- Files likely touched: `codex2codex/scripts/capsule.py`, `codex2codex/scripts/validate_capsule.py`, `codex2codex/scripts/test_capsule_validator.py`
- Writable scope: `codex2codex/scripts/capsule.py`, `codex2codex/scripts/validate_capsule.py`, `codex2codex/scripts/test_capsule_validator.py`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-3-capsule-validator.md`
- Estimated scope: M

### Task 4: 实现 complex-mode blackboard contract

- Description: 新增 structured blackboard module 和 validator，用于复杂任务中 worker 间共享 compact risks/questions/decisions/evidence。
- Worker role: coding
- Wave: 2
- Acceptance criteria:
  - `blackboard.py` 支持 append/read compact digest，字段固定且 bounded。
  - `validate_blackboard.py` 检查 schema、entry size、evidence links、无 raw transcript。
  - Unit tests 覆盖空 blackboard、风险追加、digest 截断、非法 raw dump。
- Verification: `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_blackboard.py`
- Dependencies: Task 1, Task 2
- Files likely touched: `codex2codex/scripts/blackboard.py`, `codex2codex/scripts/validate_blackboard.py`, `codex2codex/scripts/test_blackboard.py`
- Writable scope: `codex2codex/scripts/blackboard.py`, `codex2codex/scripts/validate_blackboard.py`, `codex2codex/scripts/test_blackboard.py`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-4-blackboard.md`
- Estimated scope: M

### Task 5: 扩展 execution-state receipts

- Description: 扩展 execution state，记录 capsule refs、capsule hashes、budget metrics、evidence ledger refs、blackboard refs，并保持旧 state 兼容。
- Worker role: coding
- Wave: 3
- Acceptance criteria:
  - 新字段缺失时旧 state 仍可读取。
  - wave/plan receipt 可记录 capsule path/hash/validation status。
  - Tests 覆盖 legacy state、new capsule receipts、failed wave receipts。
- Verification: `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_execution_capsule_state.py`
- Dependencies: Task 3
- Files likely touched: `codex2codex/scripts/execution_state.py`, `codex2codex/scripts/test_execution_capsule_state.py`
- Writable scope: `codex2codex/scripts/execution_state.py`, `codex2codex/scripts/test_execution_capsule_state.py`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-5-execution-state.md`
- Estimated scope: S

### Task 6: 注入 worker brief 与 role prompt 协议

- Description: 更新 wave preparation 和 role prompts，使 workers 输出 concise artifacts、避免 raw transcript、按复杂模式读写 blackboard digest。
- Worker role: coding
- Wave: 3
- Acceptance criteria:
  - `prepare_wave.py` brief 包含 context firewall restrictions、capsule/blackboard expectations、raw detail 禁止规则。
  - Roles 说明 reviewer/gatekeeper 必须检查 raw artifacts 与 capsule claim 一致性。
  - Tests 覆盖 normal mode 不注入 blackboard、complex mode 注入 compact digest。
- Verification: `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_prepare_wave_blackboard.py`
- Dependencies: Task 4
- Files likely touched: `codex2codex/scripts/prepare_wave.py`, `codex2codex/roles/_defaults.yaml`, `codex2codex/roles/coding.yaml`, `codex2codex/roles/review.yaml`, `codex2codex/roles/consult.yaml`, `codex2codex/roles/sa.yaml`, `codex2codex/scripts/test_prepare_wave_blackboard.py`
- Writable scope: `codex2codex/scripts/prepare_wave.py`, `codex2codex/roles/_defaults.yaml`, `codex2codex/roles/coding.yaml`, `codex2codex/roles/review.yaml`, `codex2codex/roles/consult.yaml`, `codex2codex/roles/sa.yaml`, `codex2codex/scripts/test_prepare_wave_blackboard.py`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-6-brief-roles.md`
- Estimated scope: M

### Task 7: 集成 run_wave capsule 生成

- Description: 让 `run_wave.py` 在每个 wave 完成/失败后生成 wave-level capsule fragments、更新 blackboard、记录 capsule validation status，并让 stdout 默认只返回 compact capsule path/status。
- Worker role: coding
- Wave: 4
- Acceptance criteria:
  - PASS wave 写入 `run-capsule.json` / `run-capsule.md` 或 wave fragment，并记录 evidence paths/hash。
  - FAIL/blocker wave 写 compact failure capsule，不粘贴 raw transcript。
  - `validate_capsule.py` 在 wave 结束路径被调用或可由 final validator 调用。
  - Tests 覆盖 success、review FAIL、missing artifact、raw leak。
- Verification: `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_run_wave_capsule.py`
- Dependencies: Task 3, Task 4, Task 5, Task 6
- Files likely touched: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_capsule.py`
- Writable scope: `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_capsule.py`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-7-run-wave.md`
- Estimated scope: M

### Task 8: 集成 run_plan 汇总 capsule

- Description: 让 `run_plan.py` 汇总 wave capsules，生成 plan-level final capsule，并把 capsule path 作为 lead-facing primary output。
- Worker role: coding
- Wave: 5
- Acceptance criteria:
  - Dry-run 仍明确输出 `COMPILE ONLY - NOT A QUALITY GATE`，不得生成 success capsule。
  - Non-dry-run success 输出 final capsule path、spec_dir、validation status。
  - Failed wave 停止后仍生成 compact failure capsule。
  - Tests 覆盖 dry-run、success、wave failure aggregation。
- Verification: `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_run_plan_capsule.py`
- Dependencies: Task 7
- Files likely touched: `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/test_run_plan_capsule.py`
- Writable scope: `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/test_run_plan_capsule.py`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-8-run-plan.md`
- Estimated scope: M

### Task 9: 扩展 wave 与 final validators

- Description: 将 capsule consistency 纳入 `validate_wave.py` 和 `validate_execution_complete.py`，确保 final acceptance 同时证明 artifacts、review PASS、cleanup、capsule evidence 一致。
- Worker role: coding
- Wave: 5
- Acceptance criteria:
  - `validate_wave.py` 可校验 wave capsule refs 与 worker artifacts 一致。
  - `validate_execution_complete.py` 校验 final `run-capsule.json`、review PASS、capsule budget、raw leak、cleanup。
  - Legacy/migration 模式错误信息清晰，不误称旧 dry-run 为 complete。
  - Tests 覆盖 missing capsule、bad capsule hash、review FAIL hidden by capsule、legacy state。
- Verification: `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_execution_completion.py && PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_validate_wave_capsule.py`
- Dependencies: Task 7
- Files likely touched: `codex2codex/scripts/validate_wave.py`, `codex2codex/scripts/validate_execution_complete.py`, `codex2codex/scripts/test_execution_completion.py`, `codex2codex/scripts/test_validate_wave_capsule.py`
- Writable scope: `codex2codex/scripts/validate_wave.py`, `codex2codex/scripts/validate_execution_complete.py`, `codex2codex/scripts/test_execution_completion.py`, `codex2codex/scripts/test_validate_wave_capsule.py`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-9-validators.md`
- Estimated scope: M

### Task 10: 补齐端到端回归测试

- Description: 添加 context firewall integration tests，模拟 plan/wave receipts、capsule generation、validator chain、blackboard complex mode。
- Worker role: coding
- Wave: 6
- Acceptance criteria:
  - Integration tests 不依赖真实 meight worker；用 temp dirs/fakes 模拟 receipts。
  - 覆盖 lead token reduction proxy：capsule bounded，raw result 不进入 capsule。
  - 覆盖 final validator 对 capsule + execution-state + review artifact 的联合校验。
- Verification: `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_context_firewall_integration.py`
- Dependencies: Task 8, Task 9
- Files likely touched: `codex2codex/scripts/test_context_firewall_integration.py`
- Writable scope: `codex2codex/scripts/test_context_firewall_integration.py`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-10-integration-tests.md`
- Estimated scope: M

### Task 11: 更新文档与 ADR 级说明

- Description: 更新 `SKILL.md`、`ARCHITECTURE.md`、可选 `README.md`，记录 context firewall protocol、capsule-first lead flow、blackboard complex mode、validation/rollback。
- Worker role: coding
- Wave: 6
- Acceptance criteria:
  - `SKILL.md` 说明 lead 默认读取 capsule，raw artifacts 仅按需 pull。
  - `ARCHITECTURE.md` 记录 context firewall rationale、capsule schema、quality gates、failure policy。
  - 文档明确 dry-run 不是质量 gate，review PASS 和 final validator 仍必需。
- Verification: `rtk grep -n "run-capsule\\|context firewall\\|blackboard\\|validate_capsule" codex2codex/SKILL.md codex2codex/ARCHITECTURE.md`
- Dependencies: Task 7, Task 8, Task 9
- Files likely touched: `codex2codex/SKILL.md`, `codex2codex/ARCHITECTURE.md`, `codex2codex/README.md`
- Writable scope: `codex2codex/SKILL.md`, `codex2codex/ARCHITECTURE.md`, `codex2codex/README.md`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-11-docs.md`
- Estimated scope: S

### Task 12: 执行计划 dry-run 与验证矩阵

- Description: 运行全量 unit tests、plan dry-run、capsule validators、final execution validator dry fixture，并输出验证矩阵。
- Worker role: coding
- Wave: 7
- Acceptance criteria:
  - 所有 `codex2codex/scripts/test_*.py` 单元测试通过或记录非本改动阻塞。
  - `run_plan.py <plan.md> --dry-run` 通过，且明确 dry-run 非质量 gate。
  - Capsule validator 和 final execution validator 在成功/失败 fixture 上均按预期返回。
- Verification: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s codex2codex/scripts -p 'test_*.py' && python3 codex2codex/scripts/run_plan.py .codex/work/20260620-codex2codex-context-firewall/plan.md --dry-run`
- Dependencies: Task 10, Task 11
- Files likely touched: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-12-validation.md`
- Writable scope: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-12-validation.md`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task-12-validation.md`
- Estimated scope: S

### Task 13: 最终独立 review

- Description: 独立审查全部实现、tests、docs、validators、rollback/compatibility，给出 PASS/FAIL。
- Worker role: review
- Wave: 8
- Acceptance criteria:
  - Review 检查 capsule 是否可能隐藏 material risk。
  - Review 检查 same-quality gates：review PASS、validator chain、artifact evidence、cleanup、raw leak prevention。
  - Review artifact 包含 Findings、Verification 或 Tests、Verdict: PASS|FAIL。
- Verification: `test -s .codex/work/20260620-codex2codex-context-firewall/review.md && rtk grep -n "Verdict: PASS\\|Verdict: FAIL" .codex/work/20260620-codex2codex-context-firewall/review.md`
- Dependencies: Task 12
- Files likely touched: `codex2codex/scripts/capsule.py`, `codex2codex/scripts/validate_capsule.py`, `codex2codex/scripts/blackboard.py`, `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/validate_wave.py`, `codex2codex/scripts/validate_execution_complete.py`, `codex2codex/SKILL.md`, `codex2codex/ARCHITECTURE.md`
- Writable scope: `.codex/work/20260620-codex2codex-context-firewall/review.md`, `codex2codex/scripts/capsule.py`, `codex2codex/scripts/validate_capsule.py`, `codex2codex/scripts/blackboard.py`, `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/validate_wave.py`, `codex2codex/scripts/validate_execution_complete.py`, `codex2codex/SKILL.md`, `codex2codex/ARCHITECTURE.md`
- Output artifact: `.codex/work/20260620-codex2codex-context-firewall/review.md`
- Estimated scope: M

## Step-by-Step Plan

1. 执行 Task 1-2：先锁定 boundary 和 scenario probes，避免后续 schema 漏质量门。
2. 执行 Task 3-4：先做 capsule/blackboard schema + validators + tests，形成后续 runner contract。
3. 执行 Task 5-6：把 receipts 和 worker briefs 接入新 contract，保持旧格式兼容。
4. 执行 Task 7：让 wave runner 生成 capsule/blackboard evidence，默认 compact output。
5. 执行 Task 8-9：让 plan runner 汇总 final capsule，并让 validators 把 capsule consistency 纳入 final gate。
6. 执行 Task 10-11：补齐 integration regression 和 docs/ADR 级说明。
7. 执行 Task 12：跑 unit test matrix、plan dry-run、capsule validator、final execution validator。
8. 执行 Task 13：独立 review，PASS 后才允许交付。

## Parallelization

- Wave 1: Task 1 与 Task 2 都是 read-only consult，仅写不同 artifact，可并行。
- Wave 2: Task 3 写 capsule files，Task 4 写 blackboard files；implementation scope 不重叠，可并行。
- Wave 3: Task 5 写 execution-state files，Task 6 写 prepare_wave/roles files；implementation scope 不重叠，可并行。
- Wave 4: Task 7 单独执行，因为 `run_wave.py` 是核心集成点，依赖 Task 3-6。
- Wave 5: Task 8 写 `run_plan.py`，Task 9 写 validators；implementation scope 不重叠，可并行，但都依赖 Task 7。
- Wave 6: Task 10 写 integration test，Task 11 写 docs；implementation scope 不重叠，可并行。
- Wave 7: Task 12 串行验证，避免并行写测试缓存；使用 `PYTHONDONTWRITEBYTECODE=1`。
- Wave 8: Task 13 独立 review，必须在所有实现和验证后运行。

## Files / Components Likely Affected

- Runner:
  - `codex2codex/scripts/run_wave.py`
  - `codex2codex/scripts/run_plan.py`
  - `codex2codex/scripts/prepare_wave.py`
- State/validation:
  - `codex2codex/scripts/execution_state.py`
  - `codex2codex/scripts/validate_wave.py`
  - `codex2codex/scripts/validate_execution_complete.py`
  - `codex2codex/scripts/validate_result_contract.py`
- New protocol modules:
  - `codex2codex/scripts/capsule.py`
  - `codex2codex/scripts/validate_capsule.py`
  - `codex2codex/scripts/blackboard.py`
  - `codex2codex/scripts/validate_blackboard.py`
- Tests:
  - `codex2codex/scripts/test_capsule_validator.py`
  - `codex2codex/scripts/test_blackboard.py`
  - `codex2codex/scripts/test_execution_capsule_state.py`
  - `codex2codex/scripts/test_prepare_wave_blackboard.py`
  - `codex2codex/scripts/test_run_wave_capsule.py`
  - `codex2codex/scripts/test_run_plan_capsule.py`
  - `codex2codex/scripts/test_validate_wave_capsule.py`
  - `codex2codex/scripts/test_context_firewall_integration.py`
  - `codex2codex/scripts/test_execution_completion.py`
- Roles/docs:
  - `codex2codex/roles/_defaults.yaml`
  - `codex2codex/roles/coding.yaml`
  - `codex2codex/roles/review.yaml`
  - `codex2codex/roles/consult.yaml`
  - `codex2codex/roles/sa.yaml`
  - `codex2codex/SKILL.md`
  - `codex2codex/ARCHITECTURE.md`
  - `codex2codex/README.md`

## Owners / Responsibilities

- Lead/main agent:
  - 审批方向、保存 plan、运行 `$codex2codex`、最终决定是否交付。
  - 默认读取 `run-capsule.md` / `run-capsule.json`，只按需拉 raw artifacts。
  - 不接管 worker-scoped implementation fallback。
- Coding workers:
  - 只修改各自 file-disjoint scope。
  - 写 scoped task artifact，记录 changed files、verification、risks。
  - 遵守 context firewall output budget，不输出 raw logs/transcripts。
- Consult/SA workers:
  - 只读审查边界、风险、rollback、schema、validation strategy。
  - 输出 artifact-ready 建议，不改 repo。
- Review worker:
  - 读取 raw artifacts、capsule、blackboard、tests、docs。
  - 检查 capsule 是否隐藏 material defects。
  - 给出 `Verdict: PASS|FAIL`。
- Runner/validators:
  - 生成 deterministic capsule。
  - 校验 evidence、artifacts、review PASS、cleanup、budget、raw leak。
  - 失败时 fail closed，不输出伪成功。

## Validation Plan

- Focused unit tests:
  - `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_capsule_validator.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_blackboard.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_execution_capsule_state.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_prepare_wave_blackboard.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_run_wave_capsule.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_run_plan_capsule.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_validate_wave_capsule.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_context_firewall_integration.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 codex2codex/scripts/test_execution_completion.py`
- Full unit suite:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s codex2codex/scripts -p 'test_*.py'`
- Plan dry-run:
  - `python3 codex2codex/scripts/run_plan.py .codex/work/20260620-codex2codex-context-firewall/plan.md --dry-run`
  - Expected: prints `COMPILE ONLY - NOT A QUALITY GATE`; no quality-complete claim.
- Capsule validators:
  - `python3 codex2codex/scripts/validate_capsule.py <spec-dir>/run-capsule.json --spec-dir <spec-dir>`
  - `python3 codex2codex/scripts/validate_blackboard.py <spec-dir>/blackboard.json`
- Final execution validator:
  - `python3 codex2codex/scripts/validate_execution_complete.py <spec-dir>`
- Documentation checks:
  - `rtk grep -n "run-capsule\\|context firewall\\|blackboard\\|validate_capsule" codex2codex/SKILL.md codex2codex/ARCHITECTURE.md`
- Acceptance gate:
  - Unit tests PASS.
  - Plan dry-run PASS.
  - Capsule validator PASS on success fixture and FAIL on bad fixtures.
  - Final execution validator PASS only with valid review PASS + capsule consistency.
  - Independent review `Verdict: PASS`.

## Rollout Plan

- Phase 0: Add schema/validators/tests without changing default runner behavior.
- Phase 1: Generate capsule artifacts additively while preserving existing raw artifacts and stdout essentials.
- Phase 2: Make `run_plan.py` / `run_wave.py` return capsule path as primary lead-facing output.
- Phase 3: Enable capsule consistency in final execution validator by default for new runs; provide clear legacy error/compat path.
- Phase 4: Enable blackboard only for complex/high-risk opt-in runs; measure latency and token savings before default expansion.
- Phase 5: Update docs/roles so future agents treat capsule-first workflow as canonical.

## Monitoring / Observability

- Track in `execution-state.json`:
  - `capsule_path`
  - `capsule_hash`
  - `capsule_validation_status`
  - `capsule_estimated_tokens`
  - `raw_artifact_bytes`
  - `raw_artifacts_omitted`
  - `blackboard_path`
  - `review_verdict`
  - `cleanup.shutdown_ok`
- Track in `run-capsule.json`:
  - per-wave status and worker counts;
  - evidence ledger path/hash/type;
  - verification commands and exit status;
  - review PASS/FAIL;
  - unresolved blockers/questions;
  - budget warnings/errors.
- Success metrics:
  - lead-facing capsule token estimate bounded under target;
  - no raw transcript leakage;
  - final validator false PASS rate stays zero on seeded bad fixtures;
  - simple task overhead remains small; complex blackboard overhead justified by review quality.

## Documentation / ADR Updates

- ADR: Needed
- Record ADR-level decision in `codex2codex/ARCHITECTURE.md`:
  - why capsule is deterministic runner output;
  - why raw artifacts stay on disk;
  - why review remains mandatory;
  - why blackboard is complex-mode only;
  - failure policy and rollback path.
- Update `codex2codex/SKILL.md`:
  - capsule-first lead workflow;
  - validator commands;
  - no raw transcript in lead context;
  - complex blackboard trigger guidance;
  - dry-run disclaimer.
- Update `codex2codex/README.md` if it exists and exposes user-facing runner usage.

## Rollback / Recovery Plan

- Keep existing `result.md`, `events.log`, worker artifacts, `execution-state.json`, `review-summary.md` behavior intact.
- Additive rollout means rollback can disable capsule enforcement while preserving raw evidence.
- If capsule generation fails but worker execution succeeded:
  - mark run as failed for new protocol;
  - preserve existing artifacts;
  - allow rerun of capsule generation/validator from `execution-state.json`.
- If blackboard causes latency or noise:
  - disable complex-mode default;
  - keep schema/tests but stop injecting blackboard digest.
- If validators are too strict:
  - adjust validator fixtures and docs, not worker quality gates;
  - never bypass review PASS requirement.
- If docs/roles confuse workers:
  - rollback role prompt edits only, keeping deterministic runner validators.

## Abort Criteria

- Capsule validator permits raw transcript/event dump in `run-capsule.md` or `run-capsule.json`.
- Final validator passes without review PASS for non-trivial implementation.
- Dry-run can be mistaken for quality-complete execution.
- Capsule claims success while evidence ledger points to missing/empty artifacts.
- Blackboard becomes required for simple tasks and causes excessive latency.
- Worker brief changes cause out-of-scope edits or reduce test/review quality.
- Full `codex2codex/scripts/test_*.py` suite has unresolved failures caused by this refactor.
- Independent review returns `Verdict: FAIL`.

## Risks

- Risk: Capsule hides material defect.
  - Mitigation: reviewer/gatekeeper reads raw detail; validators require evidence links; seeded defect tests.
- Risk: Validator becomes bureaucratic and slows simple tasks.
  - Mitigation: deterministic stdlib checks, blackboard opt-in, budgeted capsule sections.
- Risk: Backward compatibility break for old spec dirs.
  - Mitigation: legacy mode/error path, additive artifacts, clear migration docs.
- Risk: Token budget estimate inaccurate.
  - Mitigation: treat as proxy metric; enforce chars/sections plus raw-leak regex and evidence hashes.
- Risk: Review worker trusts capsule instead of raw artifacts.
  - Mitigation: role prompt requires raw artifact inspection and capsule consistency check.
- Risk: Same-wave workers conflict on shared scripts.
  - Mitigation: task waves keep implementation writable scopes disjoint.

## Open Questions

- What exact hard token budget should ship by default: 4k, 6k, or 8k?
- Should complex-mode trigger be CLI flag only first, or automatic for multi-wave/high-risk/review-FAIL plans?
- Should failing runs include expanded compact failure detail by default, or require lead pull of artifact links?
- Should an explicit `gatekeeper` role be added later, or keep gatekeeping under `review` + deterministic validators for MVP?
- Should capsule artifacts live only in `.codex/specs/<slug>/`, or also mirror into `.codex/work/<topic>/artifacts/` for plan-driven runs?

## Execution Decision

- Recommend proceed with implementation after saving this plan to `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/plan.md`.
- Execution should use `$codex2codex` heavy mode, file-disjoint waves, independent final review, and no lead fallback implementation.
- Do not execute destructive git actions; do not commit or push.
- Treat Task 12 and Task 13 as hard gates.
- If any worker raises a direction-changing `QUESTION:`, pause and route it to the orchestrator instead of guessing.

## Execution Handoff

- Goal: Refactor `codex2codex` into a context firewall protocol with bounded `run-capsule.*`, stronger validators, and optional complex-mode blackboard.
- Current state: Plan drafted only; no repo mutation performed in this planning worker.
- Authoritative artifacts: `.codex/work/20260620-codex2codex-context-firewall/idea.md`; intended plan path `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/plan.md`.
- Decisions: Capsule is deterministic runner output; review remains mandatory; raw artifacts stay on disk; blackboard is opt-in complex mode; dry-run is not a quality gate.
- Verification: Required commands include `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s codex2codex/scripts -p 'test_*.py'`, `python3 codex2codex/scripts/run_plan.py .codex/work/20260620-codex2codex-context-firewall/plan.md --dry-run`, `python3 codex2codex/scripts/validate_capsule.py <spec-dir>/run-capsule.json --spec-dir <spec-dir>`, and `python3 codex2codex/scripts/validate_execution_complete.py <spec-dir>`.
- Remaining risks: Capsule false confidence, validator strictness, legacy compatibility, blackboard overhead, review worker over-trusting capsule.
- Next action: Save this markdown as `plan.md`, run plan-contract validation, then execute via `$codex2codex` waves.
- Suggested skills: `codex2codex`, `test-driven-development`, `debugging-and-error-recovery`, `api-and-interface-design`, `codegraph-project-reader`.
- Redactions / omitted raw data: No raw worker transcripts, logs, secrets, or large command outputs included.
SPEC2PLAN_ARTIFACT_END
