Salvaged-From-Worker: coding-2

Task 3 complete.

Changed:
- [interview-me/SKILL.md](/data/lcq/.codex/skills/interview-me/SKILL.md): frontmatter narrowed to chosen-direction requirement clarification.
- Added Discovery Routing gate for premature/weak solution choices.
- Added route-to-`idea-refine` before spec writing when direction doubtful.
- Added resume condition: return only after user-confirmed `idea-refine` direction.
- Added handoff-contract note for `spec2plan` / downstream transfer.

Verification passed:
```bash
rtk grep -n "Discovery Routing\\|idea-refine\\|spec2plan" interview-me/SKILL.md
```

Matched:
```text
interview-me/SKILL.md:24:Use Discovery Routing when the requested solution may be premature...
interview-me/SKILL.md:26:Route to `idea-refine` before writing a spec when direction quality is doubtful...
interview-me/SKILL.md:137:- Use `idea-refine` if the spec exposes multiple possible product directions...
interview-me/SKILL.md:139:- Use `spec2plan` when the confirmed spec should become executable tasks.
```

Artifact write blocked by apply_patch approval infrastructure. Complete artifact body:

```markdown
# Task 3: interview-me Handoff Update

## Changed Files

- `interview-me/SKILL.md`

## Summary

- Narrowed frontmatter so `interview-me` focuses on chosen directions with missing requirements, not broad direction stress-testing.
- Added a Discovery Routing gate before interviewing when a solution may be premature, weakly motivated, or one of several competing directions.
- Added route-to-`idea-refine` guidance before writing a spec when direction quality is doubtful.
- Added resume condition: return to `interview-me` only after the user confirms a recommended direction from `idea-refine`.
- Added handoff-contract instruction for downstream transfers, including `spec2plan`.

## Verification

Command:

```bash
rtk grep -n "Discovery Routing\\|idea-refine\\|spec2plan" interview-me/SKILL.md
```

Result:

```text
interview-me/SKILL.md:24:Use Discovery Routing when the requested solution may be premature. Read `references/discovery-routing.md` before interviewing if the user has not chosen a direction, if multiple directions are competing, or if the artifact appears weakly motivated.
interview-me/SKILL.md:26:Route to `idea-refine` before writing a spec when direction quality is doubtful. Resume `interview-me` only after the user confirms a recommended direction from `idea-refine`.
interview-me/SKILL.md:137:- Use `idea-refine` if the spec exposes multiple possible product directions or the chosen solution becomes untrusted.
interview-me/SKILL.md:139:- Use `spec2plan` when the confirmed spec should become executable tasks.
```

## Risks / Notes

- `interview-me/SKILL.md` already had prior dirty edits before this task; this task only added scoped routing/handoff changes on top.
- No commits or pushes were run.
```
