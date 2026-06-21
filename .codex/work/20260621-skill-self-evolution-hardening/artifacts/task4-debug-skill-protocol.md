# Task 4 Execution: Debug-Skill Trace And Audit Protocol

- Status: COMPLETE
- Changed files: `debug-skill/SKILL.md`, `debug-skill/references/report-template.md`, `debug-skill/references/hermes-reuse.md`, `debug-skill/scripts/skill_audit_core.py`
- Acceptance: `debug-skill` now documents trace mode and deep audit mode; reports include trace fields and promotion gates; helper CLI supports `--trace-skeleton`.
- Hermes protocol fields: evaluation/task input, trace, constraints, fitness dimensions including safety, candidate improvements, promotion gates, redaction, and human approval.
- Verification: `python3 debug-skill/scripts/skill_audit_core.py --self-test`: PASS (`SELF_TEST_OK`)
- Trace probe: `.codex/work/20260621-skill-self-evolution-hardening/artifacts/debug-skill-trace-probe.md`
- Raw data omitted: no external traces or private history used.
