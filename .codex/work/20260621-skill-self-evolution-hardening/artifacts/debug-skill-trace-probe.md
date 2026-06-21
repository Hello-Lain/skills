# Debug Skill Trace: debug-skill trace/deep-audit protocol

- Mode: trace
- Skill(s): `debug-skill`
- Task: add lightweight trace mode and deep audit protocol split.
- Trigger: user requested implementation with `debug-skill` in the workflow.
- Loaded instructions: `debug-skill/SKILL.md`, `debug-skill/references/report-template.md`, `debug-skill/references/hermes-reuse.md`, `debug-skill/scripts/skill_audit_core.py`.
- Decisions: trace mode captures in-run trajectory without web search; deep audit mode keeps reuse search, candidate scoring, promotion gates, and recommendations.
- Actions: patched `debug-skill` docs and helper CLI with `--trace-skeleton`.
- Failures / friction: none in helper self-test after patch.
- Recovery: not needed.
- Validators: `python3 debug-skill/scripts/skill_audit_core.py --self-test`: PASS.
- Outcome: helper emits required trace fields and preserves human approval before edits.
- Optimization hints: future deep audits can convert traces into candidate improvements with reuse attribution.
- Redaction: none needed; no secrets in fixture.
- Human approval required before edits: yes
