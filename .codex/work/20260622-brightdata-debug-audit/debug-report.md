# Debug Skill Report: brightdata

- Verdict: REVISE
- Date: 2026-06-22
- Scope: local `brightdata` parent router plus `brightdata-mcp-tools` child/reference docs.

## Verdict

- Impact: net-positive, not production-clean.
- Confidence: high.
- One-line reason: recent MCP-first updates pass deterministic validators and real MCP calls prove efficiency gains, but remaining routing contradictions, deferred-tool discovery gaps, and access/sampling caveats can still cause underuse or false success claims.

## Evidence Used

- Skill files: `brightdata/SKILL.md`, `brightdata/skills/brightdata-mcp-tools/SKILL.md`, `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp.md`, `brightdata/skills/brightdata-mcp-tools/references/bright-data-mcp-mcp-tools.md`, `brightdata/skills/brightdata-web-search/SKILL.md`, `brightdata/skills/brightdata-web-scrape/SKILL.md`.
- Prior live artifact: `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md`.
- Prior review artifact: `.codex/work/20260622-brightdata-mcp-first-efficiency/review-debug-skill.md`.
- Deterministic checks: `python3 debug-skill/scripts/skill_audit_core.py --skill brightdata --json`, `python3 .system/skill-creator/scripts/quick_validate.py brightdata`, `python3 .system/skill-creator/scripts/quick_validate.py brightdata/skills/brightdata-mcp-tools`.
- Current live MCP checks: `session_stats`, `discover`, `search_engine_batch`, `scrape_batch`.
- Upstream/source checks: `https://docs.brightdata.com/ai/mcp-server/tools`, `https://github.com/brightdata/skills/blob/main/skills/bright-data-mcp/references/mcp-tools.md`, local readonly clone `.tmp/brightdata-skills` at commit `8d427e9`.
- Dirty-tree context: `git diff --stat -- brightdata` showed pre-existing Bright Data edits; this audit did not change target skill files.

## Execution Trace

1. Trigger: user requested `debug-skill` audit of `brightdata` and solution search.
2. Skill instructions loaded: `debug-skill`, report template, Hermes reuse reference, `context-engineering`, and `edit-orchestration` for the artifact write.
3. Local evidence loaded: parent router, MCP child, MCP refs, web-search/web-scrape child skills, prior validation/review artifacts.
4. Deterministic validation: parent and MCP child passed quick validation; audit core found structure/size constraints passing.
5. Real tool validation: MCP calls confirmed `discover`, `search_engine_batch`, `scrape_batch`, and `session_stats` are usable; prior validation confirmed `extract` and `web_data_github_repository_file` fail in this environment with explicit fallback-worthy errors.
6. Upstream search: Bright Data MCP docs and upstream Bright Data skills were inspected for route matrices, group taxonomy, missing-tool handling, and research/RAG workflow patterns.
7. Output: this report only; no target skill modification.

## Effectiveness

- Quality: improved versus static guidance because live MCP behavior and upstream docs were both checked.
- Efficiency: `search_engine_batch` collapsed multiple SERP queries into one call; `scrape_batch` collapsed multiple page reads into one call.
- Stability: batch tools returned structured per-item results; failed tools returned explicit errors instead of silent partial success.
- Verification: deterministic validators passed; live MCP checks provided reliability/fallback evidence.
- Context handling: large MCP/page outputs were kept out of the main answer and summarized in artifacts.
- User friction: no new questions needed; reversible report artifact only.

## Findings

| ID | Type | Severity | Evidence | Impact | Solution |
| --- | --- | --- | --- | --- | --- |
| F1 | instruction ambiguity | high | `brightdata/SKILL.md:21` says phase flow ends with “MCP only when needed”; `brightdata/SKILL.md:25` says MCP-first. | Agents may still pick CLI/web/manual loops before MCP, losing speed/stability. | Replace with a single priority ladder: if Bright Data MCP tools are present and task is live web/search/scrape/extract, check MCP route first; use CLI only for reproducibility, files, pipelines, tests, or MCP blockers. |
| F2 | documentation/reference mismatch | high | `brightdata/skills/brightdata-mcp-tools/SKILL.md:15` and refs include narrow GitHub/Reuters readers; `brightdata/skills/brightdata-mcp-tools/SKILL.md:23` says do not route to `web_data_*`. | Agents may either skip useful narrow readers or over-block all `web_data_*` guidance. | Reword boundary: allow explicitly listed narrow readers when present and active; block broad platform-data/feed/marketplace `web_data_*` workflows. |
| F3 | tooling gap | high | `search_engine_batch` only appeared after deferred `tool_search`; current `session_stats` confirms it was actually callable and used. | Agents can falsely decide “tool unavailable” and fall back to serial searches or `web.run`. | Add a deferred-tool discovery step: before declaring a known Bright Data MCP tool unavailable, search tool metadata for the expected tool/group, then record present/missing/fallback. |
| F4 | recovery gap | high | Prior validation: `extract` failed with `MCP error -32601: sampling/createMessage`; `web_data_github_repository_file` failed with `HTTP 400: Customer is not active`. | Parent over-promotes extraction/readers; agents may claim success or retry unstable paths. | Parent and child should say “MCP-first when available and validated”; `extract` requires sampling support and valid JSON; narrow readers require active account/tool access. |
| F5 | workflow overreach/underreach | medium | Tool ref has a material-update validation matrix but no compact runtime availability checklist. | Normal tasks may either overrun a full matrix or skip cheap `session_stats`/output gates during expensive MCP work. | Split “runtime workflow” from “skill-maintenance validation”; runtime checklist: tool present, account active, sampling needed, output verified, fallback selected, stats if 3+ MCP calls/material claim. |
| F6 | output-actionability gap | medium | `brightdata/SKILL.md:33` points broadly to upstream repo for removed scopes; upstream has useful research/RAG/group patterns not summarized locally. | Future agents lack a clear extension map and may import too much or miss useful Discover workflows. | Add a small optional “future extension candidates” reference: live-research, RAG, Pro groups, browser automation, platform feeds; keep parent lean. |
| F7 | schema drift risk | low | Official docs currently describe broader limits/groups; active tool schema in this session caps `scrape_batch` at 5 URLs. | Agents may trust docs over active schema and send invalid calls. | Guidance should say active MCP tool schema wins over docs; docs are source of capability intent, not per-session limits. |

