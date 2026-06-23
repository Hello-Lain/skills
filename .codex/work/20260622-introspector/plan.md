# Introspector Skill Implementation Plan

Mode: light
Risk level: Medium
Confidence: High

## Goal

将 `Introspector` 落地为一个可触发的新 Codex skill，具备明确的审查 contract、进阶引用文档、对“证据获取/反依附/稳定性检查”的强约束，以及可验证的生产门控产物。

## Non-Goals

不实现外部网络服务，不新增 MCP 依赖，不引入运行时数据库或持久化 verdict memory，不在本次落地中构建自动 benchmark runner。

## Evidence Inspected

- `/data/lcq/.codex/skills/.codex/work/20260622-introspector/spec.md`
- `/data/lcq/.codex/skills/.codex/work/20260622-introspector/artifacts/neutrality-research.md`
- `/data/lcq/.codex/skills/.codex/work/20260622-introspector/artifacts/self-review-20260623.md`
- `/data/lcq/.codex/skills/.codex/work/20260622-introspector/artifacts/self-review-20260623-r2.md`
- `/data/lcq/.codex/skills/spec2plan/SKILL.md`
- `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- `/data/lcq/.codex/skills/spec2plan/references/artifact-contract.md`
- `/data/lcq/.codex/skills/plan2do/SKILL.md`
- `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- `/data/lcq/.codex/skills/plan2do/references/review-rubric.md`
- `/data/lcq/.codex/skills/plan2do/references/failure-policy.md`
- `/data/lcq/.codex/skills/reviewer/SKILL.md`
- `/data/lcq/.codex/skills/.system/skill-creator/SKILL.md`
- `/data/lcq/.codex/skills/.system/skill-creator/references/openai_yaml.md`
- `/data/lcq/.codex/skills/.system/skill-creator/scripts/init_skill.py`
- `/data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py`
- `/data/lcq/.codex/skills/skill-tokenless/references/skill-production-gate.md`
- `/data/lcq/.codex/skills/skill-tokenless/plan.md`
- `/data/lcq/.codex/skills/skill-router/artifacts/production-report.md`
- `/data/lcq/.codex/skills/skill-router/artifacts/review-report.md`
- `/data/lcq/.codex/skills/interview-me/SKILL.md`
- `git status --short` 未执行；本次以内联 diff 和 workspace artifact 为主。

## Spec Summary

`Introspector` 需要成为一个用户显式触发的中立审查 skill。它不顺从用户 framing，先重述目标，再做 framing audit、evidence acquisition、候选方案比较、verification、falsifier、delta review、verdict stability check，并把结论交给 `reviewer` heavy gate。最新 spec 已补齐 `evidence-first`、`adversarial reviewer default`、`scope stop`、`delta review` 和 `verdict stability`。

## Domain Language Check

沿用现有本地术语：`SKILL.md`、`agents/openai.yaml`、`references/`、`reviewer` heavy gate、`block`、`falsifier`、`delta review`、`verdict stability check`、`dependency ring`、`calibration harness`。避免引入新的同义词替换这些 contract 词。

## Current Context

当前 workspace 已有成熟 `spec.md`、多轮 self-review artifact、研究笔记和 manifest，但仓库中还没有 `introspector/` skill 目录。现有本地 skill 模式显示：主入口保持紧凑，稀有或长流程下沉到 `references/`；`agents/openai.yaml` 保持简短；生产门控需要 `production-report.md`、review artifact、计划执行 artifact 和 validator 结果。

## Implementation Map

- Files:
  - `introspector/SKILL.md`：主 skill contract 与触发描述。
  - `introspector/agents/openai.yaml`：UI 元数据与默认 prompt。
  - `introspector/references/workflow.md`：详细审查流程、输出结构、hard stops。
  - `introspector/references/report-schema.md`：规范 verdict vocabulary、sections、evidence class、delta review、stability check。
  - `introspector/references/calibration-harness.md`：最小 benchmark/case set 与使用规则。
  - `introspector/references/validation.md`：本 skill 的本地验证、scenario gate、cleanup、review handoff。
  - `.codex/work/20260622-introspector/artifacts/production-report.md`：生产门控报告。
  - `.codex/work/20260622-introspector/review-introspector-final.md`：最终 reviewer 报告。
- Symbols / APIs:
  - 无代码符号；核心 contract 为 `block`、`keep|trim|merge|redo|pause|change-direction`、`falsifier`、`delta review`、`verdict stability check`。
  - 使用 `.system/skill-creator/scripts/init_skill.py`、`.system/skill-creator/scripts/quick_validate.py`。
