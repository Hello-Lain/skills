## 提案
`conductor` 最优定位：**治理路由器 + context firewall**，不是完整执行编排器。

应 owned：

- Master hygiene：只保留目标、约束、已确认决策、风险、下一步、批准摘要。
- Ambient routing：先静默判定 `master / branch / dispatch / explainer / merge`。
- Branch governance：分支卡、稳定标题、允许上下文、完成条件、返回条件。
- Wave/dependency planning：判断并行、依赖、gate、optional。
- Merge gate：只合并用户确认完成后的 `completion-report.md`，默认只进 master 一个短 merge note。
- Staleness control：master 目标/约束变更时标记相关 active branches stale。
- Artifact discipline：维护 `branch-map.md` / `conductor.yaml`，用 branch brief + completion report 作为隔离边界。

不应 owned：

- Worker delegation / arbitration execution：归 `codex2codex`。
- `plan.md` 生产级规划：归 `plan-grill`。
- skill 压缩/重构：归 `skill-tokenless`。
- terse reply / compression style：归 `caveman`。
- Domain-specific implementation/review/research：归具体 domain skill 或普通 Codex flow。
- Raw branch history summarization：默认禁止，除非用户要求 audit/debug。

Context pollution 减法规则：

- 小任务留 master，不创建 branch card/map/report。
- Branch 只收 brief、显式文件、批准摘要、branch-local user msg。
- Branch 决策先 local，master 确认前不成全局事实。
- Master 不读 raw branch history。
- Completion report 进入 master 前需用户确认；默认只使用 `Suggested Merge Note`，150 words max。
- Dispatch/explainer 作为 sidecar，输出只回流决策/答案，不回流过程。

## 理由
该边界最大化 long/multi-branch 质量，同时最小化 master 污染。

- `conductor` 擅长的是控制流、上下文边界、合并门禁；不是做事本身。
- `codex2codex` 已定义 lead/worker 分工、meight worker lifecycle、worker verification；若 conductor 再管 worker，会重复且冲突。
- `plan-grill` 已定义 plan artifact workflow；conductor 应只把 `plan.md` 需求 route 到它。
- `skill-tokenless` 已定义 skill 优化流程；conductor 不应替代 token optimizer。
- `caveman` 已定义 reply/delegation compression style；conductor 可受益于其低污染原则，但不应 own style config。

最佳模型：`conductor` 是**master session 的 airlock**。脏工作可发生在 branch/dispatch/explainer/worker，但只有已验证、已批准、短格式结果能穿过 airlock。

## 证据
- [conductor/SKILL.md](/data/lcq/.codex/skills/conductor/SKILL.md), `Ambient Mode`：要求先静默 route；小任务留 master；master 只保留 goals/constraints/decisions/risks/next steps/approved summaries。
- [conductor/SKILL.md](/data/lcq/.codex/skills/conductor/SKILL.md), `Local Routing`：明说 `$plan-grill` 处理 production `plan.md`；`$codex2codex` 处理 explicit worker delegation；`conductor`: governance only。
- [conductor/SKILL.md](/data/lcq/.codex/skills/conductor/SKILL.md), `Core Rules`：master owns overview/confirmed decisions；branches only receive branch brief/approved summaries/explicit files；do not read raw branch history unless audit/debug；merge only after explicit approval。
- [conductor/SKILL.md](/data/lcq/.codex/skills/conductor/SKILL.md), `Routing` + `Waves`：conductor owns branch classification, dependency order, wave gates, optional/explainer handling。
- [conductor/references/branch-brief-template.md](/data/lcq/.codex/skills/conductor/references/branch-brief-template.md), `Allowed Context` + `Forbidden Assumptions`：branch may use only brief/listed files/approved summaries/local msgs；must not assume master history; must not summarize sibling raw context。
- [conductor/references/completion-report-template.md](/data/lcq/.codex/skills/conductor/references/completion-report-template.md), `Suggested Merge Note`：explicitly says this is the only text intended for master context unless edited after approved merge。
- [conductor/references/branch-map-template.md](/data/lcq/.codex/skills/conductor/references/branch-map-template.md), `Today View`, `Wave Plan`, `Branch Registry`, `Staleness Warnings`：supports conductor as project-control artifact, not execution engine。
- [codex2codex/SKILL.md](/data/lcq/.codex/skills/codex2codex/SKILL.md), `Use` + `Workflow` + `Contracts`：explicit-trigger only; lead owns decomposition/arbitration/integration/verification; workers never commit/push/recurse; structured worker outputs validated by lead。
- [plan-grill/SKILL.md](/data/lcq/.codex/skills/plan-grill/SKILL.md), `Workflow` + `Output`：owns `.plan-grill/<task-slug>/plan.md`, planner/grill/synthesizer phases, required plan sections, no execution by default。
- [skill-tokenless/SKILL.md](/data/lcq/.codex/skills/skill-tokenless/SKILL.md), `Non-Negotiables` + `Workflow`：owns preserving triggers/gates/validation while shrinking skill docs。
- [caveman/SKILL.md](/data/lcq/.codex/skills/caveman/SKILL.md), `Reply Style` + `Delegation`：owns terse style/context-saving delegation formats, not branch governance。

## 风险
- Ceremony bloat：branch cards/maps for trivial work would reduce velocity. Mitigation: enforce `Ambient Mode`: no ceremony unless control flow changes。
- Responsibility duplication：conductor could drift into codex2codex/plan-grill territory. Mitigation: hard route explicit worker delegation to `codex2codex`, plan artifacts to `plan-grill`。
- Stale summary false authority：merge notes may become outdated or overtrusted. Mitigation: mark proposed global decisions separately; master confirmation required。
- Under-context branches：strict firewall may starve branch work. Mitigation: branch brief must list explicit files, approved summaries, inputs, completion criteria。
- Hidden dependency errors：parallel branches from same snapshot can conflict later. Mitigation: dependency pass before opening branches; branch-map staleness warnings。
- User workflow unknown：exact preferred ceremony level unknown. Judgment call: default low ceremony, escalate only when durable branches/deps/merge gates matter。

## 替代方案考虑
- Governance/router only：too weak alone. Good for boundaries, but misses active pollution controls like allowed-context briefs, completion-report gate, staleness handling。
- Full orchestrator：rejected. Duplicates `codex2codex`, `plan-grill`, domain skills; increases ceremony/context load。
- Context firewall：best core identity. Directly matches master-clean goal and hard constraint against raw branch/worker history pollution。
- Plan/worker wrapper：rejected as primary role. It should route to `plan-grill` / `codex2codex`, not wrap their internals。
- Current best synthesis：**conductor = ambient governance router with context-firewall artifacts**; escalation creates branch cards/waves/reports only when needed, then routes specialized work outward.
