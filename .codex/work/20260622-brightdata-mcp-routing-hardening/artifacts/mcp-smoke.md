# MCP Smoke

- Date: 2026-06-22.
- Deferred discovery: `tool_search` found `mcp__brightdata.search_engine_batch`.
- `session_stats`: PASS before/after smoke; counts updated for `discover`, `search_engine_batch`, `scrape_batch`, `scrape_as_markdown`, and `extract`.
- `discover`: PASS; returned ranked results for a Bright Data MCP tools documentation query.
- `search_engine_batch`: PASS; two Google queries completed in one call and returned official docs/upstream skill results.
- `scrape_batch`: PASS; `https://example.com/` and `https://www.iana.org/domains/reserved` returned fulfilled markdown content.
- `extract`: EXPECTED FAIL; `MCP error -32601: sampling/createMessage`, so v1 uses fallback and does not claim `extract` is fixed.
- Structured fallback: PASS; `scrape_as_markdown https://example.com/` provided fields parsed locally as `title`, `primary_link_text`, and `primary_link_url`.
- Exclusion check: PASS; no restored GitHub/Reuters reader routing or upstream 60+ tool catalog. Remaining Pro/platform/browser mentions are exclusions only.
