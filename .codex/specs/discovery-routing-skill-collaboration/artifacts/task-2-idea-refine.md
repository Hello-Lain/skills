Salvaged-From-Worker: coding-1

Updated [idea-refine/SKILL.md](/data/lcq/.codex/skills/idea-refine/SKILL.md).

Verification passed:

```bash
rtk grep -n "Discovery Routing\\|interview-me\\|spec2plan" idea-refine/SKILL.md
```

Artifact write blocked: `apply_patch` rejected artifact creation with `404 No active credentials...`. Per instruction, complete artifact body:

```markdown
# Task 2: idea-refine Handoff Instructions

## Changed Files

- `idea-refine/SKILL.md`

## Summary

- Updated frontmatter to position `idea-refine` as direction discovery, not requirement clarification or planning.
- Added `Discovery Routing` section that reads `references/discovery-routing.md` when handoff/workflow routing is relevant.
- Added route-in criteria for uncertain ideas, option sets, rough solutions, and premature directions.
- Added route-out criteria: confirmed direction -> `interview-me`; `spec2plan` only when confirmed spec/equivalent clear requirements already exist.
- Clarified that `idea-refine` may borrow `interview-me` one-question-at-a-time questioning only for missing critical facts, without producing a full spec.
- Added explicit handoff contract guidance after Phase 3 output.
- Added anti-pattern and verification checks for Discovery Routing and avoiding full `interview-me` specs.

## Verification

Command:

```bash
rtk grep -n "Discovery Routing\\|interview-me\\|spec2plan" idea-refine/SKILL.md
```

Result: passed. Matches found for Discovery Routing section, `interview-me` handoff/questioning rules, and `spec2plan` gating language.

## Risks / Notes

- `idea-refine/SKILL.md` was already dirty before this task; I preserved unrelated existing edits such as `.codex/ideas/[idea-name].md` output path wording.
- No commit or push performed.
```
