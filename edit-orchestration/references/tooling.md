# Tooling

Use helper tools only after a route selects them. Do not install tools during skill load.

## Install Roots

Default root:

```text
${CODEX_HOME:-~/.codex}/tools/edit-orchestration
```

Allowed roots:

- `$CODEX_HOME/tools/edit-orchestration`
- `~/.codex/tools/edit-orchestration`
- project `.codex/tools/edit-orchestration`
- another explicit user-controlled path passed with `--root`

Forbidden:

- `sudo`
- `/usr`, `/usr/local`, `/bin`, `/sbin`, `/etc`, `/var`, `/opt`
- system package manager mutation

## Manifest

`scripts/prepare_edit_tools.py` records prepared tools in:

```text
<root>/manifest.json
```

Each record includes tool id, method, command path, package spec, detected version, and timestamp. If a package is installed without a pinned version, the detected version in this manifest is the audit record.

## Supported Tool IDs

### `ast-grep`

Purpose: structural rewrite path for multi-language AST search and rewrite.

Preparation:

```bash
python3 edit-orchestration/scripts/prepare_edit_tools.py --tool ast-grep
```

Self-check:

```bash
python3 edit-orchestration/scripts/self_check_edit_tools.py --tool ast-grep
```

Implementation note: installs `@ast-grep/cli` with `npm --prefix <root>/node install ...` when a usable `ast-grep` binary is not already found.

### `jscodeshift`

Purpose: JavaScript and TypeScript codemod route.

Preparation:

```bash
python3 edit-orchestration/scripts/prepare_edit_tools.py --tool jscodeshift
```

Implementation note: installs `jscodeshift` with `npm --prefix <root>/node install ...`.

### `aider`

Purpose: agent-edit path for complex multi-file edits where Aider-style edit blocks, repo-map behavior, and lint/test loops are useful.

Preparation:

```bash
python3 edit-orchestration/scripts/prepare_edit_tools.py --tool aider
```

Implementation note: creates a venv under `<root>/venvs/aider` and installs `aider-chat` there.

### `openrewrite`

Purpose: JVM migrations and framework recipes.

Preparation:

```bash
python3 edit-orchestration/scripts/prepare_edit_tools.py --tool openrewrite
```

Implementation note: OpenRewrite's official open-source workflow is project Maven or Gradle plugin based. This skill does not fake a standalone generic CLI. Self-check passes only when the current project has Maven or Gradle build files and an executable build tool path.

## Version Policy

- Prefer pinned package specs through environment variables when reproducibility matters:
  - `EDIT_ORCH_AST_GREP_PACKAGE`
  - `EDIT_ORCH_JSCODESHIFT_PACKAGE`
  - `EDIT_ORCH_AIDER_PACKAGE`
- If no pinned spec is provided, install the package default and record detected version in `manifest.json`.
- Route self-check is mandatory after install.

## ADR: Route Orchestration Instead of Full Agent Replacement

This skill coordinates editing routes rather than replacing Codex with a separate coding agent. The goal is to keep small edits cheap and auditable while making complex edits safer through mature tools, pending diff review, and selected-route self-checks. A full external agent would add state, dependencies, and trigger ambiguity for every edit; lazy route-specific tooling keeps the default path small and makes failure explicit.
