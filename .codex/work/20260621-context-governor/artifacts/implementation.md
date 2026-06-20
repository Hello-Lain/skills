# Implementation Notes

## Summary

Rewrote `context-engineering/SKILL.md` from a tutorial-style context setup guide into a Decision-Grade Context Governor.

## Changed

- Updated frontmatter description to trigger on bloated/stale/polluted context, risky decisions, compaction timing, and context packs.
- Added core governance rule: compressed summaries are continuity hints, not evidence.
- Added `Context States`: `fresh`, `focused`, `bloated`, `stale`, `compressed`, `decision-critical`.
- Added governance loop: `Sense -> Select -> Quarantine -> Capsule -> Compact -> Rehydrate -> Decide -> Act -> Verify`.
- Added `Compression Triggers`.
- Added `Context Capsule` template.
- Added `Compaction Actuator Policy` and `COMPACT_NOW` fallback.
- Added `Decision-Critical Triggers`.
- Added `Rehydration` rules.
- Added `Decision Packet` template.
- Added `Anti-Pollution Rules`.
- Preserved source hierarchy, trust levels, focused context pack, conflict handling, and verification behavior in a more operational form.

## Files Touched

- `context-engineering/SKILL.md`

## Notes

- No database, MCP server, hook, or live compaction helper implementation was added.
- `/compact` automation is documented as best-effort only.
