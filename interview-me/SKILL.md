---
name: interview-me
description: Interview users one question at a time to turn a chosen direction with missing requirements into confirmed, implementation-ready specs before planning or coding. Use when who, why, success criteria, constraints, scope, or non-goals are missing; when the user asks to be interviewed, grilled, or questioned on requirements; or when a selected artifact like "dashboard", "AI agent", "refactor", "make faster", "clean architecture", "modern", or "robust" needs requirement clarification rather than direction discovery.
---

# Interview Me

## Contract

- Extract intent, then produce a confirmed markdown spec downstream skills can consume.
- Do not plan, code, or write tasks before spec confirmation.
- Ask one focused question at a time. Include a guess and why the question matters.
- Require explicit approval before treating a restatement or spec as authoritative; an explicit `yes` to the restatement authorizes writing the final spec and saving it to the default workspace.
- Requires a live user. In non-interactive/autonomous contexts, stop and report missing requirements instead of guessing.
- If the user explicitly chooses speed, a short pass, or "don't overthink it", use Fast Spec Mode.
- In final/user-facing interview output, do not announce that the skill is being used; start with the interview output. This does not override higher-priority system requirements for commentary-channel progress updates.

## Use / Do Not Use

Use when any of these are missing: target user, reason, success criteria, binding constraint, scope, non-goals.

Do not use for typo fixes, mechanical edits, or pure explanations.

Use Discovery Routing when the requested solution may be premature. Read `references/discovery-routing.md` before interviewing if the user has not chosen a direction, if multiple directions are competing, or if the artifact appears weakly motivated.

Route to `idea-refine` before writing a spec when direction quality is doubtful. Resume `interview-me` only after the user confirms a recommended direction from `idea-refine`.

## Workflow

### 1. Hypothesize

Start with:

```text
HYPOTHESIS: You want <outcome>, and "<requested artifact>" is probably just the first solution that came to mind.
CONFIDENCE: ~30% - missing: <who/why/success/constraint/scope>
```

Confidence rubric:
- Start at 20%.
- Add 15 for explicit target user.
- Add 15 for real problem / why now.
- Add 20 for measurable success.
- Add 15 for binding constraint.
- Add 15 for scope in/out.
- Add 10 for acceptance checks.
- Cap at 69% if success, scope, or non-goals are still vague.

Thresholds:
- Below 70%: keep interviewing.
- 70-84%: restate intent and ask `Explicit yes / refine?`.
- 85%+: final spec may be drafted only after explicit approval.

### 2. Interview One Question At A Time

Before the first question, choose a mode. If the request maps to a listed mode, read `references/question-ladders.md` and use that mode's first useful question. Otherwise use this default ladder:

1. Who benefits?
2. What painful situation triggered this?
3. What outcome would make this successful?
4. What constraint is binding: time, tech, data, UX, migration, policy, budget?
5. What must be included in v1?
6. What is explicitly out of scope?
7. How will done be verified?

Ask:

```text
Q: <question>
GUESS: <likely answer + evidence>
UNLOCKS: <decision this answer controls>
```

Wait for the answer. Do not batch questions. Update the hypothesis and confidence as answers arrive.

Mode triggers:
- Product/feature
- Refactor: "refactor", "clean up", "rewrite", "simplify", "architecture"
- Performance: "faster", "slow", "latency", "throughput", "optimize"
- Bug: "bug", "broken", "regression", "expected vs actual"
- UI/design: "UI", "design", "layout", "screen", "component"
- Docs/process: "docs", "runbook", "process", "workflow"

Probe "should want" answers. If the user gives best-practice or sophistication-signaling terms like "scalable", "modern", "clean", "robust", or "standard", ask:

```text
If you did not have to justify this to anyone, what would you actually want?
```

Stop interviewing only when you can predict the user's reaction to the next three questions. If several rounds do not raise confidence, say what foundational fact is still missing and ask whether to step back.

### 3. Fast Spec Mode

Use only when the user asks to move fast, avoid a long interview, do a rough pass, keep it minimal, or "don't overthink it".

