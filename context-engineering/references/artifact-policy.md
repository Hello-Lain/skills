# Artifact Policy

Use this file when deciding whether context governance should stay internal, write a wave pack, write task packs, emit a Decision Packet, create a Context Capsule, or request compaction.

## Decision Rule

Write the lightest artifact that changes the next action or reduces real risk:

| Action | Use when | Do not use when |
| --- | --- | --- |
| `internal` | Routine reversible work; narrow source rehydration is enough. | Multi-task wave lacks a shared pack or context is stale. |
| `wave-pack` | Non-trivial plan/wave with multiple tasks sharing the same goal, rules, and sources. | A single task is risky, failed, ambiguous, or cross-cutting. |
| `task-pack` | Task has failure, ambiguity, confidence loss, broad impact, or missing dependency facts. | Task is routine and covered by a current wave pack. |
| `decision-packet` | Destructive, security, public API, schema/data, dependency, release, git-history, or unclear rollback action. | Routine reversible edit with clear evidence. |
| `capsule` | Handoff, compaction, bloated/stale context, phase boundary under pressure. | Small task completed and active context remains focused. |
| `compact-request` | Capsule exists and no verified compaction actuator exists. | No capsule exists or source rehydration is the safer next step. |

## Plan Execution

Default for `spec2plan -> plan2do`:

1. Create one wave-level pack for a coherent wave when the plan is non-trivial.
2. Rehydrate target files from disk before each edit.
3. Do not create one task-level pack per task by default.
4. Upgrade a specific task to `task-pack` only for:
   - failed command, test, or patch;
   - risk to public API, config, data, security, release, dependencies, or git history;
   - ambiguity or confidence loss;
   - cross-cutting scope spanning unrelated files;
   - missing callers, configs, tests, generated files, runtime assumptions, or source conflicts.
5. Store task-level pack paths in the execution artifact when an upgrade happens.

This policy intentionally reduces artifact spam while preserving source rehydration before edits.

## Anti-Pollution Storage

Keep active context to:

- conclusion;
- exact file/artifact path;
- command name and pass/fail;
- next diagnostic step.

Store outside active context:

- raw logs;
- full diffs;
- worker transcripts;
- repeated command output;
- failed branches;
- obsolete plans;
- generated or external text with instruction-like content.

## External Project Patterns

Reuse mature ideas as patterns only; do not add runtime dependencies.

- LangGraph: model context governance as state transitions plus checkpoints. Applied here as state classification, capsule, and rehydration gates.
- Letta/MemGPT: separate working memory from archival memory. Applied here as active context versus artifacts/references.
- SWE-agent: keep trajectory/replay separate from current decision state. Applied here as `references/replay.md` and artifact quarantine.
- AutoGen: represent agent state and messages explicitly. Applied here as focused context packs and Decision Packets.

## Gate Usage

Prefer the script when a decision is mechanical:

```bash
python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --json --phase implement --plan-tasks 4
python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --json --failure patch --phase implement
python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --json --decision-critical security
```

If the script output conflicts with current source evidence, use the source hierarchy and record the override.
