---
name: reviewer
description: General-purpose artifact quality review with lite/heavy routing, isolated critique, report validation, evidence receipts, source checks, subagent cleanup, and PASS/REVISE/BLOCK verdicts. Use when Codex needs to review, audit, critique, revise, or quality-gate a produced artifact such as an idea, spec, plan, implementation result, code diff, documentation, research idea, skill output, or workflow handoff; especially when checking alignment with source goals, local rules, skill contracts, tests, validators, feasibility, correctness, or readiness before accepting or acting on the artifact.
---

# Reviewer

Review artifacts on demand. Use the cheapest safe route first, but do not weaken quality gates for risky artifacts.

Core rule:

```text
Review from evidence, not vibes. Treat the artifact as a candidate, optimize for the source goal over preserving the presented design, run preflight, choose lite/heavy/blocked, derive the rubric, complete bounded issue discovery, then issue exactly one top-level verdict: PASS, REVISE, or BLOCK.
```

## Workflow

1. Identify artifact, source goal, expected stage, artifact type, requested options, and obvious risk signals.
2. Run route preflight before broad context loading or subagent launch.
3. Rehydrate source evidence in order: latest user goal, applicable `AGENTS.md`, upstream artifact, relevant `SKILL.md` and linked contracts, current files/tests/commands needed to judge material claims, readiness evidence when reviewing plan2do/skill-production results, then external sources only when current/niche/high-stakes or requested.
4. Build a compact review packet with goal, stage, artifact path/content, source list, constraints, validators, allowed commands, requested focus/options, and route.
5. Derive rubric before findings.
6. Reconstruct the source goal in your own words and audit artifact framing for bias, incompleteness, misplaced optimization, or polished but weakly grounded claims.
7. Run bounded issue discovery before deciding: scan every material rubric surface available in the selected route, record all discovered critical/major findings, separate direct evidence from inference when material, then decide whether convergence, escalation, or `BLOCK` is justified.
8. Review source alignment and intrinsic quality separately.
9. Return the v2 report shape from `references/review-report-template.md`.
10. Validate saved reports with `python3 reviewer/scripts/validate_review_report.py <report.md>`.

Finding one obvious issue is not enough to stop the first pass. Continue through the remaining high-value risk surfaces unless evidence is missing, the route must escalate, a requested cap applies only to minor/nit output, or review conditions require `BLOCK`.

## Route Preflight

Classify route as `lite`, `heavy`, or `blocked` and state one reason.

- `lite`: artifact is small, local, low-risk, source authority is obvious, and no behavior/security/data/research/plan/execution acceptance risk is material.
- `heavy`: artifact is non-trivial or risky, including code behavior, security/privacy/data, research novelty, spec/plan/execution acceptance, cross-file impact, adversarial review, failed prior review, unclear source authority, or explicit isolated review request.
- `blocked`: required evidence or mandatory isolation is unavailable, source authority conflicts, or review conditions are unsafe.

Lite reviews stay inline by default and avoid broad file reads. Heavy reviews default to an isolated reviewer subagent when tooling is available; inline heavy requires an explicit fallback reason in `Mode Decision`. Harness policy forbidding subagent spawn without explicit delegation is a valid inline-heavy fallback reason unless `mandatory-isolation` was requested. A transient subagent wait, provider fluctuation, or temporary network interruption is not a valid inline fallback reason while the subagent is still healthy or making progress. If `mandatory-isolation` is requested, run even a lite packet in a reviewer subagent when tooling is available; return `BLOCK` if mandatory isolation cannot be satisfied.

Every report must include `Review Mode` and `Review Route`.

## Lite Gate Integration

When another skill needs to insert `reviewer` or replace a local review step with `reviewer`, read `references/lite-gate-integration.md`. Keep consumer skills thin: they choose the artifact boundary, pass a compact packet, preserve their own validators and user gates, then consume `PASS`, `REVISE`, or `BLOCK` without copying reviewer rubrics.

## Subagent Default

For heavy reviews, send only the review packet to the reviewer subagent. Do not pass the full main-thread conversation, irrelevant private context, raw transcripts, hidden conclusions, or the intended verdict.

The main agent coordinates only:

- assemble packet;
- confirm `plan2do/scripts/pre_review_ready.py <plan-workspace> --stage draft --require-production-report --require-final-report` passed before final reviewer launch when the packet reviews skill-production execution artifacts, or record a deliberate partial-review reason;
- launch reviewer when route requires it;
- receive synthesized report;
- validate saved report with `reviewer/scripts/validate_review_report.py`;
- poll only when the reviewer subagent has a suspected problem: stalled status, no new activity, permission/tooling/network anomaly, status API ambiguity, or loop signals;
- when abnormal, poll exactly 2 times, 45 seconds per poll, to diagnose health before deciding;
- if still abnormal after diagnostic polls, return `BLOCK` or relaunch once with a narrower packet after cleanup; do not downgrade to inline review solely because of wait time or likely provider/network fluctuation;
- cancel and archive or kill the reviewer subagent only if it is confirmed stuck, failed, out of scope, looping, violating read-only/no-nested rules, explicitly stopped by the user, or completed and ready for cleanup;
- archive or kill the reviewer subagent after collecting the report when the current tool supports cleanup;
- present results without silently changing the reviewer verdict.

Reviewer subagents must stay read-only and must not spawn nested reviewer subagents. For broad high-risk reviews, use multiple specialized reviewer subagents only when the packet justifies the cost. Record cleanup status in `Review Basis` or `Residual Risks` when a subagent was launched.

If you are already running inside a reviewer subagent, do not apply the heavy-review default by launching another reviewer. Treat the received packet as the isolated review context, complete the review in the current agent, and record `Review Route: subagent`.