- Tests:
  - 计划内不新增 Python 单测；使用 `quick_validate.py`、grep/内容检查、review report validator、生产门控 validator、scenario gate artifact。
- Commands:
  - `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/introspector`
  - `python /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/plan.md --mode light`
  - `python /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/plan.md`
  - `python3 /data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/review-introspector-final.md --root /data/lcq/.codex/skills`
  - `python3 /data/lcq/.codex/skills/skill-tokenless/scripts/validate_skill_production.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
  - `python3 /data/lcq/.codex/skills/plan2do/scripts/pre_review_ready.py /data/lcq/.codex/skills/.codex/work/20260622-introspector --stage draft --require-production-report --require-final-report`
  - `python3 /data/lcq/.codex/skills/skill-tokenless/scripts/validate_skill_production.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`
  - `python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260622-introspector`
- Data / migration impact:
  - Not applicable：仅新增 skill 目录与 workspace artifacts，无数据迁移。

## Assumptions

- `introspector` 作为新 skill 名称可用，且应保持 hyphen-case 规则的单词形式，无需前缀。
- `references/` 文档足以承载较长流程与 benchmark 细节，不需要额外脚本来运行 `calibration harness`。
- 本次可接受以静态 scenario gate 和文档级 forward checks 代替真实子代理压测，因为用户未要求多代理 forward-test。

## User Inputs Needed

Not applicable：用户已明确要求将该 skill 落地，当前 spec 与本地上下文足以推进实现。

## Proposed Approach

先创建最小 skill 骨架，再把 contract 分层：`SKILL.md` 只保留触发条件、主流程、引用路由、hard stops、mandatory review gate；把详细 workflow、报告 schema、benchmark、validation 细节下沉到 `references/`。执行阶段同步产出 `production-report.md`、review artifact、final-report.md`，并跑完 `quick_validate.py`、review validator、production gate validator、execution validator`。

## Scenario Probes

- RED/control：旧 spec-level artifact 没有真实 skill 目录；新实现必须提供可触发的 `introspector/SKILL.md` 与 reference routing。
- GREEN/retest：触发描述中必须覆盖 `idea/spec/plan/implementation-result/framework-design`，并要求 evidence acquisition、falsifier、delta review、verdict stability。
- Adversarial probe：skill 文档必须明确“用户同意不是证据”“被审对象默认不可信”“证据不足优先 `block`”。
- Cleanup probe：执行完成后不应留下临时 scaffold/example 垃圾文件。

## Dependency Graph

计划验证 -> task state 编译 -> skill 骨架 -> 主入口 contract -> references 下沉 -> production/report artifacts -> reviewer gate -> final gate。

## Task Breakdown

### Task 1: 生成执行状态与上下文包

- Description: 为 `plan2do` 执行创建 `execution/tasks.json` 与 wave 级 context pack，确保后续任务按 contract 驱动。
- Worker role: coding
- Wave: 1
- Acceptance criteria: `execution/tasks.json` 存在且能反映本计划任务；`artifacts/context-wave1.md` 存在并指向权威源。
- Verification: `python /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/plan.md`
- Concrete edits: 写入 `.codex/work/20260622-introspector/execution/tasks.json` 与 `.codex/work/20260622-introspector/artifacts/context-wave1.md`。
- Interfaces / contracts changed: 无用户可见接口变化；仅建立执行状态与上下文 contract。
- Test cases: 执行编译命令并确认输出路径存在。
- Pre-check commands: `python /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/plan.md --mode light`
- Post-check commands: `python /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/plan.md`
- Dependencies: None
- Files likely touched: `.codex/work/20260622-introspector/execution/tasks.json`, `.codex/work/20260622-introspector/artifacts/context-wave1.md`
- Writable scope: `.codex/work/20260622-introspector/execution/`, `.codex/work/20260622-introspector/artifacts/context-wave1.md`
- Output artifact: `.codex/work/20260622-introspector/artifacts/task1-execution.md`
- Estimated scope: S

### Task 2: 创建 skill 骨架与 UI 元数据

- Description: 创建 `introspector/` 目录、`SKILL.md`、`agents/openai.yaml` 和 `references/` 基础结构，保证名字、frontmatter 和默认 prompt 合法。
- Worker role: coding
- Wave: 2
- Acceptance criteria: `introspector/` 目录存在；`SKILL.md` frontmatter 通过 `quick_validate.py`；`agents/openai.yaml` 包含 display name、short description、default prompt。
- Verification: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/introspector`
- Concrete edits: 新增 `introspector/SKILL.md`、`introspector/agents/openai.yaml`、`introspector/references/` 目录与必要文件。
- Interfaces / contracts changed: 新增显式可触发 skill `introspector`。
- Test cases: 名称 hyphen-case；description 触发面覆盖 spec 中的 artifact classes；default prompt 明确使用 `$introspector`。
- Pre-check commands: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/init_skill.py --help`
- Post-check commands: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/introspector`
- Dependencies: Task 1
- Files likely touched: `introspector/SKILL.md`, `introspector/agents/openai.yaml`, `introspector/references/`
- Writable scope: `introspector/`
- Output artifact: `.codex/work/20260622-introspector/artifacts/task2-skill-scaffold.md`
- Estimated scope: M

