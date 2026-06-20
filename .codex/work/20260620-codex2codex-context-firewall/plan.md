# codex2codex 预首项停滞恢复与 spec2plan 重型合成流计划

Mode: heavy  
Risk level: High  
Confidence: High

## Goal

实现更安全的 `codex2codex` 恢复与 `spec2plan` 重型规划流：当 worker 已到 `turn/started` 但没有 `item/started`、没有 token 使用、没有 current item 且活动陈旧时，明确归类为 `PRE_FIRST_ITEM_STALL`，按基础设施/app-server stream 失败处理，轮换 daemon/app-server 与 fresh `MEIGHT_HOME`，运行 nonce smoke worker 后仅重试一次，并更新重型规划指南以支持紧凑合成输入，同时保留全部质量门禁。

## Non-Goals

- 不实现 blackboard/context-firewall 的更大范围改造；本计划只覆盖恢复分类、恢复决策、测试与相关文档。
- 不把 dry-run 当作质量门禁；dry-run 只能作为结构预检。
- 不允许 main-agent fallback synthesis；最终仍必须由验证通过的 `SPEC2PLAN_ARTIFACT_V1` synthesizer artifact 驱动。
- 不改变 `codex2codex` 的正常成功路径或现有任务质量失败语义，除非为新增分类所必需。

## Evidence Inspected

- `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/subagents/synthesis-packet.md`
- `/data/lcq/.codex/skills/spec2plan/SKILL.md`
- `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/idea.md`
- `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/subagents/planner.md`
- `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/subagents/reviewer.md`
- `/tmp/meight-codex2codex-context-firewall/workers/spec2plan-synthesizer/events.log`
- `/tmp/meight-codex2codex-context-firewall/workers/spec2plan-synthesizer-2/events.log`
- `codex2codex/meight.py`
- `codex2codex/scripts/run_wave.py`
- `spec2plan/references/heavy-mode.md`

## Spec Summary

- 现象：两次 synthesizer worker events log 只有 `turn/started` 后被 interrupt，没有 `item/started` 与 token，表明不是任务内容失败，而是 app-server/stream 基础设施停滞。
- 当前行为：`Worker._handle_event()` 在 `turn/started` 后设为 running；`wait_for_worker()` 将 stale running 视作 generic stall；`run_wave.py` 有恢复分类但没有 `PRE_FIRST_ITEM_STALL`。
- 目标行为：新增精确分类与恢复合同，检测到预首项停滞时轮换 daemon/app-server，使用 fresh `MEIGHT_HOME`，先运行 nonce smoke worker，再对原 worker 重试一次。
- 规划流：更新 `spec2plan` heavy-mode 指南，优先使用验证过的 planner/reviewer artifact，并优先走 `reviewer -> planner follow finalizer` 或 compact synthesis packet，避免完整 fresh synthesizer 造成上下文过载；仍要求验证通过的 synthesizer artifact，无 main-agent fallback。
- 质量门禁：保留 review PASS/FAIL、subagent artifact validator、最终 plan validation；dry-run 只做结构预检。

## Domain Language Check

- 使用现有域词：`worker`、`turn/started`、`item/started`、`token usage`、`current item`、`stale activity`、`daemon`、`app-server`、`MEIGHT_HOME`、`nonce smoke worker`、`SPEC2PLAN_ARTIFACT_V1`。
- 新增规范词：`PRE_FIRST_ITEM_STALL`，定义为基础设施/app-server stream failure，不是 task quality failure。
- 术语冲突：现有 generic `stall` 可能覆盖过宽；实施时需让 `PRE_FIRST_ITEM_STALL` 优先于 generic stale-running 分类。

## Current Context

- 运行环境观测到两次 synthesizer 均在 `turn/started` 后无后续 event/token，说明重型合成 worker 可在进入第一项前卡死。
- `codex2codex` 已有 worker 状态与恢复路径，但缺少预首项停滞的专用分类与恢复决策。
- `spec2plan` heavy-mode 要求 planner/reviewer/synthesizer，但未提供紧凑合成兜底路径，容易重复触发同类 stream 失败。
- 本计划供 `$codex2codex` 执行；仓库修改需留在 working tree，不执行 `git commit` 或 `git push`。

## Assumptions

