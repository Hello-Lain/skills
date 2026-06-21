# Git Worktrees

Load before detecting, creating, using, or removing git worktrees.

## Scope

This reference owns local git worktree hygiene only. Use `$conductor` for multi-session routing, sidecars, Handoff Capsules, dependency waves, and hard-gate coordination.

## Flow

1. Inspect state:
   ```bash
   git rev-parse --show-toplevel
   git rev-parse --git-dir
   git rev-parse --git-common-dir
   git rev-parse --show-superproject-working-tree
   git worktree list
   git status --short
   ```
2. Detect existing isolation:
   - If `git-dir` differs from `git-common-dir` and `show-superproject-working-tree` is empty, this is already a linked worktree; do not create another unless explicitly needed.
   - If `show-superproject-working-tree` is non-empty, treat it as a submodule, not a worktree.
3. Prefer native tooling:
   - If Paseo worktree tools are available, use `list_worktrees`, `create_worktree`, and `archive_worktree`.
   - Use raw `git worktree` only as fallback or for read-only inspection.
4. Choose location:
   - Prefer user-provided path.
   - Else prefer an existing project-local ignored worktree dir such as `.worktrees/` or `worktrees/`.
   - Else prefer a sibling dir outside the repo.
5. Guard ignored dirs before project-local worktrees:
   ```bash
   git check-ignore -q .worktrees/ || git check-ignore -q worktrees/
   ```
   If no project-local dir is ignored, either add the narrow ignore rule as part of the current change or create a sibling worktree outside the repo.
6. Create from the intended base:
   ```bash
   git fetch --all --prune
   git worktree add -b <branch> <path> <base>
   ```
   Skip fetch only when offline, expensive, or the task requires local-only state; report that assumption.
7. Establish baseline in the new worktree before edits:
   - Run the project setup/test commands already documented by the repo.
   - If baseline fails, record command/output summary and decide whether the task can proceed without hiding the pre-existing failure.
8. Work and verify:
   - Keep changes branch-local.
   - Commit only when requested or when the task explicitly includes git commits.
   - Run focused tests/lint/build or record blockers.
9. Cleanup:
   - If native tooling created the worktree, remove it with the native archive/remove tool.
   - If raw git created it, run `git worktree remove <path>` only for the path created for this task.
   - Never delete unknown worktree dirs manually.

## Red Flags

- Creating a worktree inside the repo without an ignore rule.
- Treating a submodule as an existing worktree.
- Nesting a worktree inside another linked worktree by accident.
- Switching branches in the main checkout when a worktree was requested for isolation.
- Running dependency installs or migrations without checking repo conventions first.
- Removing or pruning worktrees you did not create.
