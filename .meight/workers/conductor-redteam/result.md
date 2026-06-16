## 审查对象
`conductor` 扩展/优化边界。证据来自本地 docs：

- `conductor/SKILL.md` sections: `Ambient Mode`, `Local Routing`, `Core Rules`, `Branch Card`, `Routing`, `Waves`, `Lifecycle`, `Artifacts`
- `conductor/references/branch-brief-template.md`
- `conductor/references/branch-map-template.md`
- `conductor/references/completion-report-template.md`
- `codex2codex/SKILL.md`
- `plan-grill/SKILL.md`
- `skill-tokenless/SKILL.md`
- `caveman/SKILL.md`

核心判断：`conductor` 应保持“治理/路由/合并门禁”，不应扩成 planner、executor、worker runtime、token optimizer、Trellis 替代品。

## 假设挑战
1. “更多 branch card → 更可靠”是假设过强。  
   `conductor/SKILL.md` `Ambient Mode` 已写：small/single-thread/immediate tasks 留在 master；trivial tasks 不建 branch cards/maps/reports/session titles。若扩展成默认建卡，会直接制造 ceremony，降低吞吐。

2. “branch 决策可自动进入全局”危险。  
   `conductor/SKILL.md` `Core Rules` 写：branch decisions local until master confirms。`branch-brief-template.md` `Global Decision Rule` 也要求把跨分支/架构/范围/命名/目标变更放到 `Proposed Global Decisions`。不要加“branch 可自动更新 master truth”。

3. “completion report 越完整越好”不成立。  
   `completion-report-template.md` 限制 `Result` 为 3-6 sentences，`Suggested Merge Note` <=150 words，且说明这是唯一 intended master-session context。不要把完整报告、原始分支历史、长推理链合并回 master。

4. “conductor 可统一所有规划”会重复 `plan-grill`。  
   `conductor/SKILL.md` `Local Routing` 明确 `$plan-grill`: production `plan.md` or safer plan artifact。`plan-grill/SKILL.md` 自己有 Planner/Grill/Synthesizer、风险/回滚/验证 gate。不要把 plan.md hardening、风险审计、执行计划模板搬进 conductor。

5. “conductor 可自动派 worker”会冲突 `codex2codex`。  
   `codex2codex/SKILL.md` `Use`: only explicit `/codex2codex`；lead owns decomposition/arbitration/integration/verification。`conductor/SKILL.md` `Local Routing` 也说 `$codex2codex`: explicit meight worker delegation。不要让 conductor ambient mode 静默启动 worker 或绕过 meight contracts。

6. “优化 conductor = 加更多上下文压缩逻辑”方向错。  
   `skill-tokenless/SKILL.md` 负责 skill token/context optimization，要求 keep `SKILL.md` lean、细节放 `references/`、保留 gates 并 validate。`caveman/SKILL.md` 负责 terse/context-saving delegation style。conductor 不应复制这些能力，只应引用/尊重边界。

## 遗漏风险
1. Small-task bureaucracy。  
   风险：用户只要一个小修/解释，却被 branch card、branch map、completion report 包围。  
   证据：`conductor/SKILL.md` `Ambient Mode` 已反向约束。扩展时最该保护这条。

2. Hidden stale state。  
   风险：`branch-map.md` / `conductor.yaml` 成第二事实源，master 以为状态新，实际 branch 已 stale。  
   证据：`conductor/SKILL.md` `Lifecycle` 仅要求 master goals/constraints change 时标记 affected active branches stale。缺口：若 branch 自己发现新事实但未 report，map 仍可能误导。

3. Worker over-read。  
   风险：branch/worker 为“补上下文”读取 master/sibling/raw history，污染判断。  
   证据：`branch-brief-template.md` `Allowed Context` 限制只用 brief、explicit files、approved summaries、branch-local user messages；`Forbidden Assumptions` 禁止 sibling raw context。扩展不要放宽。

4. Report laundering。  
   风险：verbose completion report 被当作 approved truth 注入 master，掩盖 branch-local assumptions。  
   证据：`conductor/SKILL.md` `Core Rules`: merge only explicit user approval；`completion-report-template.md` 仅 `Suggested Merge Note` intended for master context。

5. Dispatch creep。  
   风险：dispatch 从“branch planning only”变成 second master。  
   证据：`conductor/SKILL.md` `Session Types`: dispatch = Branch planning only；`Routing`: dispatch only when planning >2-3 turns, >3 candidate branches, unclear deps, parallel/serial debate。

6. Trellis contamination。  
   风险：branch briefs/reports/raw summaries 写入 Trellis execution/check logs，污染 implementation context。  
   证据：`conductor/SKILL.md` `Artifacts`: Do not put branch briefs, completion reports, raw conversation summaries into Trellis `implement.jsonl` or `check.jsonl` unless user confirms.

7. Role creep into execution quality ownership。  
   风险：conductor 开始评判 code quality、写 validation policy、执行 merge checks，重复 lead/plan-grill/codex2codex reviewer。  
   证据：`conductor/SKILL.md` `Local Routing`: governance only; do not replace planners, executors, Trellis, worker tools。

## 反证
现有 conductor 已有不少正确护栏，不需要“大扩展”：

- `Ambient Mode` already blocks ceremony for trivial tasks.
- `Local Routing` already delegates plan artifacts to `$plan-grill`, worker delegation to `$codex2codex`.
- `Core Rules` already protects master context: approved summaries only, local branch decisions, explicit completion/merge approval, no raw branch history by default.
- `Branch Brief` template already has context minimization and global-decision quarantine.
- `Completion Report` template already caps merge payload via <=150-word `Suggested Merge Note`.
- `Branch Map` template already prefers visible state, active branch limit 2, planned/blocked separation.

结论：优化应是“收紧边界/减少误触发/防污染”，不是新增 conductor 能力面。

## 替代方案
1. Add “Do Not Add” charter to conductor, not new workflow:
   - no automatic worker spawn
   - no automatic plan.md generation
   - no code execution/review ownership
   - no globalizing branch decisions
   - no raw-history merge
   - no branch ceremony for small tasks

2. Add routing quick test before any branch card:
   - Can master finish in one pass?
   - Is there durable parallel work?
   - Is dependency ordering unclear?
   - Would branch output be a bounded artifact?
   - If all no → stay master.

3. Add merge budget:
   - default master merge = `Suggested Merge Note` only
   - full report read only for audit/debug/risk review
   - raw branch history never unless explicit audit request

4. Add staleness rule:
   - any branch report with changed assumptions marks dependent planned/active branches stale
   - stale branch refresh requires explicit updated brief, not informal memory

5. Keep optimization external:
   - token/doc slimming → `skill-tokenless`
   - terse output/delegation format → `caveman`
   - production plan hardening → `plan-grill`
   - worker runtime/council/arbitration → `codex2codex`

Best direction: make conductor smaller and stricter. Add negative boundaries + merge/context gates; avoid expanding it into planner/worker/optimizer.