- `codex2codex/meight.py` 可安全暴露或返回 stall classification，供 `run_wave.py` 做恢复决策。
- `codex2codex/scripts/run_wave.py` 已具备 daemon/app-server 恢复入口，可增量扩展为 fresh `MEIGHT_HOME` + nonce smoke + retry once。
- 现有测试可通过直接构造 worker/event state 与 monkeypatch recovery runner 覆盖新增分支。
- 文档更新应放在 `codex2codex/SKILL.md`、`codex2codex/ARCHITECTURE.md`、`spec2plan/references/heavy-mode.md`，不新增大规模指南体系。

## User Inputs Needed

Not applicable：需求包已给出目标、约束、证据、文件范围与输出形态；实施阶段无需额外产品决策。

## Proposed Approach

1. 先定义可测试恢复合同：`PRE_FIRST_ITEM_STALL` 的字段条件、优先级、恢复动作、重试上限、失败后输出。
2. 在 `meight.py` 中实现分类能力，让 `turn/started` 后无首项/无 token/无 current item/活动陈旧的 worker 得到专用分类。
3. 在 `run_wave.py` 中把分类映射到基础设施恢复：停止/轮换 daemon/app-server，创建 fresh `MEIGHT_HOME`，运行 nonce smoke worker，成功后重试原 worker 一次。
4. 增加回归测试覆盖分类与恢复决策，防止该场景再次变成 generic stall 或 task failure。
5. 更新 `codex2codex` 与 `spec2plan` 文档，明确紧凑合成输入、验证 artifact、禁止 main-agent fallback、dry-run 非质量门禁。
6. 最后运行定向测试、结构预检、真实执行后的最终 validator，并由独立 review worker 给出 PASS/FAIL。

## Scenario Probes

- worker 只有 `turn/started`，无 `item/started`、无 token、无 current item、stale activity → `PRE_FIRST_ITEM_STALL`，执行 infra recovery。
- worker 有 `item/started` 但无完成事件 → 不是 `PRE_FIRST_ITEM_STALL`，沿用现有 item-level stall 逻辑。
- worker 有 token usage 但停滞 → 不是 `PRE_FIRST_ITEM_STALL`，避免误判任务执行慢或模型输出卡顿。
- nonce smoke worker 失败 → 不重试原 worker，报告 infra recovery failure 并保留清理/日志摘要。
- nonce smoke worker 成功但原 worker 重试仍 pre-first-item stall → 不无限重试，报告一次 retry exhausted。
- heavy-mode synthesizer 卡死 → 优先使用 validated planner/reviewer + compact synthesis packet 重新发起，不由 main agent 合成 plan。
- dry-run 通过但测试或 artifact validator 失败 → 整体不通过，dry-run 不提升为质量门禁。

## Dependency Graph

```text
Task 1 -> Task 2 -> Task 5 -> Task 6
Task 1 -> Task 3 -> Task 5 -> Task 6
Task 1 -> Task 4 -> Task 5 -> Task 6
```

- Task 1 定义与测试分类合同，是后续恢复实现和文档措辞的基础。
- Task 2 依赖 Task 1 的分类常量/合同。
- Task 3、Task 4 可在 Task 1 后并行，因为写入路径不重叠。
- Task 5 汇总验证前序代码与文档改动。
- Task 6 是独立最终 review。

## Task Breakdown

### Task 1: 定义预首项停滞分类

- Description: 在 worker 状态/等待逻辑中新增 `PRE_FIRST_ITEM_STALL` 分类，精确定义 `turn/started` 后无 `item/started`、无 token usage、无 current item 且 stale activity 的检测条件，并增加分类回归测试。
- Worker role: coding
- Wave: 1
- Acceptance criteria:
  - `PRE_FIRST_ITEM_STALL` 常量或等价枚举存在且命名稳定。
  - 分类优先级高于 generic stale-running stall。
  - 有 `item/started`、有 token usage、或有 current item 的 worker 不会被误分类。
- Verification:
  - `python codex2codex/scripts/test_worker_recovery_contracts.py`
- Dependencies:
  - None
- Files likely touched:
  - `codex2codex/meight.py`
  - `codex2codex/scripts/test_worker_recovery_contracts.py`
