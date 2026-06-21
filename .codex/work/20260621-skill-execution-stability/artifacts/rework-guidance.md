# Rework Guidance

- Evidence: reviewer report returned `REVISE` with two major findings.
- Defect: draft readiness allowed blocked non-review tasks when final report was incomplete; production report changed-file validation only checked backticked paths.
- Impact: reviewer could launch before implementation was review-ready; production report could pass with nonexistent unbackticked paths.
- Required change: require non-review tasks to be `complete` for readiness; parse normal changed-file bullet paths in addition to backticked paths; add negative self-tests.
- Writable scope: `plan2do/scripts/pre_review_ready.py`; `skill-tokenless/scripts/validate_skill_production.py`; `.codex/work/20260621-skill-execution-stability/artifacts/`.
- Verification: `python3 plan2do/scripts/pre_review_ready.py --self-test`; `python3 skill-tokenless/scripts/validate_skill_production.py --self-test`; draft readiness; focused reviewer recheck.
- Cycle: 1.
