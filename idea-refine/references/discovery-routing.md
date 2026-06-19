# Discovery Routing

Keep this file byte-identical across `idea-refine`, `interview-me`, and `spec2plan`.

## Purpose

Discovery Routing prevents premature specs, premature plans, and loops between discovery skills.

Use this route:

```text
Idea or direction uncertainty -> idea-refine
Confirmed direction with missing requirements -> interview-me
Confirmed spec needing execution plan -> spec2plan
```

## Skill Roles

- `idea-refine`: explore, compare, stress-test, and choose a product or solution direction.
- `interview-me`: turn a chosen direction into a confirmed implementation-ready spec.
- `spec2plan`: turn a confirmed spec or equivalent clear requirements into an executable plan.

## Route Signals

Route to idea-refine when:

- The user has an idea but is unsure it is the right thing to build.
- Multiple possible directions, products, architectures, or workflows are competing.
- The request asks to ideate, refine, stress-test, compare options, or find a better direction.
- The current solution seems premature, overfit, weakly motivated, or missing a clear success model.

Route to interview-me when:

- A direction has been chosen but requirements remain incomplete.
- Success criteria, users, scope, constraints, risks, data, integrations, or non-goals are unclear.
- The user wants to be interviewed, grilled, or questioned before implementation.
- The next artifact should be a confirmed `spec`, not an execution plan.

Route to spec2plan when:

- A confirmed spec exists.
- Requirements are clear enough that planning does not require inventing major product decisions.
- The user asks for implementation sequencing, task breakdown, worker waves, validation, or rollout planning.
- The next artifact should be an executable `plan`.

## Entry Criteria

`idea-refine` may start from a vague idea, rough concept, concern, option set, or weak solution guess.

`interview-me` should start from a selected direction. If the direction is not selected, route to `idea-refine` first.

`spec2plan` should start from a confirmed spec or equivalent clear requirements. If only a raw idea or unconfirmed direction exists, route upstream before planning.

## Exit Criteria

`idea-refine` exits with:

- Recommended direction.
- Rejected alternatives or tradeoffs.
- Key assumptions and risks.
- Enough context for `interview-me` to ask requirement questions.

`interview-me` exits with:

- Confirmed spec.
- Explicit scope and non-goals.
- Success criteria and constraints.
- Enough detail for `spec2plan` to produce tasks without inventing requirements.

`spec2plan` exits with:

- Executable plan.
- Task sequence, dependencies, validation, risks, rollback, and ownership.
- No unresolved product-direction or spec-quality gaps hidden as implementation assumptions.

## Avoid Loops

- Route only one step upstream at a time unless the user explicitly requests a full restart.
- Do not bounce repeatedly between two skills. After one upstream route, ask the user to confirm the next handoff.
- Do not use a downstream skill to fill upstream gaps. `spec2plan` must not invent specs; `interview-me` must not choose strategy when the direction is untrusted.
- Do not create a full spec in `idea-refine`; ask only the minimum interview-style questions needed to choose a direction.
- Do not create an execution plan in `interview-me`; stop after the spec is confirmed unless the user asks for planning.
- If the user explicitly chooses to proceed despite uncertainty, record assumptions and continue in the requested skill.

## Handoff Contract

When handing off, state:

- Current artifact maturity: `idea`, `direction`, `spec`, or `plan`.
- Why the current skill should stop.
- Which skill should run next.
- What artifact the next skill should produce.
- Any assumptions, risks, or open questions that must carry forward.
