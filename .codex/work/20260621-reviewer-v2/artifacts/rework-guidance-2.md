# Rework Guidance

- Evidence: compact heavy reviewer forward-test from subagent `590aa8b2-0abd-4023-a879-26fd87f77e39` returned `REVISE`.
- Defect: validator had remaining false-pass/false-fail edges: command evidence with path arguments, block-wide missing markers, required headings matched by prose, loose verdict casing, and loose confidence values.
- Impact: reviewer reports could be rejected incorrectly or accepted outside the v2 schema contract.
- Required change: add regression fixtures, parse command evidence into path-like tokens, scope missing markers per line, require exact section headings, enforce exact top-level verdict casing, and validate `Confidence`.
- Writable scope: `reviewer/scripts/validate_review_report.py`, `.codex/work/20260621-reviewer-v2/artifacts/rework-guidance-2.md`.
- Verification: `python3 reviewer/scripts/validate_review_report.py --self-test`; `python3 -m py_compile reviewer/scripts/validate_review_report.py`.
- Cycle: 2
