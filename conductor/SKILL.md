---
name: conductor
description: "Use proactively for long, noisy, multi-turn, or multi-branch work that needs an Autopilot context firewall: clean master session, dependency-aware routing, sidecars/branches, short merge notes, and hard-gate user decisions only. Route plan.md work to $plan-grill and explicit worker delegation to $codex2codex."
---

# Conductor

Keep one master session clean. Act as router + context firewall + gatekeeper; do not become planner, executor, worker runtime, token optimizer, or Trellis replacement.

## Modes

- `Ambient`: small/immediate work stays in master. No branch card, map, report, or session title.
- `Autopilot` default: create sidecars/branches/maps/reports when useful; ask the user only at hard gates.
- `Strict`: high-risk or audit mode. Ask before branch/session open, completion, and merge.

## Routing

- First silently route: `master`, `dispatch`, `branch`, `explainer`, or `merge`.
- `master`: global goals, scope, constraints, priorities, confirmed decisions, risks, next steps.
- `dispatch`: branch/wave planning only when planning takes >2-3 turns, >3 candidate branches, or dependency order is unclear.
- `branch`: one bounded exploratory, implementation-heavy, review-heavy, research-heavy, or noisy task.
- `explainer`: long tutorial/background/conceptual question. Default no merge.
- `merge`: completion-report short note back to master, unless a hard gate blocks.
- Route means choose the owner and gates. Do not execute specialized workflows here.

## Local Routing

- `$plan-grill`: production `plan.md` or safer plan artifact.
- `$codex2codex`: explicit meight worker delegation; keep its verification and sandbox rules.
- `$skill-tokenless`: skill shrinking/refactor/validation.
- `$caveman`: terse style, commit messages, and compact delegation formats.
- `conductor`: governance only. Do not replace planners, executors, worker tools, token optimizers, or domain skills.
- OpenHands skill is not installed. Use an explicit external workflow if needed.

## Gates

Soft gates run automatically in Autopilot:

- branch cards, branch briefs, branch maps, sidecars, completion reports
- short merge notes from completion reports
- stale marks on affected planned/active branches
- status moves in `branch-map.md` / `conductor.yaml`

Hard gates require user input:

- global goal, architecture, scope, acceptance criteria, or naming changes
- irreversible action, destructive git, data loss, production/external side effect
- branch conflict that needs a tradeoff
- worker/branch proposes a direction change that affects delivery
- raw branch/worker/explainer history is needed for audit/debug
- user explicitly requested Strict/manual control

## Context Firewall

- Master owns overview and confirmed decisions only.
- Keep master content to goals, constraints, confirmed decisions, risks, next steps, and approved short summaries.
- Branches receive only branch brief, approved summaries, explicit files, and branch-local messages.
- Branch decisions are local until master confirms them.
- Default master merge payload is only `Suggested Merge Note` from `completion-report.md` (150 words max).
- Do not read or merge raw branch, worker, or explainer history unless a hard gate asks for audit/debug.
- A stale branch must refresh its brief; do not continue from fuzzy master memory.
- This prevents new pollution. It cannot erase context already loaded into a dirty single dialogue.

## Safety

- Never run or suggest destructive git for dirty worktrees without explicit user request.
- Preserve unrelated user changes.
- Never put mutable status in titles; use branch map / Today View.
- Run dependency pass before opening branches; parallel means safe from the same snapshot.
- Prefer at most 2 active interactive branches. Dispatch and explainer do not count.

## Session Types

| Type | Title Pattern | Use |
| --- | --- | --- |
| `master` | `[CD-MAIN][master] <project>` | Source of truth |
| `dispatch` | `[CD-DISPATCH][routing] Branch planning` | Branch/wave/session planning only |
| `branch` | `[CD-001][W1][role] <purpose>` | One bounded interactive task |
| `explainer` | `[CD-E01][sidecar][explainer] Dirty questions` | Long explanations; no merge by default |

Use one dispatch session and one explainer per project.

## Branch Card

Before opening a branch, create: ID, stable title, type/role, purpose, why it exists, wave/deps, allowed context, artifact, completion criteria, return condition, open/planned/blocked state.

In Autopilot, do not ask before opening unless a hard gate is present. In Strict, ask before binding the real session.

Opening prompt must include: purpose, not-for, input snapshot, output artifact, return-to-master condition, and hard-gate return rule.

## Waves

Classify proposed branches:

- `ready_parallel`: can start from current snapshot.
- `dependent`: waits for branch output, decision, artifact, or user confirmation.
- `gate`: review, merge, or master decision unlocks next wave.
- `optional`: useful but not critical path.
- `explainer`: sidecar unless user makes it blocking.

Open only current-wave branches by default. Later branches stay `planned` or `blocked`.

## Lifecycle

Use stable states: `planned`, `brief_ready`, `active`, `blocked`, `hard_gate_pending`, `report_ready`, `merge_pending`, `merged`, `rejected`, `archived`.

If a branch implies a global decision, record it as proposed in the completion report and stop at a hard gate. It is not binding until master confirms it.

If master goals/constraints change, automatically mark affected planned/active branches stale and refresh briefs unless the refresh changes direction or scope.

## Artifacts

- Branch brief: use `references/branch-brief-template.md`.
- Completion report: use `references/completion-report-template.md`.
- Branch map: use `references/branch-map-template.md`.
- No Trellis: maintain `conductor.yaml` + `branch-map.md`.
- Trellis available: map master to parent/root, branch to child task, dispatch/explainer to sidecars; keep `task.json.meta.conductor` minimal.

Do not put branch briefs, completion reports, or raw conversation summaries into Trellis `implement.jsonl` or `check.jsonl` unless a hard gate confirms they are execution/check context.
