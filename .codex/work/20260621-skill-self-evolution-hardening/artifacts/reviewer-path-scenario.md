# Reviewer Path Scenario

- Scenario: reviewer subagent receives a packet for `.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md`.
- Coordinator cwd: `/data/lcq/.codex/skills`.
- Cwd-relative artifact path: `.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md`.
- Absolute artifact path: `/data/lcq/.codex/skills/.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md`.
- Required check before missing finding: `pwd` plus `test -e .codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md` and `test -e /data/lcq/.codex/skills/.codex/work/20260621-skill-self-evolution-hardening/artifacts/production-report.md`.
- Expected reviewer behavior: cite the checked cwd and path form; do not report a missing artifact from a different workspace root.
- PASS condition: a missing-artifact finding is valid only after both supplied local path forms fail or commands are disallowed and the report labels command verification unavailable.
