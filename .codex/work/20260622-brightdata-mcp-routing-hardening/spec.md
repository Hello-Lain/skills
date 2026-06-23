# Spec: Bright Data MCP Routing Hardening

## Objective

Improve the local `brightdata` skill group so Codex agents consistently discover and prioritize reliable Bright Data MCP tools for live search, batch search, scraping, conditional structured extraction, and research-style Discover/RAG workflows while keeping fallback behavior explicit and verifiable.

## Users

- Primary: Codex agents using `/data/lcq/.codex/skills/brightdata` for Bright Data-backed web data tasks.
- Secondary: the user maintaining local skills and expecting faster, more stable MCP-first execution.

## Problem

The current Bright Data skill group is valid but ambiguous. The parent router contains conflicting guidance between “MCP-first” and “MCP only when needed”; deferred MCP tools such as `search_engine_batch` may be missed unless tool metadata is searched; runtime checks and material skill-update validation are mixed; and research/RAG Discover patterns are not captured locally. Prior live validation also showed `extract` fails in this environment with `MCP error -32601: sampling/createMessage`, so v1 must not depend on `extract` success.

## Success Criteria

- Search, batch-search, scrape, conditional structured extraction, and research-style Discover tasks first check for available Bright Data MCP tools before falling back to CLI, `web.run`, serial shell loops, or generic scraping.
- Reliable current MCP tools are promoted: `discover`, `search_engine`, `search_engine_batch`, `scrape_as_markdown`, `scrape_as_html`, `scrape_batch`, and `session_stats`.
- `extract` remains documented as a conditional tool only: use it when live smoke validation proves sampling support; otherwise use scrape markdown/html plus local schema parsing and field checks.
- Narrow `web_data_*` readers are not recommended in v1 and are removed or downgraded from normal routing guidance.
- Runtime workflow is clearly separated from material skill-maintenance validation.
- Research/RAG guidance covers multi-angle Discover, dedupe/ranking, content quality checks, provenance, and when to scrape selected URLs.
- Validation passes with `quick_validate.py` for touched Bright Data skills plus one real MCP smoke covering discovery, batch search, scrape, stats, and conditional structured extraction fallback.

## Scope

### In

- Patch `brightdata/SKILL.md` to remove MCP routing ambiguity and state a clear MCP-first priority ladder.
- Patch `brightdata/skills/brightdata-mcp-tools/SKILL.md` and MCP references to:
  - require checking active/deferred Bright Data MCP tool availability before fallback;
  - document reliable v1 tools;
  - treat `extract` as conditional on sampling support;
  - remove or downgrade narrow `web_data_*` recommendations;
  - separate runtime checks from material skill-update validation.
- Patch Bright Data search/scrape child guidance where needed so it routes through MCP-first paths for applicable tasks.
- Add or update lightweight research/RAG Discover guidance in references, not the parent router, covering multi-angle query decomposition, dedupe, relevance ranking, provenance, and scrape-after-discover.
- Add acceptance evidence under the topic workspace or existing Bright Data work artifacts.

### Out

- Do not fix `extract` in v1; that is a required follow-up stage after this routing-hardening work.
- Do not implement or enable Pro/platform-data tools.
- Do not add browser automation guidance.
- Do not import the upstream 60+ tool catalog into the local skill.
- Do not auto-edit MCP client/server configuration, secrets, API tokens, account activation, or user account settings.
- Do not restore broad business-analysis, SEO, brand-listening, price-comparison, or marketplace dataset workflows.

## Requirements

### Functional

- The parent router must express a single precedence rule: use MCP-first when active Bright Data MCP tools are available and the task is live web search, Discover, scraping, batch scraping, usage tracking, or conditional structured extraction; use CLI only for reproducible shell/file workflows, local pipelines, broad repo work, tests, or MCP blockers.
- MCP tool guidance must include a compact runtime availability checklist:
  - active tool present or discoverable in current tool metadata;
  - task matches tool capability;
  - account/sampling caveat does not block the chosen tool;
  - output is non-empty and not a block page;
  - fallback path is named when the tool is missing or fails;
  - `session_stats` is used for validation-heavy or multi-call MCP work.
