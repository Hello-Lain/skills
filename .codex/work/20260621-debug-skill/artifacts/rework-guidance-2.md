# Rework Guidance

- Evidence: `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill` failed with `review artifact lacks Verdict: PASS or Verdict: FAIL: .../artifacts/final-report.md`.
- Defect: Task 5 is a review-role task whose output artifact is `final-report.md`; the validator requires a standalone `Verdict: PASS` or `Verdict: FAIL` line in every review-role output artifact.
- Impact: Execution could not be marked complete despite `artifacts/review.md` containing `Verdict: PASS`.
- Required change: Add standalone `Verdict: PASS` line to `artifacts/final-report.md`.
- Writable scope: `.codex/work/20260621-debug-skill/artifacts/final-report.md`.
- Verification: `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-debug-skill`.
- Cycle: 2
