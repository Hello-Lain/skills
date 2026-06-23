# Policy Schema

Policies live in `policies/known-conflicts.json`.

## Required Fields

- `id`: stable `sr-NNN-slug`.
- `status`: `active` or `stale`.
- `category`: one of `duplicate-name`, `stale-route`, `router-child-overlap`, `same-domain-skills`, `same-capability-tools`, `mandatory-interrupt`, `mode-gated-tool`, `missing-tool`, `fallback-policy`.
- `triggers`: user-visible words or conditions that start matching.
- `conditions`: exact constraints that must be true before using the policy.
- `primary_route`: object with `kind` and `name`; kinds: `skill`, `tool`, `mcp`, `blocked`.
- `why`: priority rationale.
- `suppressed`: routes not selected plus reasons.
- `fallbacks`: fallback routes plus activation conditions.
- `evidence`: `path`, `session`, or `spec` evidence objects.
- `safety_notes`: safety, mode, tool, or staleness notes.
- `created_at`, `updated_at`: ISO dates.
- `review_notes`: review status or follow-up.

## Staleness Rules

Mark policy stale when:

- A `path` evidence item is missing or no longer says the cited trigger/route exists.
- Current tool availability contradicts the policy condition.
- Higher-priority prompt/tool instructions override the policy.
- The policy selects a deleted, renamed, or unavailable skill/tool.
- A lower-level tool is primary where a live skill owns the decision contract.

Stale policy behavior: do not silently use it; emit a decision with `safety_notes` describing staleness, then choose from live evidence.

## Self-Update

- `scripts/validate_fixtures.py` must fail on known route drift and print the repair command.
- `scripts/validate_fixtures.py --repair-known-drift` may update only `policies/known-conflicts.json` and `references/scenario-fixtures.json`.
- Repair is limited to encoded safe migrations and priority inversions, such as `edit-orchestration` -> `structural-edit` and manual edits routing through `structural-edit` before `apply_patch`.
- After repair, rerun validation without repair mode and update review/production artifacts for material routing changes.

## Update Rules

- Update only files under `skill-router/`.
- Preserve old ids unless semantics change; create a new id for incompatible precedence changes.
- Add one policy per repeatable conflict, not one per prompt wording.
- Store conflict-resolution decisions only; do not copy full workflows from other skills.
- Run `scripts/validate_fixtures.py` and `quick_validate.py` after every policy change.
