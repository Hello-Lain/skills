# Context Wave 1

- Goal: Build `structural-edit` as the default structure-first editing skill, migrate `edit-orchestration` to a compatibility shell, run production gates, and finish with reviewer acceptance.
- Context state: focused
- Mode: lite wave-pack
- Authoritative sources: `.codex/work/20260623-structural-edit/spec.md`; `edit-orchestration/SKILL.md`; `edit-orchestration/scripts/prepare_edit_tools.py`; `edit-orchestration/scripts/self_check_edit_tools.py`; `spec2plan/references/plan-contract.md`; `plan2do/references/execution-contract.md`; `skill-tokenless/references/skill-production-gate.md`
- Constraints: preserve unrelated dirty work; no silent downgrade when a structural route should apply; user-controlled install roots only; use `reviewer`; production report required
- Known blocker: `spec2plan` heavy subagent route via `codex2codex` is unavailable because `codex2codex/install.sh` pins `openai-codex==0.1.0b3`, which is not currently resolvable from PyPI, so planning/execution/review proceed in main thread with explicit blocker evidence
- Next action: save validated `plan.md`, then execute task 1 scaffolding