- Writable scope:
  - `codex2codex/meight.py`
  - `codex2codex/scripts/test_worker_recovery_contracts.py`
  - `.codex/work/20260620-codex2codex-context-firewall/artifacts/task1-worker-classification.md`
- Output artifact:
  - `.codex/work/20260620-codex2codex-context-firewall/artifacts/task1-worker-classification.md`
- Estimated scope: M

### Task 2: 实现恢复决策与一次重试

- Description: 在 wave runner 恢复路径中识别 `PRE_FIRST_ITEM_STALL`，按基础设施/app-server stream failure 处理：轮换 daemon/app-server，使用 fresh `MEIGHT_HOME`，运行 nonce smoke worker，成功后对原 worker 仅重试一次。
- Worker role: coding
- Wave: 2
- Acceptance criteria:
  - `PRE_FIRST_ITEM_STALL` 不计为任务质量失败。
  - 恢复动作顺序为 rotate daemon/app-server → fresh `MEIGHT_HOME` → nonce smoke worker → retry once。
  - smoke 失败不重试原 worker；原 worker 二次失败不无限重试。
  - 恢复摘要不泄漏 raw transcript。
- Verification:
  - `python codex2codex/scripts/test_run_wave_recovery.py`
  - `python codex2codex/scripts/test_worker_recovery_contracts.py`
- Dependencies:
  - Task 1
- Files likely touched:
  - `codex2codex/scripts/run_wave.py`
  - `codex2codex/scripts/test_run_wave_recovery.py`
- Writable scope:
  - `codex2codex/scripts/run_wave.py`
  - `codex2codex/scripts/test_run_wave_recovery.py`
  - `.codex/work/20260620-codex2codex-context-firewall/artifacts/task2-run-wave-recovery.md`
- Output artifact:
  - `.codex/work/20260620-codex2codex-context-firewall/artifacts/task2-run-wave-recovery.md`
- Estimated scope: M

### Task 3: 更新 codex2codex 恢复文档

- Description: 更新 `codex2codex` skill/architecture 文档，说明 `PRE_FIRST_ITEM_STALL` 的含义、恢复动作、一次重试限制、cleanup 要求、日志/转录 redaction 要求。
- Worker role: coding
- Wave: 3
- Acceptance criteria:
  - 文档明确该分类是 infra/app-server stream failure，不是 task quality failure。
  - 文档写明 fresh `MEIGHT_HOME`、nonce smoke worker、retry once。
  - 文档保留 worker cleanup 与 no raw transcript leakage 要求。
- Verification:
  - `rg "PRE_FIRST_ITEM_STALL|nonce smoke|MEIGHT_HOME" codex2codex/SKILL.md codex2codex/ARCHITECTURE.md`
- Dependencies:
  - Task 1
- Files likely touched:
  - `codex2codex/SKILL.md`
  - `codex2codex/ARCHITECTURE.md`
- Writable scope:
  - `codex2codex/SKILL.md`
  - `codex2codex/ARCHITECTURE.md`
  - `.codex/work/20260620-codex2codex-context-firewall/artifacts/task3-codex2codex-docs.md`
- Output artifact:
  - `.codex/work/20260620-codex2codex-context-firewall/artifacts/task3-codex2codex-docs.md`
- Estimated scope: S

### Task 4: 更新 spec2plan 重型合成指南

- Description: 更新 `spec2plan/references/heavy-mode.md`，要求 synthesizer 输入保持紧凑：优先使用验证过的 planner/reviewer artifacts，优先选择 `reviewer -> planner follow finalizer` 或 compact synthesis packet，仍必须产出验证通过的 `SPEC2PLAN_ARTIFACT_V1` final artifact，禁止 main-agent fallback synthesis。
- Worker role: coding
- Wave: 3
- Acceptance criteria:
  - heavy-mode 指南明确 compact synthesis 路径与适用条件。
  - 指南保留 planner/reviewer/synthesizer artifact validator 与 review PASS/FAIL。
  - 指南明确 dry-run 只做结构预检，不是质量门禁。
  - 指南明确 main agent 不得替代 synthesizer 写最终 plan。
- Verification:
  - `rg "compact synthesis|SPEC2PLAN_ARTIFACT_V1|main-agent fallback|dry-run" spec2plan/references/heavy-mode.md`
