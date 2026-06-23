# Spec: Skill Router

## Objective
Build a new Codex skill named `skill-router` for Codex agents and the user to resolve global skill/MCP/tool routing conflicts. The skill must choose one recommended route when multiple skills or tools match the same request, explain the priority decision, name suppressed or fallback candidates, and persist governance policies so repeated conflicts do not recur.

## Users
- Primary: future Codex agents operating in `/data/lcq/.codex` and child workspaces.
- Secondary: the user maintaining the Codex skill directory, MCP configuration, and callable tool policy.

## Problem
The current Codex setup has overlapping skill triggers, old cached skills, missing or stale tool routes, and multiple callable tools that claim the same job. This causes ambiguous routing, repeated conflict analysis, unnecessary context loading, and inconsistent tool use. The immediate trigger is the audit that found conflicts across Bright Data, planning/execution, review, code graph/context tools, web/search tools, agent managers, shell/read/edit routes, and stale names such as `$plan-grill`.

## Success Criteria
- Given a task where multiple skills or tools match, `skill-router` outputs exactly one recommended primary route.
- Each route decision includes priority rationale, suppressed candidates, fallback candidates, and evidence references.
- Conflict governance policies are persisted under `/data/lcq/.codex/skills/skill-router/` and loaded before new ad hoc routing.
- Re-running the same conflict scenario returns the same policy-backed route unless source evidence changed.
- The skill never edits other skill directories, MCP config, global instructions, or `.tmp` content unless a later confirmed plan explicitly authorizes that work.
- The skill can classify and route all conflict groups found in the prior audit: Bright Data, planning/team workflow, execution/orchestration, review, skill auditing, debug/test/env, context/handoff/compression, git/conductor, codegraph/lean-ctx, web/Bright Data, agent managers, shell/read/search/edit tools, and missing OpenAI docs MCP.

## Scope
### In
- Create `skill-router` as a standalone skill directory with its own `SKILL.md`.
- Define a route-decision output contract with: `primary_route`, `why`, `suppressed`, `fallbacks`, `policy_id`, `evidence`, `safety_notes`.
- Add a persistent governance policy store inside `skill-router`, preferably under `policies/`.
- Support policy entries for skill conflicts, MCP/tool conflicts, stale routes, missing tools, mode-gated tools, exact duplicate skill names, and router-vs-child skill families.
- Define precedence rules for common cases:
  - User-named skill beats generic trigger unless safety or mode constraints block it.
  - Mandatory interrupt skills, such as Python env repair, beat ordinary debug/test workflows when their exact blocker appears.
  - Router parent skills may delegate to child skills, but child skills own concrete task execution.
  - CodeGraph owns code symbol/call/impact questions; lean-ctx owns cached read/search/shell where appropriate.
  - `apply_patch` owns manual file edits; edit fallbacks must be explicit.
  - Bright Data owns anti-bot, structured scrape/search, and explicit Bright Data tasks; generic `web.run` remains valid for ordinary official-source browsing and citations when Bright Data is not required.
  - Multi-agent tools require explicit user delegation; planning skills may prepare worker scopes without spawning agents.
- Include initial policies for all conflicts listed in the audit.
- Include validation fixtures or scenarios that prove the router returns a single route and stable policy id.

### Out
- Do not delete `.tmp/brightdata-skills` or other cached files in v1.
- Do not rewrite existing skills such as `conductor`, `brightdata`, `spec2plan`, `plan2do`, `reviewer`, or `openai-docs` in v1.
- Do not modify `/data/lcq/.codex/config.toml`, MCP server definitions, hooks, global instructions, or tool availability in v1.
- Do not spawn subagents, run live web data calls, or perform external network validation just to prove routing.
- Do not replace domain skills; `skill-router` decides routing and stores policy, then hands off.

