# Decision-Grade Context Governor

## Problem Statement

How might we turn `context-engineering` from a context-writing guide into an automatic context governor that keeps normal work lean, but rebuilds authoritative context before risky decisions?

## Target / Success

Target: a local Codex power user doing engineering implementation, research exploration, and idea-to-code work over long sessions.

Success:
- The user does not need to judge compaction timing manually.
- Normal execution carries less redundant context and fewer stale branches.
- Risky decisions rehydrate source-of-truth evidence instead of trusting old summaries.
- Live compaction is attempted only when a verified actuator is available; otherwise the skill emits a clear `COMPACT_NOW` fallback.
- The v1 rule set stays light enough to live directly in `SKILL.md`.

## Sharpening Questions

- Should risk actions include deletion, migration, API/config/security/architecture changes, research conclusions, costly experiments, and release steps by default?
- Must `Decision Packet` be shown before every high-risk action?
- Should the skill always generate a `Context Capsule` before compaction?
- Is `best-effort auto compact + fallback COMPACT_NOW` acceptable?
- Should v1 only update `SKILL.md`, or also wire local hooks/helpers?

## Variations

1. `Compression Thermostat`: decide when to compact from token pressure, phase boundaries, large tool output, repeated failures, and task switches.
2. `Decision Context Gate`: before risk actions, rebuild evidence and require a decision packet.
3. `Context State Machine`: track `fresh`, `focused`, `bloated`, `stale`, `compressed`, and `decision-critical`.
4. `Evidence Ledger`: every critical fact has source, timestamp/currentness, and verification method.
5. `Context Quarantine`: stale assumptions, failed paths, speculative plans, and raw logs are isolated by default.
6. `Best-effort Compact Actuator`: call the local live compact helper only when thread id and control socket are verified.
7. `Rehydrate Before Risk`: reread authoritative files, specs, diffs, tests, and user constraints before major decisions.
8. `Phase Boundary Capsules`: create compact state capsules when moving from exploration to design, design to implementation, implementation to verification, and verification to handoff.

## Clusters

### A. Auto-Compression Layer

Focus: decide when to compact automatically.

Stress test:
- User value: high because it removes the user's burden to judge timing.
- Feasibility: high because trigger rules can be encoded in the skill.
- Differentiation: medium because auto compaction exists elsewhere.
- Kill risk: compression alone can preserve polluted summaries.

Hidden assumptions:
- Token pressure or context bloat can be observed or estimated.
- Summary quality is good enough for continuity.
- The user accepts agent-initiated compaction requests.

### B. Decision-Grade Context Gate

Focus: rebuild authoritative context before risky decisions.

Stress test:
- User value: highest because it reduces wrong deletions, migrations, architecture choices, and research conclusions.
- Feasibility: medium-high because risk triggers must be explicit.
- Differentiation: strong because most systems compact but do not rehydrate decision-grade evidence.
- Kill risk: too many gates slow work; too few miss dangerous decisions.

Hidden assumptions:
- The skill can recognize most high-risk actions.
- Authoritative context can be reread quickly.
- The user accepts `Decision Packet` friction at critical points.

### C. Full Context Governor

Focus: combine state machine, compression gate, decision gate, quarantine, and evidence rules.

Stress test:
- User value: strongest long term across engineering, research, and idea-to-code workflows.
- Feasibility: medium because over-process is the main risk.
- Differentiation: strongest because it combines compaction, provenance, quarantine, and decision rehydration.
- Kill risk: the skill becomes too complex to execute consistently.

Hidden assumptions:
- A concise `SKILL.md` can reliably shape agent behavior.
- v1 can avoid building a database or MCP service.
- The same governance loop works across code, research, and ideation.

## Recommended Direction

Build the lightweight version of cluster C: **Decision-Grade Context Governor**.

The central problem is not just long context. The dangerous failure mode is stale summaries, failed branches, raw logs, speculative ideas, and outdated assumptions being treated as facts during important decisions. Compaction is only one actuator; the system must govern what enters the active context and what counts as evidence.

Recommended loop:

```text
Sense -> Compress/Quarantine -> Capsule -> Risk Gate -> Rehydrate -> Decision Packet -> Act
```

Core rules:

```text
Compressed summaries are continuity hints, not evidence.
Decision-critical actions require source-of-truth rehydration.
Raw tool output, stale branches, and speculative reasoning must not enter decisions by default.
```

## MVP Scope

V1 should update only `/data/lcq/.codex/skills/context-engineering/SKILL.md`.

Include:
- `Context States`
- `Compression Triggers`
- `Compaction Actuator Policy`
- `Context Capsule`
- `Decision-Critical Triggers`
- `Rehydration Rules`
- `Decision Packet`
- `Quarantine Rules`
- `Verification Checklist`

Minimal state model:

```text
fresh: task just started
focused: enough relevant context, low noise
bloated: repeated logs/files/history accumulating
stale: task changed or facts may be outdated
compressed: continuity summary exists, details may be lost
decision-critical: risky action pending; rebuild from sources
```

Compact policy:

```text
If actuator verified: attempt local compact helper.
If unavailable: emit COMPACT_NOW with reason.
Before either path: generate Context Capsule.
After compact: rehydrate only current authoritative context.
```

Decision packet:

```markdown
DECISION PACKET
- Decision:
- Options:
- Authoritative evidence:
- Conflicts / uncertainty:
- Assumptions:
- Risk level:
- Reversibility / rollback:
- Verification:
- User confirmation needed: yes/no
```

## Not Doing

- No full memory database in v1.
- No exact token dashboard in v1.
- No restoration of all historical context after compaction.
- No treating compressed summaries as facts.
- No agent-only approval for high-risk conflicting decisions.
- No dumping raw tool output into active context by default.
- No MCP or hook dependency for the first implementation.

## Open Questions

- Should `Decision Packet` be mandatory before all high-risk actions?
- Should v1 implement local compact helper integration, or only document the actuator policy?
- Should future versions persist evidence ledgers under `.codex/work/`?
