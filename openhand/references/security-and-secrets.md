# Security And Secrets

OpenHandsMCP can inject environment variables prefixed with `OPENHANDS_SECRET_` into a generated `.openhands_secrets` file inside the cloned workspace.

## Rules

- Default: forward no secrets.
- Require explicit per-key approval before setting `OPENHANDS_SECRET_*`.
- Never paste secret values into prompts, logs, plan files, or references.
- Inspect diffs for `.openhands_secrets` before applying any delegated changes.
- Exclude `.openhands_secrets` from archives.
- If secret exposure is suspected, stop containers, remove secret files, inspect logs, and rotate affected secrets.

## Redaction

When reporting environment state, say only:

- `OPENHANDS_SECRET_* present`
- count of matching variables
- approved key names only if user explicitly included them

Never print values.

## Docker Socket Risk

A writable Docker/Podman socket can grant broad host control. Treat backend execution as high risk even inside a container. Prefer disposable worktrees and never mount more than required.