## Requirements
### Functional
- Detect candidate skills and tools from a task description, active skill metadata, tool metadata, and saved router policies.
- Match conflicts by stable categories: `duplicate-name`, `stale-route`, `router-child-overlap`, `same-domain-skills`, `same-capability-tools`, `mandatory-interrupt`, `mode-gated-tool`, `missing-tool`, `fallback-policy`.
- Produce one route decision in a compact, machine-readable Markdown block.
- Persist new or revised policies with stable ids, trigger conditions, precedence, suppressed routes, fallbacks, evidence paths, created/updated timestamps, and review notes.
- Prefer existing saved policy when its evidence still applies; otherwise mark the policy stale and require re-evaluation.
- Warn when a route depends on unavailable MCP tools or forbidden tool modes.
- Provide a “no safe route” result when all candidates are blocked by missing tools, approval mode, destructive risk, or unresolved user requirements.
- Provide a handoff note for downstream skills naming the chosen skill/tool, required references to read, blocked alternatives, and validation expectations.

### Non-Functional
- Deterministic: same inputs and unchanged policies return the same primary route.
- Minimal context: read only the policy entries and metadata needed for the conflict.
- Auditable: every persisted policy includes evidence and a rationale suitable for later review.
- Safe by default: route decisions are advisory unless the current user request explicitly authorizes edits or execution.
- Reversible: policy files are appendable or versioned so bad governance can be rolled back.

## Constraints
- Store all new governance data under `/data/lcq/.codex/skills/skill-router/`.
- Default policy format must be readable by both humans and agents; YAML frontmatter plus Markdown body is acceptable.
- Existing source files outside `skill-router` are read-only during v1 implementation.
- Secrets, tokens, raw MCP auth state, and private session transcripts must not be copied into policies.
- Current approval mode and active tool instructions override router preferences.

## Assumptions To Validate
- [ ] Saved policy files under `skill-router/policies/` are sufficient persistence for future Codex sessions - validate by reloading a sample policy in a fresh route decision.
- [ ] Active skill and tool metadata can be summarized without scanning private or secret files - validate with a fixture based on the prior audit.
- [ ] A compact Markdown route block is adequate for downstream skill handoff - validate with `spec2plan`, `plan2do`, and direct user-facing scenarios.
- [ ] Initial policies can cover the current known conflicts without editing existing skills - validate by replaying the conflict audit categories.

## Risks
- A router skill may become a new global bottleneck - mitigate by keeping it advisory, concise, and policy-backed.
- Stale policies may preserve wrong decisions after a skill changes - mitigate with evidence paths, timestamps, and stale-evidence checks.
- Policy files may duplicate existing skill rules - mitigate by storing only conflict-resolution decisions, not full skill workflows.
- Router decisions may conflict with higher-priority system/developer instructions - mitigate by explicitly deferring to current prompt/tool policy and returning “blocked” when precedence is unsafe.
- Over-broad routing could suppress valid specialized skills - mitigate with fallback candidates and reviewable suppression reasons.

## Acceptance Checks
- A fixture with `brightdata scrape known URL` returns `brightdata-mcp-tools` or `brightdata-web-scrape` according to MCP availability, with `web.run` listed only as fallback.
- A fixture with `repo symbol impact analysis` returns `codegraph-project-reader`/`mcp__codegraph` primary, with lean-ctx graph/read tools scoped as support or fallback.
- A fixture with `ModuleNotFoundError during tests` returns `uv-mirror-env` primary and suppresses generic debug/TDD until env is repaired.
- A fixture with `review for over-engineering` returns `ponytail-review` primary and lists `reviewer` as fallback for correctness/security findings.
- A fixture with `execute plan.md` returns `plan2do` primary and suppresses `codex2codex` unless the user explicitly requests worker isolation.
- A fixture with `multi-agent implementation` returns a route that refuses agent spawning unless the user explicitly authorized delegation.
- A fixture with the stale `$plan-grill` route marks it stale and recommends `spec2plan` for plan creation/hardening.
- A repeated fixture loads the saved `policy_id` and produces the same route without redoing full conflict analysis.
- No acceptance check writes outside `/data/lcq/.codex/skills/skill-router/`.

## Open Questions
- Should v2 be allowed to propose patches to existing skills when a policy proves a stale route, such as `$plan-grill`, or should all fixes stay in `skill-router` forever?
- Should policy validation be implemented as a script in v1, or is a documented fixture table enough for the first version?
