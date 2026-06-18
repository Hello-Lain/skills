---
name: interview-me
description: Interview users one question at a time to turn vague or conventional requests into a confirmed specification document before planning or coding. Use when an ask is underspecified ("build me X", "make it faster", "create a dashboard"), when who/why/success/constraints are unclear, or when the user explicitly asks to be interviewed, grilled, or have their thinking stress-tested.
---

# Interview Me

## Purpose

Extract what the user actually wants, then write a concrete spec. Do this before planning or coding when the request is ambiguous. The output is not just clarified intent; it is a reviewed spec that downstream skills can consume.

## Use / Do Not Use

Use when any of these are missing: target user, reason, success criteria, binding constraint, scope, non-goals.

Do not use for typo fixes, mechanical edits, pure explanations, or requests where the user explicitly chooses speed over clarification.

Requires a live user. In non-interactive/autonomous contexts, stop and report that requirements are underspecified instead of guessing.

## Workflow

### 1. Hypothesize

Start with one sentence and a confidence number:

```text
HYPOTHESIS: You want <outcome>, and "<requested artifact>" is probably just the first solution that came to mind.
CONFIDENCE: ~30% — missing: <who/why/success/constraint/scope>
```

If confidence is below 70%, include what is unresolved on the same line.

### 2. Interview One Question At A Time

Ask one focused question, always with your current guess:

```text
Q: <question>
GUESS: <likely answer + why you think so>
```

Wait for the answer before asking the next question. Do not batch questions. Update the hypothesis and confidence as answers arrive.

Probe "should want" answers. If the user gives best-practice or sophistication-signaling terms like "scalable", "modern", "clean", "robust", or "standard", ask:

```text
If you did not have to justify this to anyone, what would you actually want?
```

Stop interviewing only when you can predict the user's reaction to the next three questions. If several rounds do not raise confidence, say what foundational fact is still missing and ask whether to step back.

### 3. Restate Before Spec

When confidence is high, restate the intent in 5-8 lines:

```text
Here is what I think the spec should capture:

- Outcome: <one line>
- User: <who benefits>
- Why now: <trigger/context>
- Success: <measurable done condition>
- Constraint: <binding limit>
- Scope: <what is included>
- Out of scope: <what is explicitly excluded>

Explicit yes / refine?
```

Require an explicit yes before writing the final spec. "Whatever you think", "sounds good", or silence is not enough; offer concrete alternatives or ask what to refine.

### 4. Produce The Spec

Write a concise markdown spec. Include only details supported by the interview; mark unresolved items as open questions.

```markdown
# Spec: [Name]

## Objective
[What we are building, for whom, and why.]

## Users
[Primary/secondary users and their needs.]

## Problem
[Current pain, context, and why now.]

## Success Criteria
- [Specific, testable condition]
- [Specific, testable condition]

## Scope
### In
- [Included behavior/capability]

### Out
- [Explicit non-goal and why]

## Requirements
### Functional
- [User-visible behavior]

### Non-Functional
- [Performance, reliability, privacy, UX, compatibility, etc. Only include what matters.]

## Constraints
- [Time, tech, data, integration, budget, migration, team, policy.]

## Assumptions To Validate
- [ ] [Assumption] — [validation method]

## Risks
- [Risk] — [mitigation]

## Acceptance Checks
- [How the user/agent verifies done.]

## Open Questions
- [Question requiring user input before implementation.]
```

For codebase work, inspect relevant files before finalizing Commands, Project Structure, Testing Strategy, or integration constraints. Reference concrete paths when useful.

### 5. Confirm / Save / Hand Off

Ask the user to confirm the spec. If they approve and want persistence, save it to `docs/specs/[topic].md` or their chosen path. Do not save before confirmation.

After confirmation, downstream handoff:

- Use `idea-refine` if the spec exposes multiple possible product directions.
- Use `spec-driven-development` if the user wants the full gated SPECIFY -> PLAN -> TASKS -> IMPLEMENT process.
- Use `spec2plan` when the confirmed spec should become executable tasks.

## Quality Gates

Before finishing, verify:

- Hypothesis + confidence appeared before questions.
- Questions were one at a time and each included a guess.
- User, why, success, constraints, scope, and out-of-scope are explicit.
- Vague terms were converted into measurable criteria or open questions.
- Spec separates requirements, constraints, assumptions, risks, acceptance checks.
- User explicitly confirmed the restated intent before the final spec was treated as authoritative.
- No implementation plan or code was produced before spec confirmation.

## Red Flags

- Asking multiple questions in one message.
- Asking survey-style questions without a guess.
- Accepting "whatever you think" as approval.
- Writing implementation tasks before the spec is confirmed.
- Treating "dashboard", "AI agent", "clean architecture", or "make faster" as requirements instead of candidate solutions.
- Omitting out-of-scope.
- Saving a spec before user confirmation.
