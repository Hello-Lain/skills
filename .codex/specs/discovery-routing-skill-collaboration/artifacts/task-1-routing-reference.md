Salvaged-From-Worker: coding-1

Task 1 → implemented.

Changed:
- [idea-refine/references/discovery-routing.md](/data/lcq/.codex/skills/idea-refine/references/discovery-routing.md)
- [interview-me/references/discovery-routing.md](/data/lcq/.codex/skills/interview-me/references/discovery-routing.md)
- [spec2plan/references/discovery-routing.md](/data/lcq/.codex/skills/spec2plan/references/discovery-routing.md)

Verification:
- `rtk diff idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md spec2plan/references/discovery-routing.md` failed: `rtk diff` proxied to system `diff`, which rejects 3 operands.
- `rtk git diff -- idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md spec2plan/references/discovery-routing.md` exit 0, no output because files are untracked.
- `rtk cmp idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md` exit 0.
- `rtk cmp idea-refine/references/discovery-routing.md spec2plan/references/discovery-routing.md` exit 0.

Artifact write:
- Could not write [.codex/specs/discovery-routing-skill-collaboration/artifacts/task-1-routing-reference.md](/data/lcq/.codex/skills/.codex/specs/discovery-routing-skill-collaboration/artifacts/task-1-routing-reference.md).
- `rtk mkdir -p .../artifacts` failed: read-only filesystem.
- `apply_patch` artifact add was rejected by harness approval layer.
- Complete artifact body below.

```markdown
# Task 1 Routing Reference

## Changed Files

- `idea-refine/references/discovery-routing.md`
- `interview-me/references/discovery-routing.md`
- `spec2plan/references/discovery-routing.md`

## Summary

Created identical Discovery Routing references for `idea-refine`, `interview-me`, and `spec2plan`.

The shared contract defines:

- Three-skill pipeline: idea or direction uncertainty -> `idea-refine`; confirmed direction with missing requirements -> `interview-me`; confirmed spec needing execution plan -> `spec2plan`.
- Explicit role boundaries for direction, spec, and plan artifacts.
- Route signals, entry criteria, and exit criteria for each skill.
- Anti-loop rules to prevent repeated bouncing and downstream skills filling upstream gaps.
- Handoff contract fields for artifact maturity, stop reason, next skill, next artifact, assumptions, risks, and open questions.

## Verification

- `rtk diff idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md spec2plan/references/discovery-routing.md`
  - Result: failed because `rtk diff` proxied to system `diff`, which does not accept three file operands.
- `rtk git diff -- idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md spec2plan/references/discovery-routing.md`
  - Result: exit 0, no output because files are new and untracked.
- `rtk cmp idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md`
  - Result: exit 0.
- `rtk cmp idea-refine/references/discovery-routing.md spec2plan/references/discovery-routing.md`
  - Result: exit 0.

## Risks

- Duplicated reference files can drift unless later validation checks byte identity.
- Artifact file was not written because artifact-directory creation was blocked by read-only filesystem handling, and the subsequent `apply_patch` artifact add was rejected by the harness approval layer.
```
