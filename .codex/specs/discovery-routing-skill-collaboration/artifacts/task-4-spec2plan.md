Salvaged-From-Worker: coding-3

Implemented Task 4 in [spec2plan/SKILL.md](/data/lcq/.codex/skills/spec2plan/SKILL.md).

Changes:
- Added `references/discovery-routing.md` read rule for ambiguous source maturity.
- Added `Discovery Routing Gate`.
- Documented `idea-refine -> interview-me -> spec2plan`.
- Added refusal gate for unconfirmed ideas/directions unless user accepts assumptions.
- Clarified `idea-refine`/`interview-me` are upstream sources, not planning substitutes.

Verification passed:
```bash
rtk grep -n "Discovery Routing\\|idea-refine\\|interview-me" spec2plan/SKILL.md
```

Artifact write blocked by tool approval layer, so complete artifact body:

```markdown
# Task 4: spec2plan Collaboration Gate

Status: complete

## Changed Files

- `spec2plan/SKILL.md`

## Changes Made

- Added `references/discovery-routing.md` as a required read when source artifact maturity is ambiguous.
- Added `Discovery Routing Gate` section.
- Documented upstream pipeline: `idea-refine -> interview-me -> spec2plan`.
- Clarified `idea-refine` and `interview-me` as upstream artifact sources, not planning substitutes.
- Added refusal gate for unconfirmed idea one-pagers, weak directions, competing options, and premature solutions unless the user explicitly accepts recorded assumptions and asks to proceed.
- Added rule to avoid hiding product-direction or spec-quality gaps as implementation assumptions.

## Verification

Command:

```bash
rtk grep -n "Discovery Routing\\|idea-refine\\|interview-me" spec2plan/SKILL.md
```

Result: pass

Matched:

```text
spec2plan/SKILL.md:24:## Discovery Routing Gate
spec2plan/SKILL.md:29:idea-refine -> interview-me -> spec2plan
spec2plan/SKILL.md:32:- `idea-refine` chooses and stress-tests the direction; it is not a planning substitute.
spec2plan/SKILL.md:33:- `interview-me` turns a chosen direction into a confirmed spec; it is not a planning substitute.
spec2plan/SKILL.md:34:- If the input is an unconfirmed idea one-pager, weak direction, competing options, or a premature solution, do not draft a plan. Route through Discovery Routing to `idea-refine` or `interview-me` unless the user explicitly accepts recorded assumptions and asks to proceed.
```

## Notes

- `spec2plan/SKILL.md` already had unrelated dirty edits before this task. This task preserved them.
- No commits or pushes performed.
- Requested artifact path `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-4-spec2plan.md` was not created because `apply_patch` was rejected by the approval layer.

## Risks

- Low: stricter gating may block planning from informal but usable requirements unless the user explicitly accepts assumptions.
```
