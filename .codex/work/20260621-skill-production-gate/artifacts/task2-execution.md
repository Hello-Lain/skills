# Task 2 Execution

- Task: Correct reviewer subagent health policy.
- Changed files:
  - `reviewer/SKILL.md`
  - `reviewer/references/subagent-dispatch.md`
- Behavior:
  - Heavy and mandatory-isolation reviewer subagents now poll exactly 2 times, 45 seconds each only after abnormal signals.
  - Healthy `running` subagents with new activity or plausible progress are not canceled or archived.
  - Wait/provider/network fluctuation is not a valid inline fallback reason.
  - Confirmed abnormal state returns `BLOCK` or relaunches once with a narrower packet after cleanup.
- Verification:
  - `python3 reviewer/scripts/validate_review_report.py --self-test`: PASS
  - `python3 .system/skill-creator/scripts/quick_validate.py reviewer`: PASS
  - `rg "2 times|45 seconds|inline fallback|healthy|abnormal|provider|network|downgrade" reviewer/SKILL.md reviewer/references/subagent-dispatch.md`: PASS
- Residual risk: actual provider fluctuation behavior still depends on agent manager status APIs.
