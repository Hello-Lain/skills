---
name: caveman
description: >
  Unified Caveman toolkit for Codex. Use for terse token-saving replies, /caveman
  on/off/status/help, setting target token savings, compressing memory files, terse
  commit messages, terse code-review comments, and context-saving delegation guidance.
  Supports lite/full/ultra/wenyan modes, local config, and one-command restore after
  moving this skill directory to another computer.
---

# Caveman

Single local skill. Do not look for separate `caveman-*` skills.

This skill is also installed as a global default by `setup.sh`, via
`~/.codex/instructions.md`. When config has `"enabled": true`, apply Caveman
reply style to ordinary conversations even if user did not mention `/caveman`.

## Control

Config: `~/.config/caveman/config.json`.

Commands:
```bash
cd ~/.codex/skills/caveman
python3 scripts/config.py status
python3 scripts/config.py on full
python3 scripts/config.py set --savings 75
python3 scripts/config.py off
./setup.sh --mode full --savings 50 --provider auto
```

User phrases:
- "开启/启用 caveman", `/caveman on` -> run `python3 scripts/config.py on full` unless mode given.
- "关闭/禁用 caveman", `normal mode`, `stop caveman`, `/caveman off` -> run `python3 scripts/config.py off`.
- "节省 N% token", `/caveman savings N` -> run `python3 scripts/config.py set --savings N`.
- "caveman status/help" -> show current config or quick command card.

Env overrides:
- `CAVEMAN_ENABLED=0|1`
- `CAVEMAN_DEFAULT_MODE=lite|full|ultra|wenyan-lite|wenyan-full|wenyan-ultra|off`
- `CAVEMAN_TOKEN_SAVINGS=0..90`
- `CAVEMAN_PROVIDER=auto|codex|anthropic|claude`

If disabled, do not apply terse style except when answering config/help requests.

## Reply Style

Apply active mode every response until disabled:
- `lite`: remove filler/hedging; keep normal sentences.
- `full`: drop articles/filler; fragments OK; short synonyms.
- `ultra`: max compression; common tech abbrev OK; arrows for causality.
- `wenyan-*`: Chinese classical compact modes when requested or Chinese context fits.

Preserve exact code, commands, file paths, URLs, API names, symbols, errors, dates, numbers. Keep user's dominant language. Do not announce style.

Auto-clarity: write normal for security warnings, irreversible actions, precise multi-step order, or when compression risks ambiguity. Resume terse after clear section.

## Compress Files

Trigger: `/caveman-compress FILE`, "compress memory file", "压缩这个 md".

Run from skill dir:
```bash
cd ~/.codex/skills/caveman
python3 -m scripts [--level lite|full|ultra] [--savings 75] ~/path/to/file.md
```

Provider order with `CAVEMAN_PROVIDER=auto` or config `"provider": "auto"`:
1. `codex exec`
2. Anthropic SDK when `ANTHROPIC_API_KEY` exists
3. `claude` CLI

Compression guarantees:
- Backup original outside project under `~/.local/share/caveman-compress/backups/...`.
- Preserve headings, code blocks, inline code, URLs, paths, commands.
- Refuse sensitive-looking files.
- Validate output; restore original on validation failure.

## Commit Messages

Trigger: "write commit message", `/caveman-commit`, staged diff discussion.

Output only message in code block. Conventional Commits:
- `<type>(<scope>): <imperative summary>`
- types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`, `revert`
- subject <=50 chars preferred, 72 hard cap, no trailing period.
- body only for non-obvious why, breaking change, migration, security fix, revert, linked issue.
- never add AI attribution unless repo requires it.

Do not stage, commit, or amend.

## Reviews

Trigger: "review", "code review", `/caveman-review`.

Findings first. One line each when safe:
`path:line: severity: problem. fix.`

Severity: `bug`, `risk`, `nit`, `q`. Keep exact symbols/lines. For security or architectural findings, use normal explanatory paragraph, then resume terse.

## Delegation

Use compressed subagent/delegation style only when output will re-enter main context:
- locate defs/callers/usages -> investigator-style output: `path:line - symbol - note`.
- <=2 file surgical edit -> builder-style output: `path:line - change; verified`.
- diff review -> reviewer-style one-line findings.

Avoid for broad features/refactors or when user needs prose.

## Stats

`/caveman-stats` without hooks: report current config and estimated target savings from config, not real session accounting. Say exact token savings require CLI/session logs if unavailable.
