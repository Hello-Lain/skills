SPEC2PLAN_ARTIFACT_V1
phase: reviewer
status: complete
artifact:
## Scenario Probes
- Validate Python semantic edit classification prefers `ast-grep`.
- Validate JS/TS migration classification prefers `jscodeshift` and only uses simpler structural fallback when justified.
- Validate JSON/YAML path updates classify to `jq` and `yq`, then `BLOCK` when the required tool is unavailable.
- Validate Markdown section rewrites classify to `remark`, while tiny unique prose fixes may still use strict text fallback.
- Validate generated-output and Java/OpenRewrite edge cases keep generator-owned or `BLOCK` behavior instead of silent patch fallback.

## Code/doc contradictions
- The current `edit-orchestration` contract still treats `apply_patch` as the default fast path, which conflicts with the new spec and must be downgraded.
- The `codex2codex` heavy planner path is blocked because `openai-codex==0.1.0b3` is not currently resolvable, so the run needs explicit fallback evidence instead of silent downgrade.
- Tooling docs must distinguish structured operations that require `BLOCK` from tiny prose changes that may use strict fallback, or the old architecture will leak back in.

## Repo-unanswerable user questions
- None blocking; the confirmed spec already locks route priorities, migration outcome, and review expectations.

## Recommended fixes
- Add a dedicated route-decision helper so validation scenarios prove route choice deterministically.
- Keep `edit-orchestration` as a compatibility shell, not a second default.
- Record the heavy-subagent blocker in workspace artifacts and final review basis.
SPEC2PLAN_ARTIFACT_END
