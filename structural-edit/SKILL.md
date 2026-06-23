---
name: structural-edit
description: Structure-first manual file editing with generator-owned, AST/codemod, structured-data, and Markdown-aware routes plus strict text fallback and hard-stop tool checks. Use as the default edit entrypoint when Codex needs to create, modify, move, or rewrite files manually, especially for Python, JavaScript/TypeScript, JSON, YAML, Markdown, generated outputs, or Java/OpenRewrite migration decisions.
---

# Structural Edit

Use this as the default entrypoint for manual file edits.

## Core Rule

```text
Prefer the file owner's structural route first. Allow text fallback only for tiny, unique, low-risk edits. If the selected structural route should apply and its toolchain is missing or unhealthy, return BLOCK instead of silently downgrading.
```

## Workflow

1. Restate the edit intent, target files, and expected behavior.
2. Check whether a project-owned generator, formatter, lockfile tool, or scaffold owns the output.
3. Otherwise classify the route with `scripts/route_decision.py`.
4. Read `references/route-matrix.md` for route rules and `references/fallback-policy.md` for hard-stop boundaries.
5. Self-check the selected tool with `scripts/self_check_structural_tools.py --tool <tool>`.
6. If the selected route allows preparation, use `scripts/prepare_structural_tools.py --tool <tool>` in a user-controlled root, then re-run self-check.
7. Perform the edit through the selected structural route; use text fallback only when `references/fallback-policy.md` allows it.
8. Inspect diff, run focused verification, and report route choice, commands, and gaps.

## References

- `references/route-matrix.md` — required primary routes and fallback predicates.
- `references/tooling.md` — install roots, supported tools, manifest schema, version policy.
- `references/fallback-policy.md` — strict fallback rules and `BLOCK` response shape.
- `references/migration.md` — migration from `edit-orchestration` and rollback.
- `references/compatibility.md` — mixed-repo and missing-tool behavior.
- `references/validation-scenarios.md` — required scenario gates and commands.

## Scripts

```bash
python3 structural-edit/scripts/route_decision.py --path file.py --structured-op --json
python3 structural-edit/scripts/self_check_structural_tools.py --tool ast-grep --json --non-interactive
python3 structural-edit/scripts/prepare_structural_tools.py --tool jq
python3 structural-edit/scripts/prepare_structural_tools.py --tool jq --force-user-root
python3 structural-edit/scripts/manifest_report.py --summary
python3 structural-edit/scripts/validate_structural_routes.py
```

## Stop Conditions

- A generator-owned route should apply but the owning command or contract is unavailable.
- A selected structural tool fails self-check after preparation.
- The edit would require a broad or speculative text patch where a structural route should apply.
- Diff contains unrelated churn, lockfile drift without intent, or generated output outside scope.
- Verification fails and the next safe diagnostic step is unclear.
