Salvaged-From-Worker: coding-2

# Task 4: spec2plan heavy-mode guide

## Changed files

- `spec2plan/references/heavy-mode.md`

## Implementation

- Added `Compact Synthesis` guidance.
- Required validated `SPEC2PLAN_ARTIFACT_V1` planner/reviewer inputs.
- Banned `main-agent fallback synthesis`.
- Clarified `dry-run` as structure precheck only.
- Added pre-first-item stall recovery guidance.

## Verification

```text
$ rtk proxy rg "compact synthesis|SPEC2PLAN_ARTIFACT_V1|main-agent fallback|dry-run" spec2plan/references/heavy-mode.md
...matches found...
```

```text
$ rtk git diff --check -- spec2plan/references/heavy-mode.md
```

Exit code: `0`.

## Judgment calls

- Docs-only scope → no tests added.
- Used explicit `main-agent fallback synthesis` phrasing to match plan terminology.

## Residual risks

- Cross-doc drift remains possible until sibling `codex2codex` doc updates are reviewed together.
