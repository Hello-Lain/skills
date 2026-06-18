---
name: conductor
description: "Use proactively, without waiting for the user to name it, when work becomes long, noisy, multi-turn, parallel, risky, dependency-heavy, or multi-branch and needs an Autopilot context firewall, clean master session, routing, sidecars/branches, merge notes, Handoff Capsules, or hard-gate user decisions only. Route plan.md work to $plan-grill, explicit worker delegation to $codex2codex, and real Git branch/commit/PR/release/history work to $git-workflow-and-versioning."
---

# Conductor

Keep one master session clean. Act only as router, context firewall, and gatekeeper; do not replace planners, executors, worker runtimes, token optimizers, or domain skills.

## Core Loop

1. Route silently: `master`, `dispatch`, `branch`, `explainer`, or `merge`.
2. Open sidecars/branches only when work is noisy, long, parallelizable, risky, or dependency-heavy.
3. Pass only approved summaries, explicit files, branch briefs, and branch-local messages.
4. Merge back only a `Suggested Merge Note` by default; keep the full `Handoff Capsule` in the completion report for continuation or audit.
5. Ask the user only at hard gates.

## Modes

- `Ambient`: small/immediate work stays in master. No branch card, map, report, or session title.
- `Autopilot`: default. Create branch cards, briefs, maps, sidecars, completion reports, and Handoff Capsules automatically.
- `Strict`: high-risk/audit. Ask before branch/session open, completion, and merge.

## Local Routing

- `$plan-grill`: production `plan.md`, safer plan artifact, or plan hardening.
- `$codex2codex`: explicit meight worker delegation, worker review, or Decision Council.
- `$git-workflow-and-versioning`: real Git branches, worktrees, commits, PRs, tags, releases, conflict/history hygiene.
- `$skill-tokenless`: skill shrinking/refactor/validation.
- `$caveman`: terse style, commit messages, compact delegation formats.

## Hard Gates

Stop for user input on global goal, architecture, scope, acceptance criteria, naming, irreversible action, destructive git, data loss, production/external side effects, branch conflicts requiring tradeoffs, proposed direction changes affecting delivery, raw history audit/debug requests, or explicit Strict/manual control.

## Context Firewall

- Master owns only goals, constraints, confirmed decisions, risks, next steps, and approved short summaries.
- Branch decisions stay local until master confirms them.
- Never read or merge raw branch/worker/explainer history unless a hard gate requires audit/debug.
- Refresh stale briefs after master goals or constraints change.
- Never put branch briefs, completion reports, or raw conversation summaries into Trellis `implement.jsonl` or `check.jsonl` unless a hard gate confirms they are execution/check context.

## Artifacts

Read `references/operating-model.md` when opening branches, dispatching waves, managing lifecycle states, or mapping Trellis/session state.

- Branch brief: `references/branch-brief-template.md`
- Completion report: `references/completion-report-template.md`
- Branch map: `references/branch-map-template.md`
- No Trellis: maintain `conductor.yaml` + `branch-map.md`

## Handoff Contract

Every branch completion report must include `## Handoff Capsule` before `## Suggested Merge Note`:

- Goal:
- Current state:
- Authoritative artifacts:
- Decisions:
- Verification:
- Remaining risks:
- Next action:
- Suggested skills:
- Redactions / omitted raw data:
