---
name: edit-orchestration
description: Route every manual file edit through the lightest safe editing path, including apply_patch grammar/recovery. Use when Codex needs to create, modify, move, or delete files; choose between apply_patch, structural rewrite tools, agent-edit helpers, generated-output flows, or review-before-apply workflows; prepare user-level edit tools; recover patch misses; inspect diffs; and verify edits without silently downgrading failed routes.
---

# Edit Orchestration

Use this skill as the default entrypoint for manual file edits. It keeps small edits fast with `apply_patch`, includes patch grammar/recovery, and escalates complex edits to safer route-specific tools and gates.

## Core Rule

```text
Pick the lightest route that is safe. If a selected route needs a tool and self-check fails, stop. Do not silently downgrade.
```

## Workflow

1. **Preflight**
   - Restate the edit intent in one sentence.
   - Identify target files and expected behavior.
   - Check repo state when edits may collide with user work.
   - Read current source from disk before editing; summaries are navigation only.
   - If confidence drops, tests fail unexpectedly, or impact expands, load one dependency ring before continuing.

2. **Select route**
   - Read `references/route-matrix.md` for ambiguous or non-trivial edits.
   - Default to `fast path` only when the edit is small, single-area, and has unique context.
   - Use `structural rewrite path` for repeated syntax-aware changes.
   - Use `agent-edit path` for complex natural-language multi-file edits.
   - Use `review-before-apply path` when broad generated diffs need isolation before landing.
   - Use `generated-output path` when a project-owned generator, formatter, package manager, or lockfile tool owns the output.

3. **Prepare selected tools**
   - Read `references/tooling.md` before using a helper CLI.
   - Run `scripts/self_check_edit_tools.py --tool <tool>` before relying on an existing helper.
   - Run `scripts/prepare_edit_tools.py --tool <tool>` only when that selected route requires the helper.
   - Install only into user-controlled roots. Never use `sudo` or mutate system package manager state.

4. **Edit**
   - For `fast path`, use `apply_patch` with precise anchors; read `references/apply-patch.md` when exact grammar, add/delete/move syntax, or visual-match recovery matters.
   - For generated files, run the owning project tool, then inspect diff.
   - For structural or agent-edit routes, keep generated changes pending until diff review passes.
   - Preserve unrelated dirty work.

5. **Recover or stop**
   - Read `references/failure-recovery.md` after any patch miss, partial patch, route self-check failure, or unexpected verification result.
   - Retry a failed patch only after re-reading exact raw source.
   - Stop when the selected route cannot be made safe.

6. **Gate final response**
   - Inspect `git diff` or equivalent file diff against the stated intent.
   - Run focused verification for behavior changes.
   - Report changed files, commands run, outcomes, skipped checks, and known gaps.

## Route References

- `references/route-matrix.md`: route predicates and stop conditions.
- `references/apply-patch.md`: exact apply_patch grammar, patch forms, malformed patch avoidance, visual-match miss recovery.
- `references/tooling.md`: supported tools, install roots, manifests, and self-check policy.
- `references/failure-recovery.md`: patch miss, tool failure, diff drift, and verification recovery.
- `references/examples.md`: compact examples for route behavior; read when behavior is ambiguous or forward-testing the skill.

## Script Interfaces

```bash
python3 edit-orchestration/scripts/prepare_edit_tools.py --list
python3 edit-orchestration/scripts/prepare_edit_tools.py --tool ast-grep
python3 edit-orchestration/scripts/prepare_edit_tools.py --tool ast-grep --check-only
python3 edit-orchestration/scripts/self_check_edit_tools.py --tool ast-grep --json
```

Supported tool ids: `ast-grep`, `aider`, `jscodeshift`, `openrewrite`.

## Stop Conditions

- Target file changed unexpectedly and intent is no longer clear.
- Dirty worktree conflict touches the edit scope.
- Selected helper tool cannot be prepared or self-checked.
- Diff contains unrelated behavior, config, lockfile, or generated churn.
- Verification fails and the next safe diagnostic step is unclear.
- The edit would touch secrets, credentials, private keys, or hard-to-recover state.
