# Task Lifecycle

## Proposal-Only Default

1. Classify task with `scripts/classify-task.sh`.
2. Run `scripts/preflight.sh`.
3. Confirm OpenHandsMCP source/tool surface.
4. Ask user before backend use.
5. Create or select a disposable repo clone/worktree.
6. Call `start_session`.
7. Call `code` with a proposal-only prompt.
8. Poll `coding_task_status`.
9. Inspect generated diff and logs.
10. Run tests in the disposable workspace when practical.
11. Review before applying to live workspace.

## Cleanup

Always call:

1. `cleanup_coding_tasks(session_id)`
2. `teardown(session_id, archive_changes=true)`
3. Verify no OpenHands containers remain.
4. Verify no secret file remains in workspaces or archives.

Use `scripts/cleanup-openhands.sh` for dry-run reporting.

## Abort Conditions

- Tool surface differs from expected tools.
- Docker/Podman socket is unavailable or unacceptable.
- Secrets are required but not approved per key.
- Cleanup cannot be verified.
- Backend produces changes outside the approved scope.