## Reuse Search

| Source project/repo | Source link | Mature signal | Borrowed idea | Reusable component/CLI/schema | Adoption mode | Target skill change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Bright Data MCP docs | `https://docs.brightdata.com/ai/mcp-server/tools` | official tool reference | modes, groups, tool descriptions, `session_stats`, batch/extract semantics | docs reference | reference-only | use as authoritative external source for current MCP capabilities | do not copy 60+ tools into parent; bloats local skill |
| Bright Data skills repo | `https://github.com/brightdata/skills` | vendor-maintained skill set | tool availability check, group taxonomy, missing-tool workflow | skill patterns | adapt | safer route matrix and extension map | reject “No exceptions” and auto-config mutation; conflicts with local safety/policy |
| Upstream `bright-data-mcp` skill | `https://github.com/brightdata/skills/blob/main/skills/bright-data-mcp/references/mcp-tools.md` | dedicated MCP skill | tool/group table and fallback-worthy tool choice | markdown reference | adapt | local MCP tool reference | do not restore platform-data workflows by default |
| Upstream `live-research` skill | `https://github.com/brightdata/skills/tree/main/skills/live-research` | reusable research workflow | multi-angle Discover, dedupe, rank, cite | workflow pattern | optional future ref | `brightdata-web-search` research mode | not parent-default; would add context bloat |
| Upstream `rag-pipeline` skill | `https://github.com/brightdata/skills/tree/main/skills/rag-pipeline` | retrieval design pattern | Discover as retrieval, provenance, quality-gating | workflow pattern | optional future ref | Discover/RAG guidance | no direct pipeline unless user asks |
| Local MCP validation artifact | `.codex/work/20260622-brightdata-mcp-first-efficiency/artifacts/mcp-validation.md` | real current-session evidence | fallback rules for `extract` and GitHub reader | validation matrix | direct reuse | parent/child caveats | no rejection |

## Candidate Improvements

| Candidate | Target surface | Summary | Benefit | Risk / maintenance cost | Fitness / safety |
| --- | --- | --- | --- | --- | --- |
| A | `brightdata/SKILL.md` | Replace phase sentence with explicit MCP-first priority ladder and caveated fallback. | Removes main underuse ambiguity. | Very low docs-only change. | Safe; high value. |
| B | `brightdata-mcp-tools/SKILL.md` | Fix `web_data_*` boundary to allow only listed narrow readers when active. | Prevents contradictory routing. | Low. | Safe. |
| C | MCP refs | Add runtime availability/fallback checklist plus deferred tool-discovery instruction. | Reduces false unavailability and false success claims. | Low token cost if kept in ref. | Safe; directly supported by live evidence. |
| D | MCP refs | Split runtime checks from material skill-update validation matrix. | Prevents overcalling during normal tasks while preserving maintenance rigor. | Low. | Safe. |
| E | Web-search refs | Add optional research/RAG workflow note: multi-angle Discover, dedupe, quality gates, provenance. | Improves live research/source discovery quality. | Medium context-bloat risk. | Keep in reference, not parent. |
| F | MCP refs | Add “active tool schema wins” note for per-session limits. | Handles docs/tool schema drift. | Very low. | Safe. |

## Promotion Gates

- Evidence sufficient: yes for docs-only fixes A-D/F; medium for E because scope needs user approval.
- Real user-visible impact: yes; fixes prevent wasted serial calls, unstable extraction claims, and missed batch tools.
- Observable behavior improvement: yes; live MCP calls show batch/search/stats gains and explicit failure modes.
- Constraints pass: yes before edits; re-run validators after any future target-skill changes.
- Rollback clear: yes; scoped markdown changes only.
- Human approval before execution: required for modifying target `brightdata` files; this report is audit-only.

## Recommendation

- Do now if approved: A, B, C, D, F as one small docs-only patch, then run `quick_validate.py` on `brightdata` and `brightdata-mcp-tools`.
- Defer: E unless the user wants a broader `brightdata-live-research` / Discover-RAG extension.
- Keep: live MCP validation matrix for material skill updates, but make normal runtime checks lighter.
- Do not import: upstream “Bright Data MCP handles all web data, no exceptions” policy or auto-mutating MCP config; local safety/tool policy needs explicit fallback and user-controlled config changes.
