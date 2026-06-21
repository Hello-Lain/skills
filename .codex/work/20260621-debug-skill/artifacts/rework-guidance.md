# Rework Guidance

- Evidence: `python3 -m py_compile /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py` failed with `IndentationError: unexpected indent (skill_audit_core.py, line 301)`.
- Defect: `body_line_target` advisory block was over-indented after changing hard size checks to warnings.
- Impact: Helper script could not run; Task 4 verification was invalid after the review fix.
- Required change: Unindent the `results.append(...)` block after `body_lines = len(body.splitlines())`.
- Writable scope: `debug-skill/scripts/skill_audit_core.py`.
- Verification: `python3 -m py_compile /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py && python3 /data/lcq/.codex/skills/debug-skill/scripts/skill_audit_core.py --self-test`.
- Cycle: 1
