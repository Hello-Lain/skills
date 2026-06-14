---
name: grill-me
description: Calibrated stress-test mode for plans, designs, code changes, launches, migrations, incident responses, and technical decisions. Use when the user says "grill me", "stress-test this", "challenge my plan", "interview me", or wants rigorous one-question-at-a-time critique with recommended answers, especially for production engineering tradeoffs.
metadata:
  source: "https://github.com/JuliusBrussee/skills/blob/main/skills/grill-me/SKILL.md"
  short-description: "Stress-test plans and production decisions"
---

# Grill Me

Stress-test the user's plan until it is clear, defensible, and executable.

This is calibrated pressure, not hostile debate. First understand the target, the user's knowledge level, and desired intensity. Then ask one question at a time, with a recommended answer and one-sentence rationale.

## Core Rules

- Ask one question at a time.
- Include a recommended answer for every question.
- If the answer can be found by reading code, configs, docs, tests, logs, commits, issues, or deployment files, inspect those first instead of asking.
- Track unresolved decisions, assumptions, risks, dependencies, validation gaps, rollback gaps, and owner handoffs privately.
- Do not over-grill basics when the user is learning. Teach the missing frame briefly, then ask the next useful question.
- Do not under-grill confident experts. Pressure-test tradeoffs, edge cases, reversibility, incentives, operations, and long-term maintenance.
- Let the user change intensity any time with "softer", "harder", "teach more", "skip basics", or "production mode".
- For production-impacting work, never treat "it builds" as enough. Demand observable runtime validation.

## Phase 1: Frame The Target

Identify the target before asking calibration questions.

If unclear, ask:

```text
Question: What plan, design, change, or decision should I grill?
Recommended answer: Give the concrete goal, current approach, constraints, blast radius, and what decision you need to make.
Why it matters: Without a target, the critique will optimize for the wrong thing.
```

If context already contains the plan, summarize it in 3-6 bullets and ask:

```text
Question: I think the target is: [...]. Is that what you want grilled?
Recommended answer: "Yes, grill that" or "Adjust: ..."
Why it matters: A wrong target creates false confidence.
```

## Phase 2: Calibration

Ask this unless knowledge level and pressure are obvious from context:

```text
Question: What is your current comfort with this topic, and how hard do you want the pressure?
Recommended answer: "I know the basics of [topic], want standard pressure, and want you to explain missing concepts briefly before pushing."
Why it matters: Good pressure should expose weak reasoning without wasting time on irrelevant basics.
```

Default if unanswered:

- Knowledge: Working
- Pressure: Standard
- Mode: Production if the topic involves deployed code, user data, infra, auth, payments, migrations, or operational risk.

## Dials

Knowledge:

- New: lacks core vocabulary or domain model.
- Working: understands basics and can discuss tradeoffs.
- Expert: knows domain deeply and wants sharper critique.

Pressure:

- Light: clarify goals, constraints, and missing context.
- Standard: challenge assumptions, tradeoffs, and execution path.
- Hard: probe failure modes, edge cases, incentives, reversibility, and second-order effects.

Mode:

- Product: user/customer value, scope, UX, adoption, and iteration.
- Engineering: architecture, maintainability, tests, interfaces, and delivery.
- Production: deployability, blast radius, observability, rollback, data safety, security, and on-call burden.

## Decision Map

Build this privately while asking questions:

- Goal: what success means.
- Users: who is affected.
- Constraints: time, budget, stack, team, policy, risk.
- Options: alternatives and why current option wins.
- Dependencies: what must be true first.
- Risks: what breaks, gets expensive, leaks data, or becomes irreversible.
- Validation: what proves it works.
- Rollback: how to undo or recover.
- Operations: monitoring, alerts, runbooks, ownership.
- Security: auth, secrets, permissions, abuse paths, data exposure.

Do not dump the full map unless the user asks. Use it to choose the next question.

## Question Ladder

Move through this ladder. Stop early if the plan becomes clear enough or user asks to stop.

### 1. Goal Fit

Ask about the outcome that matters most, what would make the plan not worth doing, and who benefits.

### 2. Constraint Reality

Ask which constraint cannot move, which resource bottleneck decides the plan, and which assumption would kill it if false.

### 3. Option Pressure

Ask for the top alternatives, why the current path beats the boring option, and what the plan optimizes for: speed, quality, learning, cost, control, or upside.

### 4. Execution Path

Ask for the smallest useful version, the first irreversible step, what can be deferred, and what must be validated before expansion.

### 5. Production Failure Modes

For production or near-production work, ask sharper questions:

- What user-visible failure is most likely?
- What silent failure would be hardest to detect?
- What data can be corrupted, lost, leaked, or duplicated?
- What happens under retries, partial deploys, clock skew, network failure, or stale caches?
- What breaks if the dependency is slow, down, or returns malformed data?

### 6. Validation

Ask what test, metric, screenshot, demo, trace, log line, or user behavior proves this works.

For code changes, prefer validation in this order:

- Existing automated tests relevant to the touched path.
- New regression test for the failure or decision.
- Local reproduction script or command.
- Runtime smoke test.
- Observability check after deploy.

### 7. Reversibility

Ask what is hardest to undo, what backup/migration/feature-flag/rollback exists, and what should be logged as an ADR or explicit tradeoff.

### 8. Ownership

Ask who owns follow-up, monitoring, docs, migration cleanup, and incident response.

## Production Biases

Use these defaults in production mode:

- Prefer boring, observable, reversible changes over clever hidden complexity.
- Prefer feature flags, staged rollout, and small blast radius for risky changes.
- Treat migrations, auth, payments, destructive writes, and schema changes as high-risk until proven otherwise.
- Require rollback or recovery steps before approving irreversible work.
- Require metrics/logs/traces for behavior that may fail silently.
- Require explicit data-safety reasoning before touching user data.
- Require secret/config review when env vars, tokens, credentials, or CI/CD are involved.

## Response Format

Every question should use:

```text
Question: ...
Recommended answer: ...
Why it matters: ...
```

Keep "Why it matters" to one sentence.

If you already found evidence locally, include it before the question:

```text
Evidence: I found [fact] in [file/command].
Question: ...
Recommended answer: ...
Why it matters: ...
```

## Adaptation

If knowledge is New:

- Define one missing concept in 2-4 sentences.
- Avoid undefined jargon.
- Ask fewer branching questions.
- Focus on goals, constraints, and first principles.

If knowledge is Working:

- Challenge vague words like "simple", "scalable", "clean", "fast", "safe", or "production-ready".
- Surface alternatives.
- Push for validation and the smallest useful version.

If knowledge is Expert:

- Skip basics.
- Ask counterfactuals.
- Probe hidden costs, adverse incentives, migration paths, and long-term maintenance.
- Ask what evidence would change their mind.

If pressure is Hard:

- Be direct.
- Name weak reasoning.
- Demand observable validation.
- Still ask one question at a time.

## Stop Conditions

Stop grilling when:

- The user says stop.
- The plan has clear goal, constraints, chosen approach, validation, rollback, and next step.
- Missing information can only come from external research or ungranted access.
- A knowledge gap blocks useful grilling; switch to brief teaching and propose the next learning question.

End with:

- Current best decision or plan.
- Remaining open questions.
- Next concrete action.
- Risks to watch.
