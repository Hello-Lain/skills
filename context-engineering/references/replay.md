# Replay Notes

Use this file when auditing this skill's real execution impact or forward-testing context artifact behavior.

## Fixture: plan-contract-fail-fast

Observed artifacts:

- `.codex/work/20260621-plan-contract-fail-fast/artifacts/context-task1.md`
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/context-task2.md`
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/context-task3.md`
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/context-task4.md`
- `.codex/work/20260621-plan-contract-fail-fast/artifacts/context-task5.md`

Assessment:

- Positive: context packs preserved source hierarchy and kept plan execution auditable.
- Negative: five task-level packs were heavier than the task risk justified.
- Expected default: one `wave-pack` for the plan execution wave.
- Expected escalation: use `task-pack` only for a task with failure, ambiguity, confidence loss, cross-cutting scope, or decision-critical risk.

## Expected Gate Outcomes

| Scenario | Inputs | Expected action |
| --- | --- | --- |
| Routine reversible task | `phase=implement`, `task-risk=low`, no failure, no ambiguity | `internal` |
| Normal multi-task plan | `phase=implement`, `plan-tasks=5`, no failure, no ambiguity | `wave-pack` |
| Patch miss | `failure=patch`, `phase=implement` | `task-pack` |
| Destructive/security/API/schema | `decision-critical=security` or `api` or `schema` | `decision-packet` |
| High pressure phase boundary | `context-pressure=high`, `phase-boundary=true`, no capsule | `capsule` |
| After capsule under pressure | `context-pressure=high`, `phase-boundary=true`, `compact-ready=true` | `compact-request` |

## Audit Questions

- Did the agent rehydrate current source before edits?
- Did the agent create one wave pack instead of one task pack per routine task?
- Did failures trigger a task pack or full-mode expansion?
- Did decision-critical work get a Decision Packet?
- Were raw logs, diffs, and transcripts quarantined into artifacts?
- Did the final answer cite paths and verification outcomes instead of raw dumps?
