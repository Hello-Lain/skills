# Task 4 Validation

- Command: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/plan2do`
- Outcome: `Skill is valid!`
- Command: `rg "Self-Bootstrap|Decision Packet|Context Capsule|COMPACT_NOW|Final Acceptance|INCOMPLETE" /data/lcq/.codex/skills/plan2do`
- Outcome: required terms found.
- Command: `rg "^## Final Report$|^## Final Acceptance$" /data/lcq/.codex/skills/plan2do/references/execution-contract.md -n`
- Outcome: one `Final Acceptance` heading and one `Final Report` heading.
- Command: `python /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-plan2do/plan.md --mode light`
- Outcome: `VALID`
- Status: complete.