### Task 3: 写主入口与引用文档 contract

- Description: 将 spec 落入 `SKILL.md` 与 `references/`，明确 workflow、report schema、calibration harness、validation、hard stops、reviewer gate、delta review 和 verdict stability。
- Worker role: coding
- Wave: 3
- Acceptance criteria: 主入口紧凑；`references/workflow.md`、`references/report-schema.md`、`references/calibration-harness.md`、`references/validation.md` 覆盖 spec 核心要求；`SKILL.md` 明确何时 route 到这些引用。
- Verification: `rg "evidence acquisition|falsifier|delta review|verdict stability|block|reviewer" /data/lcq/.codex/skills/introspector /data/lcq/.codex/skills/introspector/references`
- Concrete edits: 填写主入口与四份 references；按 progressive disclosure 拆分长流程。
- Interfaces / contracts changed: 新 skill 的用户可见 contract、output contract、validation contract。
- Test cases: 触发描述能覆盖 `idea/spec/plan/implementation-result/framework-design`；引用文档能回答“什么时候 block”“为什么 verdict 变化”“如何做 calibration”。
- Pre-check commands: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/introspector`
- Post-check commands: `rg "objective extraction|framing audit|evidence acquisition|strongest defense|verification|final verdict|delta review|verdict stability" /data/lcq/.codex/skills/introspector`
- Dependencies: Task 2
- Files likely touched: `introspector/SKILL.md`, `introspector/references/workflow.md`, `introspector/references/report-schema.md`, `introspector/references/calibration-harness.md`, `introspector/references/validation.md`
- Writable scope: `introspector/SKILL.md`, `introspector/references/`
- Output artifact: `.codex/work/20260622-introspector/artifacts/task3-contract.md`
- Estimated scope: M

### Task 4: 产出生产门控与场景验证草案

- Description: 生成 `production-report.md` 草案、scenario gate 记录、任务验证 artifacts，并运行 deterministic validators。
- Worker role: coding
- Wave: 4
- Acceptance criteria: `production-report.md` 草案存在并通过 draft validator；scenario gate 写明 RED/GREEN；task verification artifact 记录命令与结果。
- Verification: `python3 /data/lcq/.codex/skills/skill-tokenless/scripts/validate_skill_production.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
- Concrete edits: 写 `artifacts/production-report.md`、`artifacts/task4-verification.md`、必要 task execution/verification notes。
- Interfaces / contracts changed: 无新用户接口；新增生产门控证据。
- Test cases: `quick_validate.py` 通过；grep 能发现关键 contract 词；scenario gate 覆盖 anti-sycophancy、block、delta review、stability check。
- Pre-check commands: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/introspector`
- Post-check commands: `python3 /data/lcq/.codex/skills/skill-tokenless/scripts/validate_skill_production.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
- Dependencies: Task 3
- Files likely touched: `.codex/work/20260622-introspector/artifacts/production-report.md`, `.codex/work/20260622-introspector/artifacts/task4-verification.md`, `.codex/work/20260622-introspector/artifacts/task4-execution.md`
- Writable scope: `.codex/work/20260622-introspector/artifacts/production-report.md`, `.codex/work/20260622-introspector/artifacts/task4-verification.md`, `.codex/work/20260622-introspector/artifacts/task4-execution.md`
- Output artifact: `.codex/work/20260622-introspector/artifacts/task4-validation.md`
- Estimated scope: S

### Task 5: 最终 reviewer gate 与收尾验证

