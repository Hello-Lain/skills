---
name: apply-patch
description: >
  Use when Codex manually edits files and should use apply_patch instead of
  shell/Python rewrites: precise source edits, multi-file patches, new/delete/move
  files, patch failure recovery, visually-matching hunk misses, avoiding malformed
  hunks, preserving user changes, or surgical changes where broad rewrites would
  be risky.
---

# Apply Patch

Use `apply_patch` for manual file edits. Do not use shell/Python to create or rewrite files unless a formatter/generator is intentionally producing bulk output.

## Workflow

1. Inspect first: read target snippets with line numbers or exact text. Check `git status` when repo state matters.
2. Patch small: one logical change per patch when possible; split risky multi-file edits.
3. Anchor precisely: include 2-5 stable context lines around each edit; prefer unique nearby symbols over whitespace-only context.
4. Preserve user work: never revert unrelated dirty changes; if target text differs unexpectedly, stop and re-read.
5. Verify: run targeted reads, grep, formatter/tests if relevant, then inspect diff.

## Patch Forms

Update:
```diff
*** Begin Patch
*** Update File: /abs/path/file.ext
@@
 context line
-old line
+new line
 context line
*** End Patch
```

Add:
```diff
*** Begin Patch
*** Add File: /abs/path/new.ext
+first line
+second line
*** End Patch
```

Delete:
```diff
*** Begin Patch
*** Delete File: /abs/path/old.ext
*** End Patch
```

Move:
```diff
*** Begin Patch
*** Update File: /abs/path/old.ext
*** Move to: /abs/path/new.ext
*** End Patch
```

## Precision Rules

- Use absolute paths when available.
- Keep patch grammar exact: `*** Begin Patch`, hunks, `*** End Patch`.
- Prefix every added line in added files with `+`, including blank lines as `+`.
- Do not include prose, JSON, markdown fences, or shell commands inside the tool input.
- Avoid giant replace-all patches; patch the smallest stable block.
- For repeated text, add context until the hunk is unique.
- For generated/minified/lock files, prefer the project tool that owns the file, then inspect diff.

## Failure Recovery

If patch fails:

1. Re-read the exact file region.
2. If context looks identical but still misses, inspect literal lines with `sed -n 'start,endl'`, `nl -ba`, or an equivalent raw/unfiltered view to expose tabs, wraps, CRLF, and trailing spaces.
3. Compare intended old text to current text.
4. Shrink the hunk to the smallest unique edit; replace one exact line first, then add adjacent helper/context in a separate hunk.
5. Retry once with the smaller patch.
6. If still failing, use a different nearby anchor or ask only when intent is ambiguous.

## Visual-Match Miss Playbook

When output looks identical but `apply_patch` reports `Failed to find expected lines`:

1. Treat displayed text as suspect; filtered/compressed tools can hide soft wraps, CRLF, tabs, and trailing spaces.
2. Re-read raw/literal around the target, e.g. `sed -n '120,150l' file` and `nl -ba file | sed -n '120,150p'`.
3. Patch only the failing unique line, not the whole function/block.
4. Insert new helpers or imports in a separate hunk anchored on a single nearby `def`, `class`, or import line.
5. If a first hunk partially applied, re-read before every retry; never reuse stale context from the failed patch.

Common causes:
- missing `+` on added-file lines
- stale context after user/tool edits
- duplicate context matched wrong block
- accidental JSON wrapper around freeform tool input
- line endings or trailing whitespace mismatch
- filtered command output hiding exact whitespace, wrapping, or control characters
- broad function-block anchors drifting after a prior partial patch

## Safety

- Do not use destructive git commands for recovery.
- Do not patch secrets or private key material into files.
- Do not combine unrelated user-visible behavior changes in one patch.
