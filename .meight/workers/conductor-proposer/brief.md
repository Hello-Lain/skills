[Harness protocol — applies on top of the task below]
- Never run `git commit` or `git push`. Leave all changes in the working tree.
- You are a teammate on this work, not a tool that only executes. If you see a better approach, the brief rests on a wrong assumption, or there's a tradeoff worth weighing before a direction is locked in, don't silently comply or guess — raise it in a final paragraph starting with `QUESTION:` and the orchestrator will discuss and adjust direction with you. Judge by the bar: raise it when the call could change direction — scope, approach, or risk — and just decide local implementation choices yourself, noting them as judgment calls in your report.
- Likewise, when you are genuinely blocked on a decision or missing information that only the orchestrator can provide, end with a `QUESTION:` paragraph stating exactly what you need instead of guessing. Either way you receive the answer as a follow-up turn in this same thread.

---

Role: Proposer.
Goal: Decide ideal responsibilities for local Codex skill `conductor`.
Decision question: What should conductor own, not own, and how should it reduce context pollution while fitting this skill system?
Objective function: higher answer quality in long/multi-branch work; minimal token/context pollution; clear boundaries with codex2codex, plan-grill, skill-tokenless, caveman, domain skills.
Hard constraints:
- Read only. Do not edit files.
- Consider only local files relevant to skills: conductor/SKILL.md + references, codex2codex/SKILL.md, plan-grill/SKILL.md, skill-tokenless/SKILL.md, caveman/SKILL.md.
- Preserve codex2codex explicit-trigger/worker-delegation role.
- Preserve plan-grill as plan.md production workflow.
- Preserve skill-tokenless as token optimization workflow.
- Avoid raw branch/worker history flowing into master context.
Known options: conductor as governance/router only; conductor as full orchestrator; conductor as context firewall; conductor as plan/worker wrapper.
Unknowns: exact user workflow; whether to modify files now.
Failure modes: ceremony bloat; duplicated skill responsibilities; master context polluted by branch reports; stale summaries becoming false authority.
Evidence required: cite concrete local skill lines/concepts by filename/section, not exact line numbers.
Decision record output. Use headings:
## 提案
## 理由
## 证据
## 风险
## 替代方案考虑
End with no QUESTION unless blocked or a better direction requires lead decision.

