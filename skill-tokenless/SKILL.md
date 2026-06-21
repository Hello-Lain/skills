---
name: skill-tokenless
description: "Use when reducing Codex skill token cost, shrinking SKILL.md, moving rare detail to references, shortening agents/openai.yaml, or auditing a skill for bloat without behavior loss."
---

# Skill Tokenless

Shrink a Codex skill without changing what it can do.

## Contract

- Preserve behavior: triggers, exclusions, workflow, safety gates, approvals, validation, scripts, assets, output quality.
- Do not remove required detail because it is verbose; compress it, route it to `references/`, or keep it.
- Keep `SKILL.md` as the always-loaded entrypoint; put conditional, long, rare, subagent-only, schema, API, example, and validation detail in one-level `references/`.
- Keep discovery strong: frontmatter says when to use only; do not hide trigger keywords only in references.
- Do not edit scripts unless docs are stale against script behavior.
- Do not delete user edits or unrelated dirty files.

## With Skill Creator

After `$skill-creator` drafts or updates a skill, run this as the final design pass before validation. Preserve all `skill-creator` requirements: valid frontmatter, required `SKILL.md`, recommended `agents/openai.yaml`, useful resource dirs, and `quick_validate.py`.

## Workflow

1. Inspect: target `SKILL.md`, `agents/openai.yaml`, references, scripts, `git status`, line counts, word counts.
2. Behavior Lock: capture triggers/exclusions, workflow, tools, scripts, approvals, validation, output schema, safety/security, fallbacks. Use `references/validation.md` for the full checklist.
3. RED before material edits: for new or materially changed skills, prove the current/unguided version fails or wastes context; include a description shortcut probe when metadata changes. Use `references/testing.md`.
4. Find waste: repeated purpose text, long examples, tables, subagent-only blocks, rare API/debug detail, duplicated schemas/templates, verbose prompts.
5. Rewrite:
   - frontmatter: trigger conditions only, concise, searchable; no workflow summary.
   - body: contract, routing, workflow, gates, validation summary.
   - references: detailed contracts, scenario probes, schemas, templates, API notes, examples.
   - `agents/openai.yaml`: short `short_description`; one-sentence `default_prompt` mentioning `$skill-name`.
6. GREEN/REFACTOR for material edits: run scenario or micro-tests from `references/testing.md`; patch real failures; retest once or record blocker.
7. Validate: run `quick_validate.py`, counts, grep gates, explicit cleanup command, diff review. Use `references/validation.md`.
8. Report: changed files, line/word delta, preserved gates, RED/GREEN or Scenario Gate result, skipped RED reason if any, validation result, residual risks.

## Compression Patterns

- Replace prose with imperative bullets.
- Keep one excellent example; move extra examples to references.
- Prefer "read `references/x.md` when..." over embedding rare detail.
- Replace broad tables with compact bullets unless exact columns matter.
- Remove duplicate "when to use" body text if frontmatter covers it.
- Keep command names, script paths, and hard gates exact.
- Use recipes/contracts for output-shape problems; use prohibitions only for rule-skipping/rationalization problems.

## Required References

- Read `references/testing.md` before creating, materially changing, or pressure-testing a skill.
- Read `references/validation.md` before editing and before final reporting.

## Hard Stops

- Stop if target behavior is unclear and no local evidence can recover it.
- Stop before deleting/moving large resources unless explicitly requested.
- Stop if validation fails after one repair attempt.
- Do not run live-system, costly, secret-bearing, long-running, or user-data forward tests; use a mock/dry-run fixture or report the blocker.
