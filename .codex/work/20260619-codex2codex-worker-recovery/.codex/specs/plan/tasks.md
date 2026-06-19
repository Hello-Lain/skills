# Codex2Codex Tasks: plan

Source plan: `/data/lcq/.codex/skills/.codex/work/20260619-codex2codex-worker-recovery/plan.md`

## Wave 1

- [ ] [coding] Task 1: Harden worker output validation gates | `codex2codex/scripts/validate_wave.py`, `codex2codex/scripts/validate_result_contract.py`, `codex2codex/scripts/test_worker_recovery_contracts.py` | Verify: `python3 -m unittest codex2codex/scripts/test_run_wave_salvage.py codex2codex/scripts/test_worker_recovery_contracts.py` Output: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-1-validation-gates.md`

## Wave 2

- [ ] [coding] Task 2: Add failure taxonomy and recovery decision helpers | `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_recovery.py` | Verify: `python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py` Output: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-2-taxonomy.md`
- [ ] [coding] Task 3: Add minimal worker status support if needed | `codex2codex/meight.py`, `codex2codex/scripts/test_meight_status_recovery.py` | Verify: `python3 codex2codex/meight.py --help && python3 -m unittest codex2codex/scripts/test_meight_status_recovery.py` Output: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-3-meight-status.md`

## Wave 3

- [ ] [coding] Task 4: Wire bounded recovery into run_wave | `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_recovery.py` | Verify: `python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py` Output: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-4-recovery-loop.md`

## Wave 4

- [ ] [coding] Task 5: Implement scoped PATCH_BODY fallback | `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_recovery.py`, `codex2codex/scripts/test_run_wave_salvage.py` | Verify: `python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py codex2codex/scripts/test_run_wave_salvage.py` Output: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-5-patch-body.md`

## Wave 5

- [ ] [coding] Task 6: Add preflight and user-visible recovery controls | `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/test_run_wave_recovery.py` | Verify: `python3 codex2codex/scripts/run_wave.py --help && python3 codex2codex/scripts/run_plan.py --help && python3 -m unittest codex2codex/scripts/test_run_wave_recovery.py` Output: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-6-preflight-controls.md`

## Wave 6

- [ ] [coding] Task 7: Update worker prompts and documentation | `codex2codex/SKILL.md`, `codex2codex/README.md`, `codex2codex/ARCHITECTURE.md`, `codex2codex/scripts/prepare_wave.py` | Verify: `rtk grep -n "lead fallback\\|PATCH_BODY\\|INFRA_FAILED\\|CONTRACT_FAILED\\|TASK_BLOCKED" codex2codex/SKILL.md codex2codex/README.md codex2codex/ARCHITECTURE.md codex2codex/scripts/prepare_wave.py` Output: `.codex/work/20260619-codex2codex-worker-recovery/artifacts/task-7-docs.md`

## Wave 7

- [ ] [review] Task 8: Final recovery review | `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/run_plan.py`, `codex2codex/scripts/validate_wave.py`, `codex2codex/scripts/validate_result_contract.py`, `codex2codex/scripts/prepare_wave.py`, `codex2codex/meight.py`, `codex2codex/SKILL.md`, `codex2codex/README.md`, `codex2codex/ARCHITECTURE.md` | Verify: `python3 -m unittest discover codex2codex/scripts -p "test_*.py" && python3 codex2codex/scripts/run_plan.py .codex/work/20260619-codex2codex-worker-recovery/plan.md --dry-run` Output: `.codex/work/20260619-codex2codex-worker-recovery/review.md`