- Dependencies:
  - Task 1
- Files likely touched:
  - `spec2plan/references/heavy-mode.md`
- Writable scope:
  - `spec2plan/references/heavy-mode.md`
  - `.codex/work/20260620-codex2codex-context-firewall/artifacts/task4-spec2plan-heavy-mode.md`
- Output artifact:
  - `.codex/work/20260620-codex2codex-context-firewall/artifacts/task4-spec2plan-heavy-mode.md`
- Estimated scope: S

### Task 5: 执行验证与结构预检

- Description: 运行定向回归测试、搜索检查、artifact validator、plan dry-run 结构预检，并记录真实执行后的最终验证结果；明确 dry-run 不作为质量门禁。
- Worker role: devops
- Wave: 4
- Acceptance criteria:
  - 新增/相关测试命令执行并记录结果。
  - `validate_subagent_artifact.py` 用于相关 worker artifact；最终 plan 执行后运行 `validate_plan_contract.py --mode heavy`。
  - `scripts/run_plan.py <plan.md> --dry-run` 若可用，仅记录为结构预检。
  - 失败项附最小错误摘要，不粘贴 raw transcript。
- Verification:
  - `python codex2codex/scripts/test_worker_recovery_contracts.py`
  - `python codex2codex/scripts/test_run_wave_recovery.py`
  - `python spec2plan/scripts/validate_plan_contract.py .codex/work/20260620-codex2codex-context-firewall/plan.md --mode heavy`
  - `python codex2codex/scripts/run_plan.py .codex/work/20260620-codex2codex-context-firewall/plan.md --dry-run`
- Dependencies:
  - Task 2
  - Task 3
  - Task 4
- Files likely touched:
  - `.codex/work/20260620-codex2codex-context-firewall/artifacts/task5-validation.md`
- Writable scope:
  - `.codex/work/20260620-codex2codex-context-firewall/artifacts/task5-validation.md`
- Output artifact:
  - `.codex/work/20260620-codex2codex-context-firewall/artifacts/task5-validation.md`
- Estimated scope: S

### Task 6: 独立最终审查

- Description: 独立审查代码、测试、文档与验证输出，给出 PASS/FAIL，重点检查分类精确性、恢复只重试一次、dry-run 非质量门禁、无 main-agent fallback synthesis、无 raw transcript leakage。
- Worker role: review
- Wave: 5
- Acceptance criteria:
  - 审查结论为明确 `PASS` 或 `FAIL`。
  - 若 `FAIL`，列出阻塞问题、受影响文件、建议修复任务。
  - 审查确认没有越界实现 blackboard/context-firewall 大范围工作。
- Verification:
  - Review artifact inspection only; no mutation required.
- Dependencies:
  - Task 5
- Files likely touched:
  - `.codex/work/20260620-codex2codex-context-firewall/review.md`
- Writable scope:
  - `.codex/work/20260620-codex2codex-context-firewall/review.md`
- Output artifact:
  - `.codex/work/20260620-codex2codex-context-firewall/review.md`
- Estimated scope: S

## Step-by-Step Plan

1. 创建 `.codex/work/20260620-codex2codex-context-firewall/artifacts/`，用于每个 worker 输出 artifact。
2. 执行 Task 1，先让 `PRE_FIRST_ITEM_STALL` 分类在单元测试中可观察、可断言。
3. 执行 Task 2，把分类接入 wave recovery，并用测试验证 rotate/fresh-home/smoke/retry-once 的决策。
4. 执行 Task 3 与 Task 4，分别更新 `codex2codex` 与 `spec2plan` 文档；两者可并行。
5. 执行 Task 5，跑定向测试与最终 validator；dry-run 只记录结构预检结果。
6. 执行 Task 6，独立 review 输出 `PASS` 或 `FAIL`。
7. 若 Task 6 为 `FAIL`，按 review artifact 开新修复 wave；若 `PASS`，交还 orchestrator 决定是否进入提交/发布流程。

## Parallelization

- Wave 1：Task 1 单独运行，因为它定义共享分类合同。
- Wave 2：Task 2 单独运行，因为它依赖 Task 1 且触碰恢复控制流。
- Wave 3：Task 3 与 Task 4 可并行；写入路径分别为 `codex2codex/*` 与 `spec2plan/references/heavy-mode.md`，无重叠。
- Wave 4：Task 5 必须在全部实现与文档更新后运行。
- Wave 5：Task 6 必须最后运行；review task 可读取所有输出，但只写 `.codex/work/20260620-codex2codex-context-firewall/review.md`。

