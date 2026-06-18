---
name: ponytail-review
description: >
  Diff over-engineering review. Finds what to delete: reinvented stdlib,
  unneeded deps, speculative abstractions, dead flexibility. One line per
  finding with tags. Use when user says "review for over-engineering",
  "what can we delete", "is this over-engineered", "simplify review",
  "/ponytail-review". Complements correctness review.
---

# Ponytail Review

Review diffs for unnecessary complexity. One line per finding: location, what to cut, what replaces it. Best outcome: diff gets shorter.

## Tags

| Tag | When | Output |
|-----|------|--------|
| `delete:` | Dead code, unused flexibility, speculative feature | Nothing replaces it |
| `stdlib:` | Hand-rolled thing stdlib already ships | Name the function |
| `native:` | Dep or code replicating platform feature | Name the feature |
| `yagni:` | Abstraction with one impl, config never set, layer with one caller | Inline it |
| `shrink:` | Same logic, fewer lines | Show shorter form |

## Format

`L<line>: <tag> <what>. <replacement>.` or `<file>:L<line>: ...` for multi-file diffs.

## Examples

- `L12-38: stdlib: 27-line validator class. "@" in email, 1 line.`
- `L4: native: moment.js for one format call. Intl.DateTimeFormat, 0 deps.`
- `repo.py:L88: yagni: AbstractRepository with one impl. Inline until second exists.`
- `L30-44: shrink: manual loop builds dict. dict(zip(keys, values)), 1 line.`
- `L52-71: delete: retry wrapper around idempotent local call. Nothing.`

## Scoring

End with `net: -<N> lines possible.` Nothing to cut: `Lean already. Ship.`

## Boundaries

Complexity only. Correctness bugs, security holes, performance → normal review. Smoke test/`assert` self-check is ponytail minimum, never flag as bloat. Does not apply fixes. One-shot. Revert: "normal mode" / "stop ponytail-review".
