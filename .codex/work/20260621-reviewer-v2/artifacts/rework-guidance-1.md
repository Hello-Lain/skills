# Rework Guidance

- Evidence: heavy reviewer forward-test from subagent `10e6d707-f7d1-4070-93c5-76db3d3eb070` returned `REVISE`.
- Defect: validator accepted reports missing `## Mode Decision`, `## Alignment Result`, `## Quality Result`, and missed continuation-line local paths after `Sources:` / `Evidence:`.
- Impact: malformed reviewer reports could pass, weakening false-PASS protection.
- Required change: add regression fixtures, require all v2 sections, validate alignment/quality `Result:`, parse source/evidence continuation blocks, and tighten heavy-route wording.
- Writable scope: `reviewer/scripts/validate_review_report.py`, `reviewer/SKILL.md`, `.codex/work/20260621-reviewer-v2/artifacts/rework-guidance-1.md`.
- Verification: `python3 reviewer/scripts/validate_review_report.py --self-test`; `python3 -m py_compile reviewer/scripts/validate_review_report.py`; `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`.
- Cycle: 1