## Files / Components Likely Affected

- `codex2codex/meight.py`
- `codex2codex/scripts/run_wave.py`
- `codex2codex/scripts/test_worker_recovery_contracts.py`
- `codex2codex/scripts/test_run_wave_recovery.py`
- `codex2codex/SKILL.md`
- `codex2codex/ARCHITECTURE.md`
- `spec2plan/references/heavy-mode.md`
- `.codex/work/20260620-codex2codex-context-firewall/artifacts/`
- `.codex/work/20260620-codex2codex-context-firewall/review.md`

## Owners / Responsibilities

- coding worker：实现分类、恢复决策、测试、文档更新。
- devops worker：运行验证命令，区分结构预检与质量门禁，汇总最小错误摘要。
- review worker：独立 PASS/FAIL 审查，阻止分类模糊、无限重试、dry-run 冒充质量门禁、main-agent fallback、raw transcript 泄漏。
- orchestrator：监督 wave 顺序、处理 `QUESTION:`、决定是否进入后续提交/发布流程；不得执行 `git commit` 或 `git push`。

## Validation Plan

- 分类回归：
  - `python codex2codex/scripts/test_worker_recovery_contracts.py`
- 恢复决策回归：
  - `python codex2codex/scripts/test_run_wave_recovery.py`
- 文档关键字检查：
  - `rg "PRE_FIRST_ITEM_STALL|nonce smoke|MEIGHT_HOME" codex2codex/SKILL.md codex2codex/ARCHITECTURE.md`
  - `rg "compact synthesis|SPEC2PLAN_ARTIFACT_V1|main-agent fallback|dry-run" spec2plan/references/heavy-mode.md`
- Artifact 验证：
  - `python spec2plan/scripts/validate_subagent_artifact.py planner .codex/work/20260620-codex2codex-context-firewall/subagents/planner.md`
  - `python spec2plan/scripts/validate_subagent_artifact.py reviewer .codex/work/20260620-codex2codex-context-firewall/subagents/reviewer.md`
  - `python spec2plan/scripts/validate_subagent_artifact.py synthesizer .codex/work/20260620-codex2codex-context-firewall/subagents/synthesizer.md`
- Plan 合同最终验证：
  - `python spec2plan/scripts/validate_plan_contract.py .codex/work/20260620-codex2codex-context-firewall/plan.md --mode heavy`
- 结构预检，非质量门禁：
  - `python codex2codex/scripts/run_plan.py .codex/work/20260620-codex2codex-context-firewall/plan.md --dry-run`

## Rollout Plan

- 本改动先作为 working tree 变更落地，不提交、不推送。
- 先运行定向测试，再运行文档搜索检查与 artifact/plan validators。
- 若 review PASS，可由 orchestrator 安排后续人工验收或单独提交流程。
- 若部署到真实工作流，先在一次受控 heavy-mode planning 任务上验证 `PRE_FIRST_ITEM_STALL` 恢复路径，再扩大使用。

## Monitoring / Observability

- 恢复摘要必须记录分类：`PRE_FIRST_ITEM_STALL`。
- 摘要必须记录恢复动作阶段：daemon/app-server rotation、fresh `MEIGHT_HOME`、nonce smoke worker、retry once。
- 摘要必须记录 retry count 与最终状态。
- 日志只保留事件类型、时间、worker id、分类、恢复结果等必要元数据；不粘贴 raw transcript、prompt、完整 events log。
- 若恢复失败，输出最小可诊断错误摘要与 artifact 路径。

## Documentation / ADR Updates

ADR: Needed

- 需要新增或更新 ADR，记录 `PRE_FIRST_ITEM_STALL` 被定义为 infra/app-server stream failure 的决策、恢复序列、一次重试限制、非任务质量失败语义。
- `codex2codex/SKILL.md`：补充操作员可执行恢复语义与 no raw transcript leakage。
- `codex2codex/ARCHITECTURE.md`：补充 worker 状态机与恢复分类。
- `spec2plan/references/heavy-mode.md`：补充 compact synthesis packet / planner follow finalizer 路径、artifact validator、禁止 main-agent fallback、dry-run 非质量门禁。

