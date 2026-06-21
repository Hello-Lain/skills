# Route Matrix

Use this table after preflight. Pick one primary route, then apply its gates.

## Fast Path

Use when:

- Edit is small, local, and uniquely anchored.
- One file or one coherent file area is affected.
- No syntax-wide migration, generated output, or broad search is needed.
- Existing `apply_patch` can express the change without giant hunks.

Required gates:

- Read current source from disk.
- Use minimal `apply_patch`.
- Inspect diff.
- Run focused verification when behavior changes.

Stop when:

- Patch misses twice.
- Context is duplicated or visually ambiguous.
- The target changed under you.

## Patch Recovery Path

Use when:

- `apply_patch` cannot find expected lines.
- A hunk partially applied.
- Whitespace, CRLF, tab, or hidden character differences are plausible.

Required gates:

- Re-read exact raw lines with `sed -n 'start,endl' file` and `sed -n 'start,endl l' file`.
- Re-read numbered lines with `nl -ba file | sed -n 'start,endlp'`.
- Patch only the smallest unique line or block.
- Never reuse stale context after partial application.

Stop when:

- Raw source and intended edit still do not align.
- The next hunk would be broad or speculative.

## Structural Rewrite Path

Use when:

- The same syntactic pattern repeats.
- Call signatures, imports, object shapes, or language constructs must be rewritten.
- A textual replacement could touch comments, strings, or unrelated code.

Preferred helpers:

- `ast-grep` for multi-language structural search and rewrite.
- `jscodeshift` for JavaScript and TypeScript codemods.
- OpenRewrite via project Maven or Gradle plugin for Java and JVM migrations.

Required gates:

- Run `scripts/self_check_edit_tools.py --tool <tool>`.
- If self-check fails, run `scripts/prepare_edit_tools.py --tool <tool>`.
- Re-run self-check.
- Inspect generated diff before finalizing.

Stop when:

- Selected helper cannot self-check.
- The rewrite matches broader code than intended.
- No reliable pattern can separate target code from non-target code.

## Agent-Edit Path

Use when:

- The change is multi-file and natural-language-driven.
- Repo context, lint/test feedback, or iterative edit blocks are useful.
- Aider-style edit formats or repo-map behavior would reduce manual patch fragility.

Required gates:

- Define files in scope before invoking an agent-edit helper.
- Keep generated edits pending until diff review.
- Run focused verification after applying accepted changes.

Stop when:

- The helper proposes out-of-scope files.
- The diff cannot be explained from the user intent.

## Review-Before-Apply Path

Use when:

- Large changes should be isolated before landing.
- Generated edits span many files.
- The safest behavior resembles a Plandex-style pending diff with explicit apply gate.

Required gates:

- Keep changes reviewable before committing them to the main worktree when possible.
- Inspect file list, semantic intent, and generated churn.
- Apply only the accepted subset.

Stop when:

- The proposed diff is too large to review.
- Rollback is unclear.

## Generated-Output Path

Use when:

- Formatter, code generator, package manager, lockfile tool, or project scaffold owns the output.
- Manual edits would fight generated state.

Required gates:

- Run the project-owned command.
- Inspect generated diff.
- Reject unrelated churn.

Stop when:

- The owning command changes files outside expected outputs.
- The command updates dependency state without explicit intent.
