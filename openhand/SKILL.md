---
name: openhand
description: Use when the user explicitly invokes $openhand or /openhand, or asks Codex to prepare an OpenHandsMCP-backed delegation workflow for complex plans, large-scale implementation, long-running refactors, or high-effort tasks. Provides explicit-first adaptive delegation, dry-run task classification, preflight checks, OpenHandsMCP setup guidance, safe task lifecycle rules, status polling guidance, cleanup, rollback, and secrets controls. Do not use for small edits or to silently auto-run Docker/OpenHands.
---

# OpenHand

Use this skill to decide, prepare, and supervise an opt-in OpenHandsMCP-backed workflow. It is explicit-first: prefer `$openhand` or `/openhand`, classify the task, ask before delegation, then use OpenHandsMCP only after preflight and approval.

This skill wraps `danshardware/OpenHandsMCP`; do not reimplement its session, git, Docker, or container backend.

## Operating Rules

- Start in dry-run mode. Never launch OpenHandsMCP, Docker, Podman, or live MCP tasks unless the user explicitly approves that step.
- Use OpenHandsMCP for proposal-only delegated work by default. Review diffs and tests before applying changes to the live workspace.
- Treat Docker/Podman socket access as high risk. Prefer disposable clones or worktrees and repo allowlists.
- Do not forward secrets by default. Require explicit per-key approval for `OPENHANDS_SECRET_*`.
- Do not claim built-in automatic runtime hooks or parity with Claude Code dynamic workflows. Phrase this as opt-in adaptive delegation.
- Call `cleanup_coding_tasks` before `teardown` when cleaning OpenHandsMCP sessions.

## Quick Flow

1. Classify the task:
   `openhand/scripts/classify-task.sh --task "<task text>"`
2. Run local preflight:
   `openhand/scripts/preflight.sh`
3. Verify a local OpenHandsMCP checkout, if available:
   `openhand/scripts/check-openhands-mcp-tools.sh --source ~/path/to/OpenHandsMCP`
4. If approved, configure/run OpenHandsMCP following `references/openhands-mcp-setup.md`.
5. Submit proposal-only tasks, poll `coding_task_status`, collect diffs, validate, then review before applying.
6. Clean up:
   `openhand/scripts/cleanup-openhands.sh --sessions-dir ./sessions --archive-dir ./archive`

## When To Delegate

Delegate only when several are true:

- The task spans many files or unclear architecture boundaries.
- The task benefits from isolated workspace exploration.
- Runtime/test cycles may be long.
- The output can be reviewed as a diff before applying.
- Docker/socket risk and repo scope are acceptable.

Do not delegate:

- Small single-file fixes.
- Secrets-heavy work without explicit approval.
- Production operations, destructive migrations, or irreversible changes.
- Work where a disposable workspace cannot be used.
- Tasks where backend cleanup cannot be verified.

## References

- Backend setup: `references/openhands-mcp-setup.md`
- Delegation policy: `references/delegation-policy.md`
- Secrets and security: `references/security-and-secrets.md`
- Task lifecycle: `references/task-lifecycle.md`
