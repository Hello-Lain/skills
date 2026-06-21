# Reviewer Lite Gate Integration

Use this when a user asks to insert `reviewer` into another skill or replace a skill-local review step with `reviewer`.

## Purpose

Keep review semantics in `reviewer`. Consumer skills should define artifact boundaries, build compact packets, consume verdicts, and preserve their own domain gates.

## When To Insert

- Before an artifact becomes authoritative for a downstream skill.
- After the producing skill has satisfied its own mandatory gate.
- After deterministic validators have run when the artifact has validators.
- Before final handoff, execution acceptance, or save-ready reporting.

Do not insert reviewer lite before required user confirmation, before required inputs exist, or in place of tests, validators, migrations, security review, production readiness, or real execution evidence.

## Replacement Rule

When replacing a skill-local review step:

1. Keep the producing skill's domain checks.
2. Remove duplicated reviewer rubrics, report templates, and severity rules from the consumer.
3. Add a short hook that points here and names the artifact boundary.
4. Preserve validator and user-confirmation gates as hard gates.

## Minimal Packet

Consumer skills pass only what the review needs:

- Source goal and latest user constraints.
- Artifact type, stage, path or compact content.
- Producing skill contract and directly relevant references.
- Validators already run, skipped checks with reasons, and allowed commands.
- Requested route, usually `lite`, plus focus options.
- Required verdict handling contract.

## Route Contract

- Start with `reviewer` route preflight.
- Use `lite` only for small, local, low-risk artifacts with clear authority.
- Escalate to `heavy` for material workflow changes, safety gates, execution/planning acceptance, data/security/privacy impact, unclear source authority, prior failed review, or explicit isolation requests.
- Return `BLOCK` when required evidence is missing or review conditions are unsafe.

## Verdict Handling

- `PASS`: continue the consumer workflow.
- `REVISE`: apply evidence-backed revisions inside the consumer's writable scope, then request a focused recheck.
- `BLOCK`: stop immediately and report the blocker; do not self-repair.

For this lite-gate integration, a consumer may attempt at most three total self-repair cycles after `REVISE`. If the third cycle still does not reach `PASS`, stop and treat the failure as a reviewer guidance issue, upstream contract ambiguity, or source requirement conflict. This integration cap does not change `reviewer`'s default recheck loop outside consumer-owned lite gates.

## Consumer Responsibilities

- Do not copy full reviewer rubrics or the report template into the consumer skill.
- Do not weaken the producing skill's own gates.
- Verify reviewer findings before applying them; push back with source evidence when feedback is unsupported.
- Record skipped validators, route escalation, rework cycles, and remaining risks in the consumer's artifact or final report.
- Keep raw transcripts, large diffs, and logs in artifacts rather than active context.

## Common Boundaries

- `idea-refine`: after the mandatory exit gate passes and before final direction artifact acceptance or save handoff.
- `interview-me`: after explicit user approval and spec quality checks, before treating `spec.md` as downstream-ready.
- `spec2plan`: after plan contract validation, before reporting `plan.md` as handoff-ready.
- `plan2do`: after task verification evidence exists, before final completion reporting.
