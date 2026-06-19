---
name: skill-tokenless
description: "Use when optimizing any Codex skill for lower token/context cost while preserving original behavior, triggers, safety gates, validation, scripts, and practical output quality. Also use proactively during $skill-creator workflows, before final validation, to make newly created or updated skills efficient by default. Refactor verbose SKILL.md bodies into concise entrypoints, move conditional details to references, shorten agents/openai.yaml prompts, normalize structure, and validate that the skill still works."
---

# Skill Tokenless

Shrink another skill without changing what it can do.

## Skill Creator Integration

When `$skill-creator` creates or updates a skill, run this skill as a final design pass before final validation:

- Draft or update the skill normally with `$skill-creator` first.
- Then apply tokenless review to keep `SKILL.md` lean from the start.
- Treat this as a companion optimization layer, not a replacement for `skill-creator`.
- Preserve all `skill-creator` requirements: valid frontmatter, required `SKILL.md`, recommended `agents/openai.yaml`, resource directories only when useful, and `quick_validate.py`.
- Prefer designing progressive disclosure up front instead of compressing after the skill becomes bloated.
- Do not block necessary domain detail; move it to references and link it clearly.

## Non-Negotiables

- Preserve original function, trigger intent, safety gates, validation commands, scripts, assets, and output quality.
- Do not remove behavior because it looks verbose; compress, move to reference, or summarize with exact gates.
- Do not edit scripts unless token work reveals dead docs pointing to wrong script behavior.
- Do not delete user edits or unrelated dirty files.
- Keep `SKILL.md` as the small always-loaded entrypoint.
- Put conditional, long, rare, or subagent-only detail in one-level `references/` files.
- Run the skill validator after changes.
- For created or materially changed skills, run a realistic scenario gate unless blocked by live-system risk; clean all temporary files afterward.

## Workflow

1. Inspect the target skill: `SKILL.md`, `agents/openai.yaml`, references, scripts, current `git status`, and line/word counts.
2. Lock behavior before editing:
   - triggers and exclusions
   - main workflow steps
   - required tools/scripts/commands
   - user-confirmation gates
   - validation/check commands
   - output schema/format
   - safety/security constraints
3. Identify waste:
   - repeated purpose/when-to-use sections
   - long examples or command blocks
   - tables that can become short bullets
   - subagent-only instructions in main `SKILL.md`
   - API/debug details always loaded but rarely needed
   - duplicated schemas/templates already enforced by scripts
   - verbose `default_prompt`
4. Rewrite:
   - frontmatter: concise but complete trigger description; no body-only trigger info.
   - body: core contract, routing, workflow, gates, validation, references.
   - references: detailed contracts, schemas, templates, API notes, examples loaded only when needed.
   - `agents/openai.yaml`: short `short_description` and one-sentence `default_prompt` mentioning `$skill-name`.
5. Run the Scenario Gate for new or materially changed skills:
   - create a bounded, realistic, complex fixture in `mktemp -d` or `<skill-dir>/.tmp-forward-test/`
   - include 3-7 files, one ambiguity/edge case, one path that should load a reference/script, and one validation command
   - use the skill to solve the scenario, watching trigger accuracy, resource loading, tool use, output format, questions asked, token bloat, and cleanup behavior
   - patch the skill for any real failure, then rerun the same scenario or a close variant once
   - delete the fixture and all outputs; verify no unrelated files remain
   - if live systems, secrets, cost, long runtime, or user data are involved, use a dry-run/mock fixture or record the blocker instead
6. Validate and compare:
   - run `.system/skill-creator/scripts/quick_validate.py <skill-dir>`
   - for established dotted canonical IDs, run `.system/skill-creator/scripts/quick_validate.py --allow-dotted-name <skill-dir>`
   - compare line/word counts before/after
   - grep key gates from the new files
   - inspect diff for accidental behavior loss; if the skill dir is not in a git repo, use the fallback in Validation Commands
7. Report: files changed, token/line reduction, preserved gates, Scenario Gate result, validation result, residual risks.

## Scenario Gate

Goal: prove the skill works in a messy task, not just passes schema checks.

PASS requires:

- Skill triggers for the scenario and avoids triggering for an obvious non-scenario.
- Required references/scripts are used only when needed.
- Output matches the skill's declared schema/format.
- Validation commands run or a concrete blocker is recorded.
- The agent does not ask avoidable questions, skip required gates, or load broad unnecessary context.
- All temporary fixtures, generated outputs, indexes, logs, and scratch files are removed.
- Any discovered failure is patched, retested, or listed as residual risk.

Fixture design:

- Prefer `tmpdir="$(mktemp -d)"`; if the task needs the skill path, use `<skill-dir>/.tmp-forward-test/`.
- Model realistic failure modes: stale config, similar names, missing fields, partial data, fallback tool path, malformed input, or conflicting docs.
- Keep the fixture small enough for fast cleanup and large enough to exercise routing.
- Do not touch live services, secrets, production data, expensive APIs, or user-owned files.
- Use subagents only when available and useful; keep prompts generic and pass the skill plus fixture, not expected answers.

## Compression Patterns

- Replace long prose with imperative bullets.
- Keep only one quick command example if it materially helps execution.
- Move final-answer schemas, audit schemas, API specs, templates, and subagent contracts to references.
- Replace long pattern tables with a compact list unless exact columns matter.
- Prefer "read `references/x.md` when..." over embedding full detail.
- Remove duplicate "When to use" body sections if frontmatter already covers them.
- Keep script names and required commands exact.
- Keep validation gates explicit even if scripts enforce them.

## Behavior Preservation Checklist

Before finishing, confirm the new skill still states:

- When it triggers and when it must not trigger.
- Who performs each phase: main agent, subagent, script, user.
- What files/resources must be read and when.
- What commands must run and what passing means.
- What output artifacts must exist.
- What user approvals are required.
- What must never be copied into context, logs, commits, or final answers.
- What fallback happens when tools, auth, or subagents are unavailable.

## Validation Commands

```bash
python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>
# Use only for established external runtime IDs, e.g. Harness dotted canonical skills:
python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py --allow-dotted-name <skill-dir>
wc -l <skill-dir>/SKILL.md <skill-dir>/agents/openai.yaml
wc -w <skill-dir>/SKILL.md

# Scenario Gate cleanup/status:
test ! -e <skill-dir>/.tmp-forward-test
git -C <repo> status --short <skill-dir>

# Diff inspection:
# 1. If <skill-dir> is inside a git repo:
git -C <skill-dir> diff --stat -- .
git -C <skill-dir> diff -- SKILL.md agents/openai.yaml
# 2. If not, create backups before editing, then compare:
diff -u <skill-dir>/SKILL.md.before <skill-dir>/SKILL.md
diff -u <skill-dir>/agents/openai.yaml.before <skill-dir>/agents/openai.yaml
# 3. If no backup exists, use validator + counts + rg gate checks as the minimum fallback.
```

Default validator mode remains required for normal hyphen-case skills.
Use `rg` to verify key terms/gates survived.

## Hard Stops

- Stop if the target skill's behavior is unclear and no local evidence can recover it.
- Stop before deleting or moving large resources unless the user explicitly asked.
- Stop if validation fails after one repair attempt.
- Do not run live-system, costly, secret-bearing, long-running, or user-data forward tests; use a mock/dry-run fixture or report the blocker.
