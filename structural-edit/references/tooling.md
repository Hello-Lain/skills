# Tooling

Use helper tools only after route selection.

## Install Roots

Default root:

```text
${CODEX_HOME:-~/.codex}/tools/structural-edit
```

Allowed roots:

- `$CODEX_HOME/tools/structural-edit`
- `~/.codex/tools/structural-edit`
- project `.codex/tools/structural-edit`
- another explicit user-controlled `--root`

Forbidden:

- `sudo`
- `/usr`, `/usr/local`, `/bin`, `/sbin`, `/etc`, `/var`, `/opt`
- system package-manager mutation

## Manifest

`scripts/prepare_structural_tools.py` records tool state in:

```text
<root>/manifest.json
```

Each record includes:

- tool id
- install method
- source package or download URL
- command path
- detected version
- updated timestamp
- last self-check status and reason

## Supported Tools

### `ast-grep`

- Purpose: Python and lightweight JS/TS structural rewrites.
- Install method: user-root npm package `@ast-grep/cli`.
- Commands:
  - `python3 structural-edit/scripts/prepare_structural_tools.py --tool ast-grep`
  - `python3 structural-edit/scripts/self_check_structural_tools.py --tool ast-grep --json`

### `jscodeshift`

- Purpose: JS/TS codemods and semantic migrations.
- Install method: user-root npm package `jscodeshift`.

### `remark`

- Purpose: Markdown AST-aware rewrites.
- Install method: user-root npm package `remark-cli`.

### `jq`

- Purpose: JSON field/value/path operations.
- Install method: download a user-root binary to `<root>/bin/jq`.
- Override: `STRUCTURAL_EDIT_JQ_URL`

### `yq`

- Purpose: YAML key/path/value operations.
- Install method: download a user-root binary to `<root>/bin/yq`.
- Override: `STRUCTURAL_EDIT_YQ_URL`

### `openrewrite`

- Purpose: Java migrations.
- Install method: no generic standalone installer in this skill; rely on project Maven/Gradle/OpenRewrite context.
- Self-check passes only when the current project has the required build files and executable tool path.

## Version Policy

- Use env overrides for pinned packages when reproducibility matters:
  - `STRUCTURAL_EDIT_AST_GREP_PACKAGE`
  - `STRUCTURAL_EDIT_JSCODESHIFT_PACKAGE`
  - `STRUCTURAL_EDIT_REMARK_PACKAGE`
  - `STRUCTURAL_EDIT_JQ_URL`
  - `STRUCTURAL_EDIT_YQ_URL`
- If no override is provided, install the default package or binary URL and record the detected version in `manifest.json`.
- Use `--force-user-root` when the manifest must point at `<root>` rather than an existing `PATH` command.
- Always re-run self-check after preparation.
