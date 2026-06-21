# Rework Guidance

- Evidence: `.codex/work/20260621-plan2do/review-plan2do.md` returned `Verdict: FAIL`.
- Defect: Context-governance and final-acceptance gates are underspecified; self-bootstrap behavior is ambiguous.
- Impact: `plan2do` could still pollute context, accept stale summaries, skip decision packets, or falsely claim self-use before the skill exists.
- Required change: Add explicit context-engineering triggers, final acceptance checklist, incomplete-status rule, and self-bootstrap rule.
- Writable scope: `/data/lcq/.codex/skills/plan2do/SKILL.md`; `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- Verification: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`; `rg "Self-bootstrap|Decision Packet|Context Capsule|COMPACT_NOW|Final Acceptance|INCOMPLETE" /data/lcq/.codex/skills/plan2do`
- Cycle: 1