## Rollback / Recovery Plan

- 若新增分类导致误判，回滚 `codex2codex/meight.py` 中分类接入与对应测试期望，保留文档草案供后续修正。
- 若 `run_wave.py` 恢复路径引入不稳定，禁用 `PRE_FIRST_ITEM_STALL` 专用恢复映射，退回现有 generic stall 行为，并记录 review FAIL。
- 若 heavy-mode 文档造成执行歧义，回滚 `spec2plan/references/heavy-mode.md` 改动，恢复原 planner/reviewer/synthesizer 流程。
- 所有回滚均只修改 working tree；不执行 `git reset`、`git commit`、`git push`，除非 orchestrator 另行授权。

## Abort Criteria

- 无法可靠区分 `PRE_FIRST_ITEM_STALL` 与已有 item-level/token-producing stall。
- 测试需要真实 daemon/app-server 或网络才能覆盖核心恢复决策，无法用 mock/contract test 稳定验证。
- 恢复实现需要无限重试或绕过 worker cleanup 才能工作。
- 任何方案要求 main agent 直接替代 synthesizer 写最终 heavy-mode plan。
- Artifact validator 或最终 plan validator 失败且无法在当前范围内修复。
- Review worker 给出 `FAIL` 且问题涉及恢复合同或质量门禁语义。

## Risks

- 误分类风险：过宽条件可能把慢启动或正常首项前延迟误判为 infra failure。
- 恢复副作用：轮换 daemon/app-server 与 fresh `MEIGHT_HOME` 可能影响同 wave 其他 worker；需隔离 scope。
- 测试脆弱性：若现有脚本不易 mock daemon/app-server，测试可能过度依赖实现细节。
- 文档漂移：`codex2codex` 与 `spec2plan` 指南需保持同一语义，避免一个允许 fallback、另一个禁止 fallback。
- 质量门禁混淆：dry-run 容易被误解为成功证明，必须持续标记为结构预检。

## Open Questions

- Not applicable：当前范围内没有必须由用户回答才能执行的问题；更大 blackboard/context-firewall 工作明确 deferred。

## Execution Decision

Proceed with implementation only after orchestrator accepts this plan. Execute via `$codex2codex` waves, preserve working tree changes, do not run `git commit` or `git push`. If any task raises `QUESTION:` or review returns `FAIL`, stop before rollout and return the blocking artifact.

## Execution Handoff

- Goal: 为 `turn/started` 后无首项/无 token 的 worker 增加 `PRE_FIRST_ITEM_STALL` 分类、infra recovery、回归测试与 heavy-mode 紧凑合成指南。
- Current state: 已有 planner/reviewer artifact 被标记为验证通过；两次 synthesizer events log 只到 `turn/started` 后中断；当前代码缺少该专用分类。
- Authoritative artifacts: `.codex/work/20260620-codex2codex-context-firewall/plan.md`、`.codex/work/20260620-codex2codex-context-firewall/subagents/planner.md`、`.codex/work/20260620-codex2codex-context-firewall/subagents/reviewer.md`、`.codex/work/20260620-codex2codex-context-firewall/review.md`。
- Decisions: `PRE_FIRST_ITEM_STALL` 是 infra/app-server stream failure；恢复顺序为 rotate daemon/app-server、fresh `MEIGHT_HOME`、nonce smoke worker、retry once；dry-run 非质量门禁；禁止 main-agent fallback synthesis。
- Verification: 运行 worker recovery contract tests、run_wave recovery tests、文档 rg 检查、subagent artifact validators、heavy plan validator；dry-run 仅结构预检。
- Remaining risks: 误分类、daemon/app-server 轮换副作用、mock 测试脆弱、文档语义漂移。
- Next action: 按 Task 1 开始实现分类合同与回归测试。
- Suggested skills: `test-driven-development`、`debugging-and-error-recovery`、`apply-patch`、`codex-agent-team:team-review-cycle`。
- Redactions / omitted raw data: 不复制 `/tmp/meight-codex2codex-context-firewall/workers/*/events.log` 原始内容；仅引用路径与最小事件摘要。