- Deferred tool discovery must be explicit: before declaring a known Bright Data MCP tool missing, search the available/deferred tool metadata when the environment supports tool discovery.
- Structured extraction must be defined as:
  - prefer `extract` only after smoke success proves MCP sampling support;
  - otherwise scrape markdown/html, parse locally to the requested schema, and verify required JSON fields before claiming success.
- Research/RAG guidance must define a lightweight workflow:
  - decompose broad questions into a small set of focused Discover angles;
  - run `discover` with intent and filters when useful;
  - dedupe normalized URLs and rank by relevance;
  - reject empty, off-topic, blocked, or low-provenance results;
  - scrape selected URLs only when Discover output is insufficient;
  - preserve source URLs for citations/provenance.
- Material skill-update validation must remain stricter than runtime usage and require a saved artifact when routing or reliability claims change materially.

### Non-Functional

- Keep parent `SKILL.md` lean; put detailed workflows in child references.
- Avoid adding noisy upstream catalog content that increases token load without affecting current local MCP availability.
- Keep guidance deterministic enough that a future agent can decide route/fallback without asking the user unless account/config mutation is required.
- Preserve credential hygiene: no secrets in prompts, logs, reports, examples, or final answers.

## Constraints

- Current live environment shows `extract` fails with `MCP error -32601: sampling/createMessage`; v1 must pass even when `extract` remains unavailable.
- The user requires a future follow-up to make `extract` work; do not mark that as solved by docs-only fallback.
- User explicitly excludes Pro/platform data, browser automation, and upstream 60+ tool import.
- Local skill edits must preserve existing source license references and avoid unrelated scope restoration.
- Existing dirty Bright Data files may predate this spec; preserve unrelated user work.

## Assumptions To Validate

- [ ] `search_engine_batch` remains available through deferred tool discovery in the active tool registry - validate with `tool_search` or equivalent tool discovery before implementation claims.
- [ ] `discover`, `search_engine_batch`, `scrape_batch`, and `session_stats` still succeed in a fresh smoke run - validate with real MCP calls after edits.
- [ ] Local schema parsing after markdown/html scrape is sufficient for v1 structured extraction tasks when `extract` fails - validate with a small public page and required-field check.
- [ ] Added research/RAG guidance fits in references without bloating the parent router - validate by inspecting resulting diff and running quick validation.

## Risks

- Agents may overuse MCP for tasks needing reproducible shell artifacts - mitigate with explicit CLI fallback criteria.
- Agents may keep trying `extract` despite sampling failure - mitigate by making smoke success a prerequisite for using `extract`.
- Deferred tool discovery may not exist in every client - mitigate by phrasing as “when environment supports tool discovery” and retaining direct visible-tool checks.
- Research/RAG guidance may expand scope - mitigate by keeping it lightweight, reference-only, and excluding Pro/platform/browser tools.
- Official docs may state broader limits than active tool schemas - mitigate by stating active tool schema wins for per-session limits.

## Acceptance Checks

- Run `python3 .system/skill-creator/scripts/quick_validate.py brightdata`.
- Run `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-mcp-tools`.
- If Bright Data search/scrape children are touched, run their `quick_validate.py` checks too.
- Run one real MCP smoke:
  - `session_stats` before or after;
  - `discover` on a public Bright Data MCP/docs query;
  - `search_engine_batch` with two public queries, using deferred tool discovery first if needed;
  - `scrape_batch` on 2 public stable URLs within the active schema limit;
  - conditional structured extraction fallback: scrape a stable public page and locally verify required JSON fields when `extract` still fails;
  - record explicit `extract` status without treating failure as v1 failure.
- Inspect `git diff -- brightdata` and confirm changes match this spec without restoring Pro/platform/browser/60+ tool catalog scope.

## Open Questions

- None for v1 routing hardening.
- Follow-up required: diagnose and make `extract` work by addressing MCP sampling/client/server configuration or version support.
