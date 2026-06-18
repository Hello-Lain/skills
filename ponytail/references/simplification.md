# Ponytail Simplification Reference

Use this only when the main Ponytail gates are not enough.

## Contract

Simplify code for clarity while preserving exact behavior.

- Same inputs -> same outputs.
- Same errors and edge cases.
- Same side effects and ordering.
- Same public API unless user explicitly asked for API change.
- Existing tests pass without weakening or rewriting expectations.

If unsure, do not make the change. First add/locate a characterization check.

## Context Checklist

- Read project instructions: `AGENTS.md`, `CLAUDE.md`, `README`, nearby conventions.
- Inspect neighboring code for import style, naming, error handling, type depth, test style.
- Identify callers/callees with search before moving or deleting code.
- Check git history/blame when a construct looks weird but intentional.
- Keep refactor-only diffs separate from behavior changes when possible.

## Opportunities

Prefer these when they make code easier to read:

- Deep nesting -> guard clauses or named predicates.
- Long mixed-responsibility fn -> focused helpers with concept names.
- Nested ternary/reduce chains -> plain `if`, loop, lookup, or helper.
- Boolean flag args -> options object or separate fns, only if call sites improve.
- Repeated conditionals -> named predicate.
- Generic/misleading names -> domain names from the codebase.
- Comments explaining obvious "what" -> delete.
- Comments explaining non-obvious "why" -> keep.
- Duplicated logic -> shared helper only after the second real use.
- Dead code/commented-out blocks -> remove after confirming unused.
- Wrapper with no policy/value -> inline.
- One-impl abstraction/factory/strategy -> inline until a second real impl exists.
- Hand-rolled stdlib/native behavior -> stdlib/native feature.

## Anti-Patterns

- Fewer lines but denser control flow.
- Clever chains where a loop is clearer.
- Removing a helper that names a real concept.
- Merging unrelated logic.
- Renaming to personal preference.
- Removing error handling, validation, auth checks, a11y, or data-loss guards.
- Refactoring unrelated files "while here".
- Touching >500 lines manually; use codemod/script or narrow scope.

## Incremental Workflow

1. Pick one simplification.
2. Patch it.
3. Run the smallest relevant test/build/lint command.
4. If it fails, revert that simplification or add missing characterization.
5. Continue only while the diff remains reviewable.

## Verify

- Tests/build/lint pass or failure is pre-existing and documented.
- No test expectations changed unless behavior change was requested.
- Diff contains no unrelated formatting churn.
- New code follows local conventions.
- Result is faster for a new teammate to understand.
