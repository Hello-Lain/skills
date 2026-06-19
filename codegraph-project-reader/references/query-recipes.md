# CodeGraph Query Recipes

Use these recipes after `SKILL.md` triggers. Prefer MCP equivalents when exposed; use CLI when MCP is unavailable.

## Prep

```bash
repo="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
/data/lcq/.codex/skills/codegraph-project-reader/scripts/ensure-codegraph-index.sh "$repo"
```

## Repo Map

```bash
codegraph status "$repo"
codegraph files -p "$repo" --max-depth 3
codegraph explore -p "$repo" "area or behavior" --max-files 5
```

Use for unfamiliar repos, feature entry, architecture questions, and "where is X implemented?".

## Symbol Focus

```bash
codegraph query -p "$repo" "symbol or phrase"
codegraph node -p "$repo" "SymbolName"
codegraph node -p "$repo" -f src/path/file.ext --symbols-only
codegraph node -p "$repo" -f src/path/file.ext --offset 120 --limit 80
```

Use before reading full files. Prefer `node` when you need source plus caller/callee trail.

## Call Graph

```bash
codegraph callers -p "$repo" "SymbolName"
codegraph callees -p "$repo" "SymbolName"
codegraph impact -p "$repo" "SymbolName" --depth 2
```

Use before edits, bug fixes, refactors, public API changes, and review findings.

## Tests Affected By Changes

```bash
git diff --name-only | codegraph affected -p "$repo" --stdin --quiet
codegraph affected -p "$repo" src/foo.ts src/bar.ts --json
```

Use to pick targeted tests. If output is empty, still run existing relevant tests found by repo conventions.

## Search Strategy

- Start with `explore` for behavior-level questions.
- Use `query` for symbol discovery.
- Use `node` for exact source context.
- Use `impact` before changing exported/shared symbols.
- Use `affected` after choosing or changing files.
- Use `rg` for exact strings, config keys, docs, generated files, or when CodeGraph misses unsupported syntax.

## Output Discipline

- Keep `--max-files` between 3 and 8.
- Use file `--offset` and `--limit` rather than full-file reads.
- Summarize graph output as `symbol -> file -> callers/callees -> risk`.
