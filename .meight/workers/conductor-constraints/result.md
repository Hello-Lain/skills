## 约束清单

**Conductor 允许职责**
- 会话治理：master / branch / dispatch / explainer / merge 路由。
- 轻量分流：小任务留 master，复杂任务才建 branch card。
- 分支治理：依赖 pass、wave plan、branch map、branch brief、completion report。
- 上下文边界：branch 只收 brief、显式文件、已批准摘要、branch-local 消息。
- 决策隔离：branch 决策仅 local；global decision 必须回 master 确认。
- 合并治理：只合并用户批准的 completion report 摘要。

**Conductor 必须 gates**
- 命名技能先读：lead 使用 named skill 前必须读其 `SKILL.md`。
- Branch gate：开真实 branch/session 前必须先展示 branch card，并获用户确认 stable title。
- Dependency gate：开 branch 前必须跑 dependency pass；parallel 仅限同 snapshot 安全项。
- Completion gate：branch 结束后先建议 completion，用户确认后才出 completion report。
- Merge gate：completion report 存在且用户显式批准后才 merge。
- Staleness gate：master 目标/约束变更后，active branch 标 stale，并询问是否 refresh brief。
- Dirty worktree gate：不得建议 destructive git；不得 reset/checkout/clean 未授权改动。

**Conductor 禁止职责**
- 禁止替代 `plan-grill` 写/硬化 production `plan.md`。
- 禁止替代 `codex2codex` 做 worker delegation、review arbitration、Decision Council。
- 禁止替代 `skill-tokenless` 压缩/重构技能。
- 禁止替代 `caveman` 控制 terse style、commit msg style、context-saving delegation pattern。
- 禁止读 raw branch history，除非用户要求 audit/debug。
- 禁止把 branch brief、completion report、raw conversation summary 写入 Trellis execution/check context，除非用户确认。
- 禁止把 branch local/global-impact decision 当 master 已接受。
- 禁止 trivial task 制造 ceremony：branch cards/maps/reports/session titles。

## 合规状态

- `conductor` 当前定位基本合规：明确 “governance only”，并路由 `plan.md` → `$plan-grill`，worker delegation → `$codex2codex`。
- `codex2codex` 契约可共存：Conductor 可决定 “需要 worker/branch”，但实际 meight worker delegation 只能由 `codex2codex` 执行，并保留 lead verification。
- `plan-grill` 契约可共存：Conductor 可做 branch/wave/session planning；production plan artifact 归 `plan-grill`。
- `skill-tokenless` 契约可共存：Conductor 可发现 skill optimization 需求；压缩执行、验证、行为锁定归 `skill-tokenless`。
- `caveman` 契约可共存：Conductor 不应定义回复风格；只可接受当前 Caveman style 作为外层表达约束。
- 用户确认 gates 在 `conductor` 文档中明确存在：card confirm、completion confirm、merge approval。
- Dirty worktree safety 未显式作为 conductor 独立条款，但上层 Codex policy + 本任务约束覆盖；集成说明应补一条 “never destructive git”。

## 违规分析（如有）

- 潜在歧义：`conductor` 描述 “Use proactively...” 可能被误解为可主动启动 worker/branch machinery。
- 合规解释：proactive 只能用于 ambient routing / governance 判断；不能越过 named-skill trigger、branch card confirmation、codex2codex explicit delegation gate。
- 潜在歧义：`branch` 与 `codex2codex worker` 概念易混。
- 合规解释：Conductor branch 是会话治理单元；codex2codex worker 是 meight 执行单元。需要 worker/delegate/council 时必须进入 `codex2codex` 契约。
- 潜在缺口：Conductor docs 未直接声明 “do not use destructive git ops”。
- 建议：在 conductor “Core Rules” 增加短 gate：`Never suggest or run destructive git ops for dirty worktrees; preserve unrelated user changes.`

## 影响评估

- 正向影响：Conductor 可成为顶层协调层，减少 master 污染，强化用户确认、依赖顺序、上下文最小化。
- 风险降低：plan、worker、skill compression、style 均交给专门技能，避免职责膨胀。
- 主要风险：若 Conductor 被实现成 “自动开分支/自动派工/自动合并”，会直接破坏 confirmation gates 与 named-skill contracts。
- 最安全集成边界：Conductor = router + map keeper + gatekeeper；specialized skills = execution owners.
- 推荐落点：保留 conductor 当前 design，补充一条 dirty-worktree safety，并在 routing 文案中明确 “route means hand off after trigger/gate, not execute.”