Ask at most three questions, still one at a time. Prefer mode-specific questions from `references/question-ladders.md`; otherwise ask:
1. Who is this for?
2. What measurable outcome counts as success?
3. What is in/out for v1?

Then write a draft spec with unresolved items marked as assumptions or open questions. Do not hide uncertainty.

### 4. Restate Before Spec

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

An explicit `yes` to this restatement means:
- Write the final spec.
- Read the shared artifact contract at `/data/lcq/.codex/skills/spec2plan/references/artifact-contract.md`.
- Save the confirmed spec automatically to `.codex/work/<yyyyMMdd>-<topic-slug>/spec.md`, or to the reused topic workspace when the interview started from an existing workspace artifact.
- Do not ask a separate "save?" question unless the canonical `spec.md` already exists and replacement intent is unclear.

### 5. Produce The Spec

Before finalizing, read `references/spec-quality-rubric.md`, use its template, and fix any failing gate. Include only details supported by the interview; mark unresolved items as assumptions or open questions.

For codebase work, inspect relevant files before finalizing Commands, Project Structure, Testing Strategy, or integration constraints. Reference concrete paths when useful.

### 6. Save / Hand Off

After the user explicitly answers `yes` to the restated intent, produce the final spec and save it automatically. First read the shared artifact contract at `/data/lcq/.codex/skills/spec2plan/references/artifact-contract.md`, then save the confirmed spec to `.codex/work/<yyyyMMdd>-<topic-slug>/spec.md` by default, or to the user's chosen path when provided. Do not save before explicit `yes`.

Prefer the project root's `.codex/work/` topic workspace so downstream skills can discover the spec, lineage, and later plan cleanly. Use a dated kebab-case topic workspace, for example `.codex/work/20260619-auth-migration/spec.md`. If the interview started from an existing workspace artifact, reuse that workspace and set `lineage.spec` to the source artifact when applicable. If the current workspace is not a project/repo, ask for a path instead of guessing.

If the intended canonical `spec.md` already exists:
- Overwrite it only when the user explicitly requested replacement or the current interview is a continuation that clearly supersedes the existing draft.
- Otherwise ask before overwriting, or save the new draft under `revisions/spec-<yyyyMMdd-HHmmss>.md` when the user asked for an alternative.

After confirmation, downstream handoff:

- Use `idea-refine` if the spec exposes multiple possible product directions or the chosen solution becomes untrusted.
- Use `spec2plan` when the confirmed spec should become executable tasks or a reviewed implementation plan.
- Use `team-spec-workflow` when the confirmed spec needs delegated, file-disjoint implementation waves and review artifacts.

For any handoff, follow the Handoff Contract in `references/discovery-routing.md`: state artifact maturity, why `interview-me` should stop, next skill, expected artifact, shared work directory, confirmed `spec.md` path, and carried assumptions or risks.

## Quality Gates

Before finishing, verify:

- Hypothesis + confidence appeared before questions.
- Questions were one at a time and each included a guess.
- Each question unlocked a real spec decision.
- User, why, success, constraints, scope, and out-of-scope are explicit.
- Vague terms were converted into measurable criteria or open questions.
- Spec separates requirements, constraints, assumptions, risks, acceptance checks.
- User explicitly confirmed the restated intent before the final spec was treated as authoritative.
- Confirmed specs are saved automatically after explicit `yes`, unless conflict rules require asking before overwrite.
- No implementation plan or code was produced before spec confirmation.

## Red Flags

- Asking multiple questions in one message.
- Asking survey-style questions without a guess.
- Accepting "whatever you think" as approval.
- Writing implementation tasks before the spec is confirmed.
- Treating "dashboard", "AI agent", "clean architecture", or "make faster" as requirements instead of candidate solutions.
- Omitting out-of-scope.
- Saving a spec before user confirmation.

## Optional Examples

Read `references/examples.md` when behavior drifts, when improving this skill, or when you need a concrete model of strong first-turn interview behavior.
