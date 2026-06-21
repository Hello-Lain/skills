# Rework Guidance

- Evidence: `rg "^## Final Report$|^## Final Acceptance$" /data/lcq/.codex/skills/plan2do/references/execution-contract.md -n` found two `## Final Report` headings.
- Defect: Duplicate heading makes the final acceptance/report contract ambiguous.
- Impact: A future agent could miss the intended final acceptance gate.
- Required change: Remove the stray `## Final Report` heading before `## Final Acceptance`.
- Writable scope: `/data/lcq/.codex/skills/plan2do/references/execution-contract.md`
- Verification: `rg "^## Final Report$|^## Final Acceptance$" /data/lcq/.codex/skills/plan2do/references/execution-contract.md -n`
- Cycle: 2
