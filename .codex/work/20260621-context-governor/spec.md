# Spec: Decision-Grade Context Governor

## Objective

Rewrite `/data/lcq/.codex/skills/context-engineering/SKILL.md` for a local Codex power user so the skill governs context over long engineering, research, and idea-to-code sessions. The rewritten skill must keep normal work context small, prevent stale or speculative context from polluting decisions, and require source-of-truth rehydration before risky actions.

## Users

Primary user: a local Codex power user who runs long sessions, uses multiple skills, researches ideas, edits code, and expects the agent to manage context quality without waiting for manual compaction timing.

Secondary user: a future Codex agent or subagent that must consume the skill and make consistent context-loading, compaction, and decision-gating choices.

## Problem

The current `context-engineering/SKILL.md` teaches useful context setup patterns, but it treats compaction as a manual conversation-management suggestion. It does not define:

- how to detect when context is bloated, stale, or polluted;
- when to compact or ask the user to compact;
- how to handle environments where `/compact` cannot be invoked programmatically;
- how to prevent compressed summaries from being treated as authoritative evidence;
- how to rebuild clean context before high-risk decisions.

This matters because long sessions accumulate logs, abandoned ideas, failed branches, outdated assumptions, and duplicated tool output. If those remain active during deletion, migration, API, security, architecture, research, or release decisions, the agent can make plausible but wrong choices.

## Success Criteria

- `SKILL.md` defines a context state model with at least `fresh`, `focused`, `bloated`, `stale`, `compressed`, and `decision-critical`.
- `SKILL.md` defines automatic compaction triggers, including phase boundaries, task switches, large tool output, repeated failed loops, stale facts, and estimated token pressure.
- `SKILL.md` defines a best-effort compaction actuator policy: attempt local live compaction only when a verified actuator exists; otherwise emit `COMPACT_NOW` with reason and required pre-compaction capsule.
- `SKILL.md` defines `Context Capsule` content that preserves current goal, constraints, authoritative files, decisions, assumptions, risks, and next action before compaction.
- `SKILL.md` defines decision-critical triggers for destructive, irreversible, user-visible, high-cost, security-sensitive, API/schema/config, architecture, migration, release, and research-conclusion decisions.
- `SKILL.md` requires source-of-truth rehydration before decision-critical actions and explicitly states that compressed summaries are continuity hints, not authoritative evidence.
- `SKILL.md` defines a `Decision Packet` format covering decision, options, authoritative evidence, conflicts, assumptions, risk level, reversibility, rollback, verification, and user-confirmation need.
- `SKILL.md` includes anti-pollution rules for raw tool output, stale branches, speculative ideas, failed paths, external docs, generated files, and old summaries.
- The rewritten skill remains lightweight enough to execute from `SKILL.md` alone; no database, MCP server, hook, or exact token meter is required for v1.

## Scope

### In

- Rewrite the main content of `/data/lcq/.codex/skills/context-engineering/SKILL.md`.
- Preserve useful existing concepts: context hierarchy, focused source loading, trust levels, conflict surfacing, and verification.
- Add a governance loop: `Sense -> Compress/Quarantine -> Capsule -> Risk Gate -> Rehydrate -> Decision Packet -> Act`.
- Add concrete trigger lists for compaction and rehydration.
- Add exact templates for `Context Capsule`, `COMPACT_NOW`, and `Decision Packet`.
- Add fallback behavior for sessions where Codex `/compact` cannot be auto-called.
- Add verification checks for future agents reviewing the skill.

### Out

- No implementation of a new MCP server, database, memory service, or hook system in v1.
- No guarantee that the agent can directly invoke Codex `/compact` in every runtime.
- No exact token accounting requirement.
- No automatic restoration of all historical context after compaction.
- No automatic approval of high-risk actions when source evidence conflicts.
- No broad cleanup of unrelated skills, configs, or docs as part of this spec.

## Requirements

### Functional

