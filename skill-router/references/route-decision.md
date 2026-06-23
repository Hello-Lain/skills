# Route Decision Contract

Use this reference before emitting a `skill-router` decision.

## Candidate Sources

- Active skill metadata: names, descriptions, source locators.
- Callable tool metadata: tool names, namespaces, approval/mode constraints.
- Current prompt stack: system, developer, user, `AGENTS.md`.
- Saved policies in `policies/known-conflicts.json`.
- Fresh evidence paths named by a policy.

Do not scan secrets, auth files, raw sessions, or private transcripts to decide routing.

## Precedence

1. Binding current instructions and tool constraints.
2. Safety/mode blockers: destructive risk, missing required tool, approval denial, unavailable Plan-mode-only tool.
3. Mandatory interrupt skills for exact blockers, e.g. `uv-mirror-env` for Python env/import failures.
4. Exact user-named skill/tool, unless blocked by 1-3.
5. Fresh saved policy with matching trigger and condition.
6. Specific child/domain skill over parent router for concrete execution; parent router only when child is unclear.
7. Specialized domain route over generic route.
8. Lowest-risk fallback or `blocked:no-safe-route`.

## Common Ties

- Bright Data: explicit Bright Data, anti-bot, Web Unlocker, SERP/Search API, Discover, and structured scraping beat generic browsing.
- Ordinary official-source browsing/citations: `web.run` is valid when Bright Data is not required; OpenAI product docs route through `openai-docs` first.
- Code understanding: `codegraph-project-reader` owns symbol/call/impact; `lean-ctx` owns cached read/search/shell support.
- Manual file edits: `structural-edit` owns edit route decisions; `functions.apply_patch` is the strict text fallback/execution tool only when that route allows it; shell redirection edits are suppressed.
- Plan creation: `spec2plan`; plan execution: `plan2do`; stale `$plan-grill` routes are invalid.
- Review: `reviewer` owns generic quality gates; `ponytail-review` owns over-engineering diff review; `debug-skill` owns skill execution audits.
- Multi-agent spawning: require explicit user delegation; otherwise route to planning/scoping or block spawning.

## Output Block

Emit one compact block:

```markdown
### Skill Router Decision
- primary_route: `kind:name`
- why: <priority reason>
- policy_id: `<id|none>`
- evidence: <paths, metadata, or unavailable evidence>
- suppressed: `<kind:name>` — <reason>; ...
- fallbacks: `<kind:name>` if <condition>; ...
- safety_notes: <mode/tool/destructive/staleness notes or "None">
```

Rules:

- `primary_route` must be singular.
- If all candidates are blocked, set `primary_route: blocked:no-safe-route` and list blocked candidates in `suppressed`.
- Include downstream handoff notes in `safety_notes` when the chosen skill must read specific references or avoid specific tools.
- Do not claim a tool is available unless it is present in the active callable tool list or discoverable metadata.
