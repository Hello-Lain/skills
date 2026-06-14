---
name: plan-grill
description: "Use when planning production-sensitive engineering work and the plan should be stress-tested before execution. Combines concise planning with grill-me-style critique: draft a plan, ask the highest-leverage challenge questions, revise the plan, then execute only after the plan is defensible or the user approves. Trigger for deployments, migrations, auth, data, DB, CI/CD, infra, dependency upgrades, refactors, security-sensitive changes, and uncertain blast radius."
metadata:
  short-description: "Plan, stress-test, revise, then execute"
---

# Plan Grill

Use this skill to make planning safer and less naive for production work.

Default workflow:

```text
Draft plan -> grill plan -> revise plan -> execute
```

This skill does not replace implementation. It adds a short, high-signal pressure test before acting.

## When To Use

Use automatically for:

- Production deployments or release plans.
- Database/schema/data migrations.
- Auth, permissions, secrets, payment, billing, or security changes.
- CI/CD, infra, config, container, networking, observability, or rollback changes.
- Dependency upgrades with runtime risk.
- Refactors with unclear blast radius.
- Work touching user data or destructive writes.
- User asks for "plan", "design", "migration", "rollout", "architecture", "safe", "production", "review my approach", or "think first".

Do not use automatically for:

- Typos.
- Tiny local style edits.
- Single-file obvious fixes.
- User explicitly says "just do it" and the blast radius is low.
- Pure explanation questions.

## Core Protocol

1. Inspect local evidence first.
2. Draft a concise plan.
3. Grill the plan with 3-7 questions.
4. Revise the plan using answers/evidence.
5. Execute only when safe enough or user approves.
6. Validate and report result.

## Evidence First

Before drafting, inspect relevant local context:

- Code paths likely touched.
- Tests for those paths.
- Config/env/deploy files.
- Existing docs/runbooks/ADRs.
- Recent git diff/status.
- Logs or scripts if available.

If evidence is missing but discoverable, search. If not discoverable and risky, ask.

## Draft Plan Format

Keep it short:

```text
Plan:
1. ...
2. ...
3. ...

Assumptions:
- ...

Validation:
- ...

Rollback:
- ...
```

Include rollback for production-sensitive work. If rollback is impossible, say so explicitly.

## Grill Pass

Ask only the highest-leverage questions. Prefer 3, max 7 unless the user requests hard mode.

Use this format:

```text
Question: ...
Recommended answer: ...
Why it matters: ...
```

Question priority:

1. What assumption would break the plan?
2. What is the blast radius?
3. What fails silently?
4. How is success observed?
5. How is rollback/recovery done?
6. What data/security risk exists?
7. What is the smallest safe rollout?

For simple tasks, ask zero or one grill question and continue.

## Revision

After the grill pass, revise the plan:

```text
Revised plan:
1. ...
2. ...
3. ...

Changes from grill:
- ...
```

If user answers are needed, wait. If local evidence answers the grill questions, continue without waiting.

## Execution Gate

Proceed without further confirmation when:

- The user already asked Codex to implement.
- Risk is low or mitigated.
- Rollback/validation are clear.
- No destructive external action is needed.

Ask before executing when:

- Destructive action is involved.
- Production credentials, deploys, or live data are involved.
- Rollback is weak.
- Requirements conflict.
- User explicitly asked only for planning.

## Production Defaults

- Prefer feature flags, staged rollout, backups, and small blast radius.
- Prefer boring, observable changes.
- Do not accept "tests pass" as runtime proof for deploy-impacting behavior.
- Require a smoke check for deploy/runtime changes.
- Require regression tests for bug fixes when practical.
- Require data backup or reversible migration for schema/data changes.
- Require secret/config review when env vars or credentials are touched.

## Final Report

When done:

- State implemented result first.
- List changed files.
- List validation run and outcome.
- List unresolved risks.
- Suggest next step only if useful.

## Delegation

If `$grill-me` is available, use its style and question format. Do not require the user to invoke it separately.
