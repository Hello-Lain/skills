# OpenHandsMCP Setup

Use `danshardware/OpenHandsMCP` as the backend. Do not copy or reimplement its session manager unless upstream is unavailable and the user explicitly approves a fork.

## Verified Upstream Snapshot

- Repository: `https://github.com/danshardware/OpenHandsMCP`
- Main commit observed during this implementation: `f65a7baf757b938e270e0304c2b873e2eaec4f5c`
- Commit date observed: `2025-06-30T14:36:28Z`
- Package: `openhands-mcp-server`
- Entrypoint: `openhands-mcp-server = openhands_mcp_server.server:main`
- Python: `>=3.8`
- Dependencies: `mcp`, `docker`, `gitpython`, `pydantic`

## Observed Tool Surface

At the snapshot above, `src/openhands_mcp_server/server.py` registers:

- `start_session(repo_url, branch="main")`
- `code(session_id, task_description)`
- `git(session_id, command)`
- `teardown(session_id, archive_changes=True)`
- `coding_task_status(session_id)`
- `cleanup_coding_tasks(session_id)`

README text may mention `list_sessions`, but this tool was not registered in the inspected `server.py`. Verify source before relying on it:

```bash
openhand/scripts/check-openhands-mcp-tools.sh --source ~/path/to/OpenHandsMCP
```

## Safe Setup Sequence

1. Clone or install OpenHandsMCP into a disposable tooling directory.
2. Pin the commit or version used for the run.
3. Run `openhand/scripts/preflight.sh --source ~/path/to/OpenHandsMCP`.
4. Verify tool surface with `check-openhands-mcp-tools.sh`.
5. Propose Codex MCP config to the user before writing it.
6. Start the MCP server only after explicit approval.

## Runtime Notes

OpenHandsMCP uses Docker or Podman sockets and mounts workspaces read-write. Treat this as high risk. Do not run backend tasks in the live repository; use disposable clones/worktrees.
