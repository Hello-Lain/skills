# Task 4 Execution

- Task: Integrate production gate into plan and execution contracts.
- Changed files:
  - `spec2plan/SKILL.md`
  - `spec2plan/references/plan-contract.md`
  - `plan2do/SKILL.md`
  - `plan2do/references/execution-contract.md`
- Behavior:
  - `spec2plan` now requires Skill Production Gate tasks for new/material skill work.
  - `plan2do` now requires a validated production report before final success for material skill work.
- Verification:
  - `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-skill-production-gate/plan.md --mode light`: PASS
  - `python3 .system/skill-creator/scripts/quick_validate.py plan2do`: PASS
  - `python3 .system/skill-creator/scripts/quick_validate.py spec2plan`: PASS
- Residual risk: `plan2do/scripts/validate_execution.py` remains structural; production report validation supplies the skill-gate-specific evidence.
