SPEC2PLAN_ARTIFACT_V1
phase: planner
status: complete
artifact:
# Structural Edit Draft Plan

## Goal
- Mode: heavy
- Risk level: High
- Confidence: Medium
- Build `structural-edit` as the new default manual-edit skill, make structure-aware routes primary, preserve a strict text fallback, and migrate `edit-orchestration` into a compatibility shell with clear rollback and validation gates.

## Draft Task Shape
- Scaffold `structural-edit/` with `scripts/`, `references/`, and `agents/openai.yaml`.
- Reuse `edit-orchestration` script patterns for tool manifests and self-checks, but extend coverage to `jq`, `yq`, `remark`, and route selection.
- Move policy detail into `references/` so `SKILL.md` stays concise.
- Rewrite `edit-orchestration` so it delegates to `structural-edit` rather than claiming patch-first authority.
- Produce route-scenario validation, production-report artifacts, and final reviewer acceptance.

## Key Constraints
- No `sudo` or system package-manager mutation.
- No silent downgrade when a structural route should apply.
- One authoritative default route after migration.
- Preserve unrelated dirty work and keep rollback explicit.
SPEC2PLAN_ARTIFACT_END
