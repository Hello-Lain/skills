---
name: skill-router
description: Resolve Codex skill, MCP, and tool routing conflicts. Use when multiple skills or callable tools match one request; when Codex must output one recommended primary route with priority rationale, suppressed candidates, fallbacks, policy id, evidence, and safety notes; when saving conflict governance policies under this skill so repeated conflicts route deterministically; or when auditing stale routes, duplicate names, router-vs-child overlaps, same-capability tools, missing MCP tools, or mode-gated tool calls.
---

# Skill Router

Choose one route, explain why, preserve the policy.

## Contract

- Emit exactly one `primary_route`; use `blocked:no-safe-route` only when no route is safe.
- Prefer saved policy before ad hoc reasoning when evidence still applies.
- Defer to current system/developer/user instructions, `AGENTS.md`, approval mode, and available tools.
- Never edit other skills, MCP config, hooks, global instructions, caches, or `.tmp` unless the current user request explicitly authorizes that plan.
- Store new or revised governance only inside this skill directory.

## Workflow

1. Capture task, named skills/tools, active mode, unavailable tools, destructive risk, and exact user authorization.
2. Read `references/route-decision.md`; read only relevant entries from `policies/known-conflicts.json`.
3. If policy evidence is stale or missing, mark it in `safety_notes` and re-evaluate from live skill/tool metadata.
4. Apply precedence: binding instructions → mandatory interrupts → exact user-named safe route → saved policy → specific child/domain route → generic fallback.
5. Output the decision block from `references/route-decision.md`.
6. For a new repeatable conflict, read `references/policy-schema.md`, append/update a policy under `policies/`, then run validation.

## Policy Store

- `policies/known-conflicts.json`: active v1 conflict governance.
- `references/policy-schema.md`: policy fields, ids, staleness checks, update rules.
- `references/scenario-fixtures.json`: deterministic acceptance fixtures.
- `scripts/validate_fixtures.py`: validates policy shape, unique ids, path evidence, route-drift invariants, and fixture stability; `--repair-known-drift` applies known safe repairs inside this skill.

## Validation

```bash
python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/skill-router
python /data/lcq/.codex/skills/skill-router/scripts/validate_fixtures.py
python /data/lcq/.codex/skills/skill-router/scripts/validate_fixtures.py --repair-known-drift
```

Run validation after policy or reference changes. Use `--repair-known-drift` only for validator-reported known drift, re-run validation, then review with `reviewer` for material routing changes.
