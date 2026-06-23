# Route Matrix

Pick one primary route. Do not silently cascade from a required structural route into fragile text patching.

## Generator-Owned

Use when a project-owned generator, formatter, scaffold, package manager, or lockfile command owns the output.

- Examples: lockfiles, generated clients, formatted snapshots, templated boilerplate.
- Required action: run the owning command, inspect diff, reject unrelated churn.

## Python

- Primary route: `ast-grep`
- Strict fallback: only for tiny, unique, low-risk edits that are effectively prose-like and do not justify AST rewrite.
- Hard-stop: if semantic rewrite should use `ast-grep` and self-check fails, return `BLOCK`.

## JavaScript / TypeScript

- Primary route: `jscodeshift` for semantic migrations and repeated rewrites.
- Secondary structural route: `ast-grep` for lighter structural rewrites where a full codemod is unnecessary.
- Strict fallback: tiny unique edits only.
- Hard-stop: if structural rewrite should apply and the selected tool is unavailable, return `BLOCK`.

## JSON

- Primary route: `jq`
- Strict fallback: tiny unique formatting-preserving edits only.
- Hard-stop: field/value/path operations must not downgrade to text patching.

## YAML

- Primary route: `yq`
- Strict fallback: rare tiny unique edits that are not semantic key/path/value operations.
- Hard-stop: config path updates must not downgrade to text patching.

## Markdown

- Primary route: `remark`
- Formatting route: project-owned formatter or `prettier` only when output ownership is explicit.
- Strict fallback: tiny unique prose fixes only.
- Hard-stop: heading/section/list/frontmatter edits should not bypass the AST route silently.

## Java

- Primary route: `openrewrite`
- Support condition: valid Maven/Gradle/OpenRewrite build context exists.
- Hard-stop: without valid build context, return `BLOCK` instead of patching semantic Java migrations manually.

## Generic Text

- Allowed route: strict text fallback only when the edit is tiny, unique, and low-risk.
- Otherwise: stop and re-evaluate the route rather than assuming patching is safe.
