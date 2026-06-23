---
name: scrape
description: Scrape web content as clean markdown/HTML/JSON via the Bright Data CLI (`bdata scrape`). Use when the user wants to fetch a page, extract content from a list of URLs, or crawl paginated listings. Hands off to `search` when URLs must be discovered first. Requires the Bright Data CLI; proactively guides install + login if missing.
---

# Bright Data — Scrape

Get clean content (markdown, HTML, JSON, screenshot) from one or more URLs via the Bright Data CLI. This skill owns the "fetch raw or lightly-structured content" job.

## Setup gate (run first)

Before any scrape, verify the CLI is installed and authenticated:

```bash
if ! command -v bdata >/dev/null 2>&1; then
    echo "bdata CLI not installed — see ../../brightdata-setup/references/bright-data-best-practices-cli-setup.md"
elif ! bdata zones >/dev/null 2>&1; then
    echo "bdata not authenticated — run: bdata login  (or: bdata login --device for SSH)"
fi
```

If either check fails, halt and route the user to `../../brightdata-setup/references/bright-data-best-practices-cli-setup.md`. Do not attempt the legacy `curl` fallback silently — ask the user first.

## Pick your path

| Situation | Action |
|---|---|
| Single URL | `bdata scrape <url> -f markdown` |
| Small list (≤ ~20 URLs) | shell loop, 1 at a time (see `scrape-patterns.md`) |
| Larger list (dozens+) | `xargs -P 4` with parallelism cap (see `scrape-patterns.md`) |
| Paginated listing | scrape page 1 → extract next-page URL → append → repeat (see `scrape-examples.md`) |
| JS-heavy / login-gated / interaction-required | escalate to `bdata browser` (see `brightdata-cli` skill) |
| No URL yet, just a topic | **hand off to `search`** |

## Action

Core commands:

```bash
# Clean markdown (default)
bdata scrape "https://example.com/article" -f markdown -o article.md

# Raw HTML (when you need the DOM)
bdata scrape "https://example.com" -f html -o page.html

# Structured JSON (when the Unlocker returns parsed fields)
bdata scrape "https://example.com" -f json --pretty -o page.json

# Visual snapshot (saves PNG)
bdata scrape "https://example.com" -f screenshot -o page.png

# Geo-targeted (override the exit country)
bdata scrape "https://example.com" --country de -f markdown

```

Full flag reference: [`scrape-flags.md`](scrape-flags.md).

## Verification gate (run before claiming success)

1. **Non-empty output:** `test -s "$out_path"` — or, for stdout, at least 200 bytes of content.
2. **Not a block page** — grep the output for any of these signatures (case-insensitive):
   - `Access Denied`
   - `Just a moment`
   - `Attention Required`
   - `Checking your browser`
   - `captcha`
   - `cf-browser-verification`
   - `cloudflare` *(with < 2KB total body)*
3. **Expected markers present** for the task: e.g., a product page should contain a price pattern (`\$\d`); an article should contain at least one `<h1>` or `# ` heading.
4. **On failure, escalation ladder:**
   - Retry with a different `--country` (e.g., `--country de` if the origin site is US)
   - Escalate to `bdata browser` for full JS rendering (hand off to `brightdata-cli` skill)

Do not report success until all checks above pass.

## Red flags

- Claiming success without inspecting the output.
- Silencing errors with `2>/dev/null` — you'll miss auth failures and rate-limit errors.
- Scraping the same URL repeatedly in the same task — cache the first result.
- Looping `bdata scrape` sequentially for large lists instead of using `xargs -P 4` (or similar) with a parallelism cap.
- Using `curl` against `api.brightdata.com` directly — legacy path; only when the CLI isn't available.

## References

- [`scrape-flags.md`](scrape-flags.md) — every flag with when-to-use notes.
- [`scrape-patterns.md`](scrape-patterns.md) — shell-loop batching, `xargs` parallelism, pagination recipe, retry/backoff, block-page recovery chain, legacy `curl` fallback.
- [`scrape-examples.md`](scrape-examples.md) — (1) single page → markdown, (2) batch a list of URLs with parallelism cap, (3) paginated listing, (4) block-page recovery.