- The skill must tell the agent to classify active context into explicit states before substantial work, after large outputs, after task shifts, and before risky actions.
- The skill must tell the agent to compact or request compaction when context is bloated, stale, phase-shifted, or dominated by redundant tool output.
- The skill must tell the agent to generate a `Context Capsule` before any compaction attempt or `COMPACT_NOW` request.
- The skill must not assume `/compact` is always callable. It must distinguish verified actuator, unavailable actuator, and manual user fallback.
- The skill must instruct the agent to quarantine low-authority context instead of letting it drive decisions.
- The skill must instruct the agent to rehydrate from authoritative sources before decision-critical work.
- The skill must require `Decision Packet` output before acting on high-risk or hard-to-reverse decisions.
- The skill must define when to ask the user instead of deciding, especially when evidence conflicts or rollback is unclear.
- The skill must support engineering, research, and idea-to-project workflows without needing separate variants.

### Non-Functional

- The rewritten `SKILL.md` should be concise and operational, not a long tutorial.
- The rules should be deterministic enough that another agent can apply them without asking for hidden intent.
- Templates should be copyable and short.
- The skill should favor authoritative local sources over conversation history.
- The skill should be compatible with Codex sessions where shell access exists but live app-server compaction does not.
- The skill should preserve safety: high-risk decisions require explicit evidence and, when appropriate, user confirmation.

## Constraints

- Target file: `/data/lcq/.codex/skills/context-engineering/SKILL.md`.
- V1 changes only the skill documentation and workflow instructions.
- Manual edits must preserve unrelated user changes in the repository.
- If later implementation edits occur, use `apply_patch` for manual file edits.
- The current environment does not expose a verified live Codex compaction socket, so automatic `/compact` must be documented as best-effort rather than guaranteed.
- The project already has a saved idea artifact at `.codex/work/20260621-context-governor/idea.md`; this spec derives from it.

## Assumptions To Validate

- [ ] The user wants `Decision Packet` to be mandatory for all high-risk actions, not only recommended. Validate by confirming during implementation review.
- [ ] The lightweight `SKILL.md`-only approach is sufficient for v1. Validate by using the rewritten skill in at least one long context-heavy task.
- [ ] The trigger lists cover the main failure modes. Validate by reviewing against engineering, research, and idea-refine examples.
- [ ] `COMPACT_NOW` fallback is acceptable when live compaction cannot be invoked. Validate by user review after the final skill text is drafted.

## Risks

- Over-process slows normal work - Mitigate by applying `Decision Packet` only to decision-critical actions and using short templates.
- Under-triggering misses dangerous decisions - Mitigate by defining broad risk categories and requiring rehydration when unsure.
- Summary pollution persists after compaction - Mitigate by saying summaries are continuity hints, not evidence.
- The skill becomes too long to follow - Mitigate by making the main workflow compact and moving rare detail to examples only if later needed.
- The agent overclaims `/compact` automation - Mitigate by requiring verified actuator checks and fallback text.
- Research workflows need different evidence than code workflows - Mitigate by defining authoritative sources generically: files, specs, papers, commands, logs, user-confirmed constraints, and current observations.

## Acceptance Checks

- `context-engineering/SKILL.md` contains the phrases or equivalent sections: `Context States`, `Compression Triggers`, `Context Capsule`, `COMPACT_NOW`, `Decision-Critical Triggers`, `Rehydration`, `Decision Packet`, and `Anti-Pollution`.
- A reader can answer: "When should the agent compact?", "What happens if `/compact` is unavailable?", and "What must happen before a risky decision?"
- The skill explicitly states compressed summaries are not authoritative evidence.
- The skill gives a concrete `Decision Packet` template.
- The skill gives a concrete `Context Capsule` template.
- The skill preserves source-trust handling for project files, configs, external docs, and generated content.
- The skill does not require implementing a new database, MCP server, hook, or token meter.
- A future implementation can be reviewed by diffing only `/data/lcq/.codex/skills/context-engineering/SKILL.md` unless the user explicitly expands scope.

## Open Questions

- Should the final skill include a short "Research Mode" subsection for papers/experiments, or keep all domains under one generic governance loop?
- Should the final skill include a direct reference to the local helper `/data/lcq/.codex/scripts/codex_compact_current.py`, or keep actuator details generic?
- Should `Decision Packet` always require user confirmation for destructive actions, or only when rollback is unclear?
