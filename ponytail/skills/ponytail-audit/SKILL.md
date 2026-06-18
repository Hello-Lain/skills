---
name: ponytail-audit
description: >
  Whole-repo over-engineering audit. Scans entire codebase instead of a
  diff: ranked list of what to delete, simplify, or replace with stdlib/
  native equivalents. Use when user says "audit this codebase",
  "audit for over-engineering", "what can I delete from this repo",
  "find bloat", "/ponytail-audit". One-shot report, does not apply fixes.
---

# Ponytail Audit

Like ponytail-review, but repo-wide. Scan whole tree instead of diff. Rank findings biggest cut first.

## Tags

Same as ponytail-review: `delete:`, `stdlib:`, `native:`, `yagni:`, `shrink:`.

## Hunt

Deps stdlib or platform already ships, single-impl interfaces, factories with one product, wrappers that only delegate, files exporting one thing, dead flags and config, hand-rolled stdlib.

## Output

One line per finding, ranked by impact: `<tag> <what to cut>. <replacement>. [path]`.

End with `net: -<N> lines, -<M> deps possible.` Nothing to cut: `Lean already. Ship.`

## Boundaries

Complexity only. Correctness bugs, security holes, performance → normal review. Lists findings, applies nothing. One-shot. Revert: "normal mode" / "stop ponytail-audit".