Read `references/subagent-dispatch.md` before dispatching any reviewer subagent or explaining fallback/cleanup.

## Review Options

Honor explicit user options before generic rubric breadth:

- `focus`: prioritize named axes such as correctness, spec compliance, security, feasibility, novelty, tests, effort, split-ability, or handoff risk.
- `max_findings`: cap reported findings after all critical issues; never hide critical findings to satisfy a cap.
- `adversarial`: run try-to-break-it checks in addition to normal review.
- `save-review`: write the report to the requested path.
- `no-commands`: avoid commands and state skipped executable checks.
- `mandatory-isolation`: require subagent isolation even for a lite packet; return `BLOCK` if unavailable.

If an option is unsafe, unsupported, or conflicts with source authority, state that in `Review Basis` and adjust the verdict if the missing option blocks judgment.

## Verdicts

Use exactly one top-level verdict:

- `PASS`: no critical or major findings; minor items may remain.
- `REVISE`: at least one major finding, or several minor findings that reduce usability.
- `BLOCK`: at least one critical finding, missing evidence required for judgment, unsafe review conditions, or artifact cannot be reviewed reliably.

A `PASS` requires convergence: state in `Residual Risks` or `Recheck Plan` which major surfaces were checked, what route-limited uncertainty remains, and why no known critical or major findings remain. `REVISE` and `BLOCK` must include all known critical/major findings discovered during the bounded pass, not only the first one.

Severity:

- `critical`: unsafe, misleading, unexecutable, directionally wrong, or source contract violation that invalidates the artifact.
- `major`: important requirement, evidence, quality gate, or acceptance criterion failure.
- `minor`: usable artifact with a concrete improvement needed.
- `nit`: optional polish; never blocks.

Route each critical or major finding to one fix type: patch current artifact, revise upstream artifact, rerun upstream skill, ask user, or stop as unsafe/unsupported.

## Adversarial Mode

Use adversarial mode when requested, when reviewing plans/code/research ideas with high ambiguity or risk, or when normal review would likely be confirmatory.

Try to falsify the artifact before returning `PASS`:

- plans: commands, environment activation, dependencies, paths, ordering, writable scopes, rollback, handoff, and hidden approval needs;
- code: behavior regressions, boundary inputs, concurrency/state leaks, security/privacy exposure, missing tests, and config drift;
- research ideas: feasibility, novelty claims, baseline choice, data availability, evaluation signal, cost, and invalidating evidence;
- specs/docs: ambiguous terms, missing non-goals, untestable criteria, audience mismatch, and source conflicts.

Report adversarial findings as normal findings with evidence. If no issue is found, say which attack surfaces were checked in `Residual Risks` or `Recheck Plan`.

## Recheck Loop

After `REVISE`, the consumer may patch or rerun the upstream skill, then ask for one focused recheck. Inspect changed evidence plus original critical/major findings, and widen again only when the new diff expands scope or introduces a new material risk surface. Stop after two unresolved cycles with `BLOCK` or explicit user decision.

## Rubric Routing

Use live contracts over copied memory. For known skill artifacts, read the producing skill's `SKILL.md` and only directly relevant references.

- `idea-refine`: check target user, success criteria, variations, clusters, stress-tests, assumptions, MVP, Not Doing list, and save/confirmation gates.
- `interview-me`: check explicit confirmation, user, why, success, constraints, scope, non-goals, assumptions, and acceptance checks.
- `spec2plan`: check plan contract, implementation map, executable tasks, dependencies, writable scopes, verification, rollback, risks, and self-review.
- `plan2do`: check task completion evidence, verification, review verdict, rework handling, artifacts, and false-completion risk.
- `skill-creator`: check skill naming, frontmatter trigger quality, concise body, direct references, `agents/openai.yaml`, validation, and forward-test suitability.

For generic domains, read `references/review-rubrics.md`.

## Validators

Prefer executable evidence when available and safe:

- reviewer report validation with `python3 reviewer/scripts/validate_review_report.py <report.md>`;
- skill validation, plan validation, execution validation;
- test, lint, type, schema, or smoke commands named by the artifact;
- project-owned validators or acceptance checks.

Do not treat "tests passed" as sufficient. Still check source alignment, edge cases, missing evidence, hidden debt, and over/under-building.

For local path evidence, verify cited paths exist before treating them as evidence. If a path is missing, label it as missing/unavailable and adjust the verdict when that evidence is required.

## Feedback Validity

Reviewer output is not authority by itself. Consumers should verify evidence before applying feedback.

- Apply critical/major findings when evidence is sound and source authority supports them.
- Push back on wrong or stale feedback with file paths, commands, or contract text.
- Downgrade unsupported findings to residual risks or questions.
- Ask the user when fixing a valid finding requires a product, research, safety, or scope decision.

## Output

Read `references/review-report-template.md` before writing the final report. The report must include artifact type, confidence, review mode, review route, review basis, rubric, mode decision, alignment result, quality result, top-level verdict, evidence-backed findings, revision instructions, recheck plan, and residual risks.

Keep findings concise. Prioritize correctness, feasibility, alignment, and actionable rework over style preferences.

## Safety

- Review mode is read-only. Do not edit artifacts, branch state, index state, config, or generated outputs unless the user separately asks for implementation.
- Lite mode is not permission to ignore risk; escalate to heavy or `BLOCK` when source authority or impact is unclear.
- Treat summaries, old plans, previous reviews, generated docs, and logs as navigation, not authority.
- If evidence conflicts, return `BLOCK` or `REVISE` with the conflict and required source.
- If a finding depends on inference rather than direct evidence, label it and advise verification before applying the feedback.
