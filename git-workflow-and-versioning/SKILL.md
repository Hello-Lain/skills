---
name: git-workflow-and-versioning
description: >
  Structures git workflow practices. Use proactively, without waiting for the
  user to name it, when code changes touch a git repo and git hygiene matters:
  dirty-tree inspection, preserving unrelated changes, staging, committing,
  branching, worktrees, conflict resolution, PR preparation, tags, releases,
  version bumps, commit messages, or history organization. For multi-session
  or parallel agent routing/context isolation, hand off orchestration to
  $conductor.
---

# Git hygiene

MIT-derived workflow from addyosmani/agent-skills. Keep this entrypoint lean; preserve upstream detail in `references/upstream.md`.

## Use
Read `references/upstream.md` for branch/commit/release workflows.
Read `references/worktrees.md` before detecting, creating, using, or removing git worktrees.

Use `$conductor` first when the problem is multi-session routing, sidecars, Handoff Capsules, context isolation, dependency waves, or hard-gate coordination. This skill owns only real Git workflow/versioning hygiene.

## Core Rules
- Keep commits atomic, descriptive, reversible.
- Never rewrite shared history unless explicitly approved.
- Inspect dirty tree before staging; avoid unrelated changes.

## Validation
- Run relevant repo tests/lint/build or targeted runtime checks.
- If verification cannot run, state why and give the strongest evidence collected.
