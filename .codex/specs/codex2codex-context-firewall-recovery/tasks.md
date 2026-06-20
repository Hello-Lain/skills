# Codex2Codex Tasks: plan

Source plan: `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/plan.md`

## Wave 1

- [x] [coding] Task 1: 定义预首项停滞分类 | `codex2codex/meight.py`, `codex2codex/scripts/test_worker_recovery_contracts.py`, `.codex/work/20260620-codex2codex-context-firewall/artifacts/task1-worker-classification.md` | Verify: `python codex2codex/scripts/test_worker_recovery_contracts.py` Output: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task1-worker-classification.md`

## Wave 2

- [x] [coding] Task 2: 实现恢复决策与一次重试 | `codex2codex/scripts/run_wave.py`, `codex2codex/scripts/test_run_wave_recovery.py`, `.codex/work/20260620-codex2codex-context-firewall/artifacts/task2-run-wave-recovery.md` | Verify: ``python codex2codex/scripts/test_run_wave_recovery.py`; `python codex2codex/scripts/test_worker_recovery_contracts.py`` Output: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task2-run-wave-recovery.md`

## Wave 3

- [x] [coding] Task 3: 更新 codex2codex 恢复文档 | `codex2codex/SKILL.md`, `codex2codex/ARCHITECTURE.md`, `.codex/work/20260620-codex2codex-context-firewall/artifacts/task3-codex2codex-docs.md` | Verify: `rg "PRE_FIRST_ITEM_STALL|nonce smoke|MEIGHT_HOME" codex2codex/SKILL.md codex2codex/ARCHITECTURE.md` Output: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task3-codex2codex-docs.md`
- [x] [coding] Task 4: 更新 spec2plan 重型合成指南 | `spec2plan/references/heavy-mode.md`, `.codex/work/20260620-codex2codex-context-firewall/artifacts/task4-spec2plan-heavy-mode.md` | Verify: `rg "compact synthesis|SPEC2PLAN_ARTIFACT_V1|main-agent fallback|dry-run" spec2plan/references/heavy-mode.md` Output: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task4-spec2plan-heavy-mode.md`

## Wave 4

- [x] [coding] Task 5: 执行验证与结构预检 | `.codex/work/20260620-codex2codex-context-firewall/artifacts/task5-validation.md` | Verify: ``python codex2codex/scripts/test_worker_recovery_contracts.py`; `python codex2codex/scripts/test_run_wave_recovery.py`; `python spec2plan/scripts/validate_plan_contract.py .codex/work/20260620-codex2codex-context-firewall/plan.md --mode heavy`; `python codex2codex/scripts/run_plan.py .codex/work/20260620-codex2codex-context-firewall/plan.md --dry-run`` Output: `.codex/work/20260620-codex2codex-context-firewall/artifacts/task5-validation.md`

## Wave 5

- [x] [review] Task 6: 独立最终审查 | `.codex/work/20260620-codex2codex-context-firewall/review.md` | Verify: `Review artifact inspection only; no mutation required.` Output: `.codex/work/20260620-codex2codex-context-firewall/review.md`

## Wave 6: fix review findings
- [x] [coding] Obsolete: earlier review findings fixed by subsequent scoped changes; final review PASS recorded in `/data/lcq/.codex/skills/.codex/work/20260620-codex2codex-context-firewall/review.md`.
