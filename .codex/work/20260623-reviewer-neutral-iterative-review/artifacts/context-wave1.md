TASK:
- Plan path: `.codex/work/20260623-reviewer-neutral-iterative-review/plan.md`
- Current task: Tasks 1-4
- Phase: implement
- Context state: focused
- Risk level: Medium

AUTHORITATIVE SOURCES:
- User goal: implement confirmed spec using skills.
- Plan sections: Goal, Upstream Coverage, Implementation Map, Task Breakdown, Validation Plan, Abort Criteria, Execution Handoff.
- Upstream artifacts: `.codex/work/20260623-reviewer-neutral-iterative-review/spec.md`
- Files/tests/configs: `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`, `reviewer/scripts/validate_review_report.py`, `skill-tokenless/references/skill-production-gate.md`
- Existing pattern: reviewer uses v2 report sections and `PASS|REVISE|BLOCK`; introspector has neutral root-objective/framing/evidence principles.

CONSTRAINTS:
- Must: preserve reviewer verdict taxonomy, lite/heavy routing, report validator compatibility, and bounded review cost.
- Must: require continued critical/major issue discovery after the first obvious issue.
- Must: require PASS convergence basis in existing report sections.
- Must not: copy introspector wholesale, require infinite loops, make every review heavy, or edit validator scripts for v1.

UNKNOWN / CONFLICT:
- None blocking. Report template can carry convergence via `Residual Risks` and `Recheck Plan`.
