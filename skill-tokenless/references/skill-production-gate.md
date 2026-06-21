# Skill Production Gate

Use this contract for every new skill, material skill update, validator/script change, workflow/safety change, or skill metadata change that can affect triggering or execution quality.

The gate is a production acceptance layer, not only a token-reduction pass.

## When Required

- New skill.
- Material update to `SKILL.md`, `agents/openai.yaml`, `references/`, scripts, triggers, workflow, output schema, validation, safety, or subagent routing.
- Validator, compiler, report-schema, or reviewer-gate script changes.
- Any change that could make an agent skip a required step or accept weak output.

Skip only for typo-only or formatting-only edits that cannot change behavior. Still run `quick_validate.py`, counts, cleanup check, and diff review.

## Required Phases

1. Behavior Lock:
   - Record triggers, exclusions, workflow, tools, scripts, subagents, user gates, safety constraints, output schema, validators, and fallback behavior that must survive.
2. Token Budget:
   - Record `SKILL.md` line/word delta and which detail moved to `references/`.
3. Deterministic Validators:
   - Run `quick_validate.py`.
   - Run changed script self-tests.
   - Run domain validators such as reviewer, plan, execution, schema, lint, or smoke checks when applicable.
4. Scenario Gate:
   - Run a RED/GREEN, mock forward test, or documented scenario probe for material changes.
   - If skipped, state why the change cannot affect behavior.
5. Reviewer Gate:
   - Before launch, validate the report as draft: `python3 skill-tokenless/scripts/validate_skill_production.py <production-report.md> --root <repo> --stage draft`.
   - Before launch, run readiness when execution state exists: `python3 plan2do/scripts/pre_review_ready.py <plan-workspace> --stage draft --require-production-report --require-final-report`.
   - Use `reviewer` for the final artifact.
   - Use `lite` only when the change is small, local, low-risk, and deterministic validators cover the risk.
   - Use heavy subagent review for new skills, material workflow changes, validators, safety gates, execution/planning routes, or prior failures.
6. Cleanup Proof:
   - Record subagent cleanup as `archive`, `kill`, `not launched`, or `unavailable with reason`.
   - Record temp fixture cleanup.
7. Production Report:
   - Save a draft production report before reviewer launch.
   - Update the report after reviewer completion.
   - Validate final report with `skill-tokenless/scripts/validate_skill_production.py <production-report.md> --root <repo> --stage final`.

## Draft / Final Lifecycle

- `draft`: allowed before reviewer runs. Reviewer Gate `Verdict` may be `PENDING` or omitted only when cleanup records `not launched` or `unavailable`.
- `final`: required before final success. Reviewer Gate `Verdict` must be `PASS`, `REVISE`, or `BLOCK`.
- A `PASS` final production report requires reviewer `PASS` and cannot include reviewer `REVISE` or `BLOCK`.
- Both stages require Behavior Lock, Token Budget, Deterministic Validators, Scenario Gate, Reviewer Gate, Reuse Attribution, Changed Files, and Residual Risks.

## Reviewer Subagent Health Policy

For heavy or mandatory-isolation reviewer subagents:

- Poll only when the subagent appears abnormal: stalled status, no new activity, permission/tooling/network anomaly, ambiguous status API, scope drift, rule violation, or loop signals.
- For abnormal diagnosis, poll exactly 2 times; each poll waits 45 seconds.
- If the reviewer is `running` with new activity or plausible progress, keep waiting. Do not cancel, archive, block, relaunch, or downgrade solely because two 45-second waits elapsed.
- Do not downgrade to inline review solely because of wait time, likely provider fluctuation, or temporary network interruption.
- If the reviewer remains abnormal after both diagnostic polls, keep partial raw output out of context, then either:
  - return `BLOCK` with evidence and cleanup status; or
  - cancel and relaunch once with a narrower packet after cleanup, when that is safer than blocking.
- Archive or kill the reviewer subagent after report collection, explicit cancel, or confirmed failure when tooling supports it.

## Reuse Attribution

Every production report for skill workflow changes must include a reuse matrix.

| Source | URL | Borrowed idea | Component | Adoption | Target change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- |

Adoption values:

- `direct`: a local optional CLI/library/script can be used as-is.
- `adapted`: the pattern is implemented in local docs/scripts.
- `pattern-only`: the idea informs behavior, no dependency added.
- `rejected`: inspected and explicitly not used.

Known source patterns:

- `https://github.com/obra/superpowers`: subagent-per-task, review after task, final review, file handoffs, progress ledger.
- `https://github.com/plandex-ai/plandex`: pending/cumulative diff review before applying generated changes.
- `https://github.com/Aider-AI/aider`: repo map plus edit/test feedback loop.
- `https://github.com/pre-commit/pre-commit`: deterministic hook-style quality gates.
- `https://github.com/ast-grep/ast-grep`: AST-aware search/rewrite for repeated code edits.
- `https://github.com/openrewrite/rewrite`: recipe/dry-run large rewrite discipline.
- `https://github.com/NousResearch/hermes-agent-self-evolution`: dataset, constraints, fitness, promotion gates.

## Production Report Template

```markdown
# Skill Production Report

- Skill: <skill name or path>
- Change Type: <new-skill|material-update|validator-script|metadata-update|minor-update>
- Verdict: <PASS|BLOCK>

## Behavior Lock
- Preserved:
- Changed intentionally:
- Fallbacks:

## Token Budget
- Before:
- After:
- Moved to references:

## Deterministic Validators
- `<command>`: <PASS|BLOCK|SKIPPED with reason>

## Scenario Gate
- Scenario:
- RED/control:
- GREEN/retest:
- Cleanup:

## Reviewer Gate
- Mode:
- Route:
- Verdict:
- Report:
- Cleanup:

## Reuse Attribution
| Source | URL | Borrowed idea | Component | Adoption | Target change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- |

## Changed Files
- <path>

## Residual Risks
- <risk or None known>
```

## Validation

```bash
python3 skill-tokenless/scripts/validate_skill_production.py <production-report.md> --root /data/lcq/.codex/skills --stage draft
python3 skill-tokenless/scripts/validate_skill_production.py <production-report.md> --root /data/lcq/.codex/skills --stage final
python3 skill-tokenless/scripts/validate_skill_production.py --self-test
```

Passing the validator is not sufficient by itself. The coordinator must still inspect evidence, changed files, reviewer findings, and relevant command outcomes.
