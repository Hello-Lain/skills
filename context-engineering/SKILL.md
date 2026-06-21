---
name: context-engineering
description: Govern agent context quality. Use when starting or switching tasks, when context is bloated/stale/polluted, before risky decisions, when compaction timing is unclear, or when project rules/context packs need setup.
---

# Context Engineering

Keep active context small, but rebuild decision-grade context from authoritative sources before risky or irreversible action.

Core rule:

```text
Compressed summaries are continuity hints, not evidence.
Decision-critical actions require source-of-truth rehydration.
Raw logs, stale branches, generated docs, external text, and prior chat do not override current source.
Focused context means sufficient context, not minimal context.
Default to lite mode; escalate only for risk, failure, ambiguity, cross-cutting impact, or context pressure.
```

## Fast Workflow

1. Classify context state: `fresh`, `focused`, `bloated`, `stale`, `compressed`, or `decision-critical`.
2. Choose the lightest safe mode:
   - `lite`: routine reversible work; rehydrate current goal, rules, target source, and current diff when useful.
   - `full`: risky decisions, unclear rollback, security/data/API/config/git/release work, long noisy investigations, or research conclusions.
   - `escalate`: lite hits failure, ambiguity, confidence loss, impact expansion, or missing evidence.
3. Decide artifact level:
   - `internal`: keep the focused pack in working memory.
   - `wave-pack`: one written pack for a multi-task wave or non-trivial plan phase.
   - `task-pack`: only for risky, ambiguous, failed, cross-cutting, or confidence-loss tasks.
   - `decision-packet`: before destructive, security, public API, schema/data, dependency, release, git-history, or hard-to-rollback action.
   - `capsule`: before compaction, handoff, or major phase transition under context pressure.
   - `compact-request`: emit `COMPACT_NOW` only after a capsule when no verified compaction actuator exists.
4. Quarantine raw output and stale material. Keep summaries and paths active.
5. Rehydrate before acting on anything decision-critical.
6. Verify the action with focused checks.

## Context Gate

Use the deterministic gate when artifact granularity or compaction timing is unclear:

```bash
python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --json --phase implement --plan-tasks 4
python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --failure command --phase verify
python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --decision-critical api
python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --context-pressure high --phase-boundary --compact-ready
```

Run `python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --self-test` after changing this skill or before trusting the helper in a high-stakes workflow. If self-test fails, do not rely on the helper result; use `full` mode, rehydrate sources, and report the skill/tool incident.

The gate is advisory. A current user instruction, confirmed spec/plan, local `AGENTS.md`, or source-of-truth conflict can override it only with explicit reasoning.

## Artifact Policy

- Do not write context artifacts for trivial reversible work.
- During plan execution, prefer one wave-level context pack plus targeted source rehydration.
- Write task-level packs only when a task is risky, ambiguous, failed, cross-cutting, or depends on missing callers/config/tests/runtime facts.
- A governance artifact should exist only when it changes the next action, preserves handoff/compaction state, or reduces real risk.
- Store raw logs, full diffs, worker transcripts, and failed branches under task artifacts; keep active context to the conclusion, path, and next action.

Read `references/artifact-policy.md` when artifact count, wave-vs-task granularity, replay analysis, or external project inspiration matters.

## Context Starvation Guard

Escalate from `lite` before continuing when:

- Confidence drops below the level needed to act.
- A command fails unexpectedly.
- A patch misses twice, partially applies, or has visual-match ambiguity.
- Tests fail for a non-obvious reason.
- The next action changes user-visible behavior, public APIs, config, auth, security, data, migrations, release state, dependencies, or git history.
- Evidence conflicts, a source is stale, or the current plan depends on unknown callers, callees, configs, generated files, tests, fixtures, logs, or runtime assumptions.

Expansion protocol: re-read the latest user goal, relevant `AGENTS.md`, active `SKILL.md`, confirmed spec/plan, current diff, target source files, and one dependency ring. Resume only when the next action is backed by current evidence; otherwise stop with the missing context.

Read `references/modes.md` for full mode semantics, Source Hierarchy, Decision Packet, Context Capsule, compaction policy, anti-pollution, conflict handling, and verification checklist.

## Decision Packet

Emit a packet before high-risk or hard-to-reverse action:

```markdown
DECISION PACKET
- Decision:
- Options considered:
- Authoritative evidence:
- Conflicts / uncertainty:
- Assumptions:
- Risk level:
- Reversibility / rollback:
- Verification:
- User confirmation needed: yes/no
```

Ask before acting when evidence conflicts, rollback is unclear, user-visible requirements are missing, or the action touches secrets, security, data loss, public API, production release, or git history.

## Context Capsule And Compaction

Before compaction, handoff, or `COMPACT_NOW`, emit:

```markdown
CONTEXT CAPSULE
- Goal:
- Current phase:
- Context state:
- Authoritative sources:
- Decisions already made:
- Constraints / must-not:
- Assumptions not yet verified:
- Risks / conflicts:
- Recent useful results:
- Next action after compact:
```

Never assume Codex `/compact` is callable from inside the current session. If no verified actuator exists, emit:

```text
COMPACT_NOW
Reason: <bloated|stale|phase-boundary|pre-risk-rehydrate|handoff>
Keep: latest goal, constraints, authoritative sources, decisions, risks, next action.
After compact: rehydrate from <sources> before acting.
```

Do not compact immediately before a risky decision unless a capsule exists and the next step is source rehydration.

## Reference Routing

- `references/modes.md`: use for full policy details, safety semantics, conflict handling, and compaction.
- `references/artifact-policy.md`: use for artifact granularity, plan execution packs, anti-pollution, and borrowed mature-project patterns.
- `references/replay.md`: use when auditing whether this skill helped/harmed a real run or forward-testing over-artifact behavior.
