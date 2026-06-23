# Review: skill-router

- Artifact Type: skill routing policy and validator update
- Confidence: High
- Review Mode: heavy
- Review Route: inline
- Verdict: PASS

## Review Basis
- Goal: make skill-router route manual edits through `structural-edit`, detect future tool-vs-skill priority drift, and provide a bounded self-repair path for known stale routes.
- Artifact: `/data/lcq/.codex/skills/skill-router`
- Sources: `skill-router/SKILL.md`, `skill-router/references/route-decision.md`, `skill-router/references/policy-schema.md`, `skill-router/references/scenario-fixtures.json`, `skill-router/policies/known-conflicts.json`, `skill-router/scripts/validate_fixtures.py`, `structural-edit/SKILL.md`, `structural-edit/references/fallback-policy.md`, `structural-edit/references/validation-scenarios.md`, `reviewer/SKILL.md`, `skill-tokenless/SKILL.md`
- Constraints: preserve one primary route, saved policy precedence, global soft hook, unrelated dirty files, and `apply_patch` as strict text fallback/execution tool.
- Validators: `quick_validate.py`, `validate_fixtures.py`, `validate_fixtures.py --repair-known-drift`, `validate_structural_routes.py`, counts, grep gate, cleanup check, final production report validation.
- Cleanup: not launched

## Rubric
- Source alignment: manual-edit routing honors `structural-edit` as decision entrypoint and `apply_patch` as allowed fallback/execution tool.
- Drift detection: validator fails when known stale route names or manual edit priority inversion reappear.
- Self-update safety: repair mode is explicit, limited to encoded known drift, and only writes inside `skill-router`.
- Fixture integrity: deterministic fixtures reflect the intended primary route.
- Scope control: no unrelated skill, global config, or generated cache changes.

## Mode Decision
- Route: heavy
- Reason: material routing and validator behavior affect future skill/tool selection.
- Packet: policy diff, validator diff, route contract, schema update, structural-edit authority, validation output.
- Raw transcript handling: omitted

## Alignment Result
- Result: PASS
- Reason: The update moves `sr-013` primary routing to `skill:structural-edit`, keeps `functions.apply_patch` as strict fallback, and documents the precedence.

## Quality Result
- Result: PASS
- Reason: The validator now actively catches the observed drift class and offers an explicit bounded repair command; checks pass after repair.

## Findings
Findings: None

## Recheck Plan
- Run `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/skill-router`.
- Run `python /data/lcq/.codex/skills/skill-router/scripts/validate_fixtures.py`.
- Run `python /data/lcq/.codex/skills/skill-router/scripts/validate_fixtures.py --repair-known-drift`.
- Run `python3 /data/lcq/.codex/skills/structural-edit/scripts/validate_structural_routes.py`.
- Run `python3 /data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py /data/lcq/.codex/skills/skill-router/artifacts/review-report.md --root /data/lcq/.codex/skills`.
- Run `python3 /data/lcq/.codex/skills/skill-tokenless/scripts/validate_skill_production.py /data/lcq/.codex/skills/skill-router/artifacts/production-report.md --root /data/lcq/.codex/skills --stage final`.

## Residual Risks
- Self-repair only handles encoded known drift; new conflict classes still require policy review and validator extension.
