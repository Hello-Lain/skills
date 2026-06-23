# Bright Data MCP Research / RAG

Use this as a lightweight reference for research-style source discovery when Bright Data MCP is available.

## When To Use

- Broad question → need a compact set of authoritative sources.
- Research/RAG → need provenance, dedupe, and rank before scraping.
- Discover-first workflows → need an efficient source shortlist before `scrape_as_markdown`, `scrape_as_html`, or `scrape_batch`.

## Workflow

1. Break the question into 3-5 focused angles.
2. Run `discover` with a clear intent for each angle.
3. Deduplicate normalized URLs across results.
4. Keep only on-topic results with usable content or strong relevance.
5. Reject blocked, empty, or low-provenance results.
6. Scrape only the selected URLs that still need full content.
7. Preserve source URLs for citations/provenance.

## Quality Gate

- Prefer the smallest source set that answers the question.
- Prefer fresh pages over stale mirrors when freshness matters.
- Do not let one noisy result dominate the shortlist.
- If results are weak, reframe the intent before widening scope.

## Out Of Scope

- Pro/platform data.
- Browser automation.
- Broad dataset ingestion.
- Long-running index build pipelines.

## Related

- `bright-data-mcp.md`
- `bright-data-mcp-mcp-tools.md`