- Description: 运行 draft readiness、生成最终 reviewer 报告、更新 production report 为 final、写 final report 并完成 execution validator。
- Worker role: review
- Wave: 5
- Acceptance criteria: readiness 通过；最终 reviewer 报告 `PASS`；production report final validator 通过；`validate_execution.py` 返回 `VALID`；`artifacts/final-report.md` 与 `review-introspector-final.md` 存在。
- Verification: `python3 /data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/review-introspector-final.md --root /data/lcq/.codex/skills && python3 /data/lcq/.codex/skills/plan2do/scripts/pre_review_ready.py /data/lcq/.codex/skills/.codex/work/20260622-introspector --stage final --require-production-report --require-final-report && python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260622-introspector`
- Concrete edits: 写 `review-introspector-final.md`、更新 `artifacts/production-report.md`、写 `artifacts/review.md`、`artifacts/final-report.md`，若 reviewer 指出缺陷则写 `artifacts/rework-guidance.md`。
- Interfaces / contracts changed: 无新用户接口；完成正式接受门控。
- Test cases: reviewer report validator 通过；production report final validator 通过；execution validator 通过；final report 包含 verification 行。
- Pre-check commands: `python3 /data/lcq/.codex/skills/plan2do/scripts/pre_review_ready.py /data/lcq/.codex/skills/.codex/work/20260622-introspector --stage draft --require-production-report --require-final-report`
- Post-check commands: `python3 /data/lcq/.codex/skills/skill-tokenless/scripts/validate_skill_production.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final && python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260622-introspector`
- Dependencies: Task 4
- Files likely touched: `.codex/work/20260622-introspector/review-introspector-final.md`, `.codex/work/20260622-introspector/artifacts/production-report.md`, `.codex/work/20260622-introspector/artifacts/review.md`, `.codex/work/20260622-introspector/artifacts/final-report.md`
- Writable scope: `.codex/work/20260622-introspector/review-introspector-final.md`, `.codex/work/20260622-introspector/artifacts/production-report.md`, `.codex/work/20260622-introspector/artifacts/review.md`, `.codex/work/20260622-introspector/artifacts/final-report.md`
- Output artifact: `.codex/work/20260622-introspector/review-introspector-final.md`
- Estimated scope: M

## Step-by-Step Plan

1. 运行 `python /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/plan.md --mode light` 验证计划本身。
2. 运行 `python /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/plan.md` 生成 `.codex/work/20260622-introspector/execution/tasks.json`。
3. 写 `.codex/work/20260622-introspector/artifacts/context-wave1.md`，记录 `spec.md`、`plan.md`、`skill-production-gate.md` 为权威源。
4. 在 `introspector/` 下创建 `SKILL.md`、`agents/openai.yaml`、`references/` 基础结构。
5. 填写 `introspector/SKILL.md`，保留触发面、workflow 摘要、引用路由、hard stops、mandatory reviewer gate。
6. 填写 `introspector/references/workflow.md` 与 `introspector/references/report-schema.md`，覆盖 verdict、falsifier、delta review、verdict stability。
7. 填写 `introspector/references/calibration-harness.md` 与 `introspector/references/validation.md`，覆盖 benchmark、scenario gate、cleanup、review handoff。
8. 运行 `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/introspector` 与 `rg` 检查关键 contract 词。
9. 写 `.codex/work/20260622-introspector/artifacts/production-report.md`、`.codex/work/20260622-introspector/artifacts/task4-verification.md` 和 `.codex/work/20260622-introspector/artifacts/task4-execution.md`。
10. 运行 draft `validate_skill_production.py` 与 `pre_review_ready.py`，然后写 `review-introspector-final.md`、更新 final production report，并运行 `validate_execution.py`。

## Parallelization

顺序执行。Task 2 创建骨架后，Task 3 才能安全写引用文档；Task 4 依赖 contract 完整后才能做 production report；Task 5 必须在所有非 review 任务产物齐备后运行。各 wave 无同波可写路径重叠。

## Files / Components Likely Affected

- `introspector/SKILL.md`
- `introspector/agents/openai.yaml`
- `introspector/references/workflow.md`
- `introspector/references/report-schema.md`
- `introspector/references/calibration-harness.md`
- `introspector/references/validation.md`
- `.codex/work/20260622-introspector/plan.md`
- `.codex/work/20260622-introspector/manifest.yaml`
- `.codex/work/20260622-introspector/execution/tasks.json`
- `.codex/work/20260622-introspector/artifacts/`
- `.codex/work/20260622-introspector/review-introspector-final.md`

## Owners / Responsibilities

主代理执行全部任务。`reviewer` 以 inline heavy 方式提供最终 gate，因为当前 run 未显式授权子代理 reviewer delegation。

