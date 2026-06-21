# Tokenless Skill Testing

Load when creating, materially changing, or pressure-testing a skill.

## Principle

Tokenless work is TDD for process docs: RED proves current guidance fails or wastes context, GREEN makes the smallest safe edit, REFACTOR closes loopholes without adding bloat.

## When Required

- New skill.
- Material rewrite of `SKILL.md`, trigger text, gates, workflow, validation, or prompt.
- Moving required behavior into references.
- Any change that could make an agent skip a required step.

Skip only for typo-only edits or pure formatting that cannot change behavior; still run validator and counts.

## RED

Before editing, create a small probe that can fail:

- Baseline: current skill, no skill, or old wording.
- Task: realistic request that tempts bloat, behavior deletion, skipped validation, or reference overloading.
- Capture: exact failure, rationalization, missed gate, token waste, or ambiguous wording.

If the control does not fail and no waste is observable, do not add guidance for that issue.

## Probe Templates

Use the smallest probe set that matches the edit:

- Trigger probe: a matching user request must select the skill.
- Non-trigger probe: an adjacent but out-of-scope request must not select it.
- Reference-loading probe: a task needing one reference/script loads only that resource.
- Validation-skip probe: a tempting success path still runs validators or records a blocker.
- Description shortcut probe: metadata-only reading must not imply workflow steps; `description` names triggers/exclusions, not process.
- Context-waste probe: baseline loads duplicated examples, schemas, prompts, or rare debug detail that the patch routes out of always-loaded context.

## GREEN

Patch the smallest wording/structure that addresses the observed failure:

- Rule-skipping/rationalization failure -> explicit prohibition plus counter.
- Wrong output shape -> positive recipe/contract, not a list of "don't" rules.
- Missing required element -> required field in the checklist/template.
- Conditional behavior -> observable predicate, not vague nuance.

## REFACTOR

Retest the same probe or a close variant once. If the agent finds a new loophole, patch the specific loophole and retest. If live systems, secrets, user data, cost, or long runtime are involved, use a mock fixture and record the blocker.

## Micro-Tests

Use before adding broad guidance or changing high-impact wording:

1. Include a no-guidance control.
2. Run 5+ fresh-context samples per variant when tooling allows.
3. Use realistic system context: full skill/prompt location, not isolated wording.
4. Manually read flagged matches; template echoes can look like failures.
5. Prefer wording that converges to one output shape with low variance.

## Scenario Gate

Goal: prove the skill works in a messy task, not just schema validation.

PASS requires:

- Skill triggers for a matching scenario and avoids an obvious non-scenario.
- Required references/scripts are loaded only when needed.
- Output matches the declared schema/format.
- Validation commands run or a concrete blocker is recorded.
- Agent does not ask avoidable questions, skip gates, or load broad unnecessary context.
- Temporary fixtures, generated outputs, indexes, logs, and scratch files are removed.
- Discovered failures are patched, retested, or listed as residual risk.

## Fixture Design

- Prefer `tmpdir="$(mktemp -d)"`; if the task needs the skill path, use `<skill-dir>/.tmp-forward-test/`.
- Include 3-7 files, one ambiguity/edge case, one path that should load a reference/script, and one validation command.
- Model realistic failures: stale config, similar names, missing fields, partial data, fallback path, malformed input, conflicting docs.
- Keep fixtures small and isolated.
- Do not touch production data, secrets, expensive APIs, or live services.
- Use subagents only when available and useful; pass the skill plus fixture, not expected answers.

## Rationalization Log

Record concise evidence:

- Scenario:
- Baseline/control result:
- Failure or waste:
- Exact rationalization:
- Patch made:
- Retest result:
- Residual risk:
