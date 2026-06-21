# Bright Data MCP Minimal Tool Reference

This local skill keeps only search, page scrape, batch, extraction, and narrow cache-reader tools.

## Core Tools

| Tool | Use |
| --- | --- |
| `search_engine` | Google/Bing/Yandex SERP search with URL/title/description results |
| `search_engine_batch` | Multiple independent SERP queries |
| `scrape_as_markdown` | Read a webpage as clean markdown |
| `scrape_as_html` | Read a webpage as HTML |
| `scrape_batch` | Read up to 5 webpages as markdown |
| `extract` | Scrape a URL, then AI-extract structured JSON using an extraction prompt |

## Narrow Readers

Use only when already available and the URL matches exactly:

| Tool | Requirement |
| --- | --- |
| `web_data_github_repository_file` | GitHub repository file URL |
| `web_data_reuter_news` | Reuters article URL |

## Selection Rules

- Unknown URL/topic → `search_engine`, then scrape chosen URLs.
- Known URL → `scrape_as_markdown`.
- Need DOM/source details → `scrape_as_html`.
- ≤5 URLs → `scrape_batch`.
- Need a small JSON object from one page → `extract` with a clear schema prompt.
- Need shell reproducibility or saved files → prefer CLI references instead.

## Output Checks

- Search: require at least one relevant result or state that no result was found.
- Scrape: require non-empty content and reject block pages.
- Extract: verify required fields exist; do not invent missing fields.