## Validation Plan

- `python /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/plan.md --mode light`
- `python /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/plan.md`
- `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/introspector`
- `rg "block|falsifier|delta review|verdict stability|evidence acquisition|reviewer" /data/lcq/.codex/skills/introspector /data/lcq/.codex/skills/introspector/references`
- `python3 /data/lcq/.codex/skills/skill-tokenless/scripts/validate_skill_production.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/artifacts/production-report.md --root /data/lcq/.codex/skills --stage draft`
- `python3 /data/lcq/.codex/skills/plan2do/scripts/pre_review_ready.py /data/lcq/.codex/skills/.codex/work/20260622-introspector --stage draft --require-production-report --require-final-report`
- `python3 /data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/review-introspector-final.md --root /data/lcq/.codex/skills`
- `python3 /data/lcq/.codex/skills/skill-tokenless/scripts/validate_skill_production.py /data/lcq/.codex/skills/.codex/work/20260622-introspector/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`
- `python /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260622-introspector`

## Rollout Plan

本地 skill 落地，无部署。完成后通过文件存在与 validator 结果生效；未来会在 skill 列表中可被显式触发。

## Monitoring / Observability

通过 `Skill Monitor` incident、`calibration harness` 手动结果、reviewer 报告、以及未来使用时的 self-review artifact 观察质量。无运行时服务指标。

## Documentation / ADR Updates

ADR: Not needed。当前变更是新增本地 skill 与 workflow contract，不涉及仓库级架构决策文件。

## Rollback / Recovery Plan

使用 `git -C /data/lcq/.codex/skills diff -- introspector .codex/work/20260622-introspector` 检查本次改动；若 validator 发现行为损失，只回滚 `introspector/` 与本 workspace 的新增文件，不做破坏性 `git reset`。

## Abort Criteria

- `validate_plan_contract.py` 在一次修复后仍失败。
- `quick_validate.py` 在一次修复后仍失败。
- `validate_skill_production.py` draft/final 任一阶段失败且两轮 rework 后仍未通过。
- 最终 reviewer gate 无法得到 `PASS`。

## Risks

- contract 过密可能再次引入 spec 级过载。
- 没有真实子代理 forward-test 时，`calibration harness` 仍以静态案例为主。
- reviewer inline heavy 与主执行线程存在 reasoning style 相关性，虽已通过 adversarial focus 缓解，但仍非完全独立。

## Open Questions

- `calibration harness` 的最小案例集是否还需要单独的 fixture 文件，还是文档描述足够。
- `reviewer` heavy gate 的默认 adversarial packet 是否需要未来固化成独立 reference。

## Plan Self-Review

- 每个任务都给出了 exact writable scope，且同 wave 无写路径重叠。
- 每个行为变化都要求 coverage 或 smoke-style evidence：`quick_validate.py`、grep contract checks、production validators、review validator、execution validator。
- 所有 unknown 都放在 `Assumptions` 或 `Open Questions`，没有藏在 Task 文字里。
- rollback、abort criteria、monitoring 都已经具体到 path 与 command，适合当前风险级别。
- 新鲜 agent 可以直接从 Task 1 开始执行：它知道要先验证 `plan.md`、再生成 `tasks.json`、再落 context pack。

## Execution Decision

Proceed now per user request.

## Execution Handoff

- Goal: 落地 `Introspector` skill，并用 `plan2do` 与 `reviewer` 完成正式门控。
- Current state: `spec.md` 已稳定到 evidence-first 版本；`plan.md` 待验证和执行。
- Authoritative artifacts: `.codex/work/20260622-introspector/spec.md`, `.codex/work/20260622-introspector/plan.md`, `.codex/work/20260622-introspector/artifacts/neutrality-research.md`
- Decisions: light planning mode；primary-agent execution；最终 reviewer 使用 inline heavy；新 skill 采用紧凑主入口 + references 下沉。
- Verification: 运行 plan validator、execution compiler、quick skill validator、draft/final production validators、review report validator、execution validator。
- Remaining risks: 缺少真实子代理 forward-test；reviewer 独立性受当前 run 模式限制。
- Next action: 验证 `plan.md`，再生成 `execution/tasks.json` 并开始实现 `introspector/`。
- Suggested skills: `spec2plan`, `plan2do`, `reviewer`, `skill-creator`, `context-engineering`.
- Redactions / omitted raw data: 未包含原始长日志、无 secrets、无外部凭证。
