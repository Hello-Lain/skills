# Examples

Use these examples to calibrate route choice. They are examples, not extra rules.

## Fast Path

Request: "Change one sentence in `README.md`."

- Selected route: `fast path`
- Preflight: read the target paragraph and confirm unique nearby text.
- Edit: use one small `apply_patch` hunk.
- Gate: inspect diff and run no command if the edit is prose-only.
- Stop signal: same paragraph appears multiple times or the target text differs.

## Patch Recovery Path

Request: "The patch failed, fix the same import."

- Selected route: `patch recovery path`
- Preflight: do not reuse the failed hunk.
- Edit: re-read raw lines with `sed -n 'start,endl' file`, `sed -n 'start,endl l' file`, and `nl -ba file | sed -n 'start,endlp'`.
- Gate: retry once with the smallest unique line.
- Stop signal: raw source still does not match the intended old text.

## Structural Rewrite Path

Request: "Rename this React prop across all TSX call sites."

- Selected route: `structural rewrite path`
- Preflight: confirm the rename is syntax-aware and repeated.
- Tool gate: run `python3 edit-orchestration/scripts/self_check_edit_tools.py --tool ast-grep`.
- Edit: use `ast-grep` or a JS/TS codemod helper after self-check passes.
- Stop signal: selected route requires `ast-grep`, and both self-check and preparation fail.

## Agent-Edit Path

Request: "Refactor this feature across its service, tests, and docs."

- Selected route: `agent-edit path`
- Preflight: define in-scope files and behavior before invoking helper tooling.
- Edit: use Aider-style edit blocks or repo-map-assisted flow only after scope is explicit.
- Gate: inspect pending diff before accepting.
- Stop signal: generated diff includes unrelated files or unexplained behavior changes.

## Review-Before-Apply Path

Request: "Apply this large migration proposal, but let me review first."

- Selected route: `review-before-apply path`
- Preflight: identify rollback and expected changed file groups.
- Edit: keep generated changes reviewable before landing where possible.
- Gate: apply only reviewed changes.
- Stop signal: proposed diff is too large or unstructured to review safely.

## Generated-Output Path

Request: "Update generated API types after schema change."

- Selected route: `generated-output path`
- Preflight: identify the project-owned generator command.
- Edit: run the generator rather than hand-editing generated files.
- Gate: inspect generated diff and reject unrelated churn.
- Stop signal: lockfiles or dependency manifests change without dependency intent.
