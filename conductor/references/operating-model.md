# Conductor Operating Model

Load this when branch/session routing, dependency waves, lifecycle states, or Trellis mapping matters. Keep master context limited to confirmed decisions, risks, next steps, and approved short summaries.

## Routing

- `master`: global goals, scope, constraints, priorities, confirmed decisions, risks, next steps.
- `dispatch`: branch/wave planning only when planning takes more than 2-3 turns, more than 3 candidate branches exist, or dependency order is unclear.
- `branch`: one bounded exploratory, implementation-heavy, review-heavy, research-heavy, or noisy task.
- `explainer`: long tutorial/background/conceptual question. Default no merge.
- `merge`: completion-report short note back to master, unless a hard gate blocks.
- Route means choose owner and gates, not execute specialized workflows.

## Soft Gates

Run automatically in Autopilot:

- branch cards, branch briefs, branch maps, sidecars, completion reports
- short merge notes from completion reports
- stale marks on affected planned/active branches
- status moves in `branch-map.md` / `conductor.yaml`

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

Create before opening a branch: ID, stable title, type/role, purpose, why it exists, wave/deps, allowed context, artifact, completion criteria, return condition, open/planned/blocked state.

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

If master goals/constraints change, mark affected planned/active branches stale and refresh briefs unless the refresh changes direction or scope.

## Trellis Mapping

- No Trellis: maintain `conductor.yaml` + `branch-map.md`.
- Trellis available: map master to parent/root, branch to child task, dispatch/explainer to sidecars; keep `task.json.meta.conductor` minimal.
- Do not put branch briefs, completion reports, Handoff Capsules, or raw conversation summaries into Trellis `implement.jsonl` or `check.jsonl` unless a hard gate confirms they are execution/check context.
