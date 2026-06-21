# Tokenless Validation

Load before editing and before final reporting.

## Behavior Lock

Before editing, record what must survive:

- Triggers and exclusions.
- Discovery surface: frontmatter and UI metadata trigger the skill but do not encode workflow steps.
- Main workflow steps.
- Who performs each phase: main agent, subagent, script, user.
- Required files/resources and when to load them.
- Required tools, scripts, commands, and passing criteria.
- User-confirmation gates.
- Output schema/format and required artifacts.
- Safety/security constraints.
- What must never enter context, logs, commits, or final answers.
- Fallback when tools, auth, validators, or subagents are unavailable.

## Validation Commands

```bash
python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>
# Use only for established external runtime IDs, e.g. dotted canonical skills:
python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py --allow-dotted-name <skill-dir>
wc -l <skill-dir>/SKILL.md <skill-dir>/agents/openai.yaml
wc -w <skill-dir>/SKILL.md
rg "trigger|validation|quick_validate|Hard Stops|references/" <skill-dir>
rtk proxy bash -lc 'test ! -e "$1/.tmp-forward-test"' _ <skill-dir>
git -C <repo> status --short <skill-dir>
```

Default validator mode is required for normal hyphen-case skills.
Do not write cleanup checks as `rtk test ! -e ...`; `rtk test` is the RTK test-output filter, not the shell `test` builtin.

## Diff Inspection

If `<skill-dir>` is inside a git repo:

```bash
git -C <repo> diff --stat -- <skill-dir>
git -C <repo> diff -- <skill-dir>/SKILL.md <skill-dir>/agents/openai.yaml <skill-dir>/references
```

If not in a git repo, create backups before editing:

```bash
diff -u <skill-dir>/SKILL.md.before <skill-dir>/SKILL.md
diff -u <skill-dir>/agents/openai.yaml.before <skill-dir>/agents/openai.yaml
```

If no backup exists, minimum fallback is validator + counts + grep gate checks.

## Final Report

Include:

- Files changed.
- Line/word delta.
- Preserved gates.
- RED/GREEN, micro-test, or Scenario Gate result.
- Skipped RED reason, if no RED probe ran.
- Validator result.
- Cleanup result.
- Diff review summary.
- Residual risks.
