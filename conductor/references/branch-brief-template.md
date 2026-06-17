# Branch Brief: <branch-id> - <title>

## Session Identity

- Stable session title:
- Type: branch
- Role:
- Status:
- Mode: Ambient / Autopilot / Strict

## Purpose Card

```text
You are branch <branch-id>: <title>
Purpose:
Not for:
Input:
Output:
Return to master when:
Hard-gate return rule:
```

## Parent Context

- Parent task:
- Parent branch:
- Snapshot id:
- Brief version:
- Created at:
- Why this branch exists:

## Branch Goal

State one precise outcome.

## Dependency / Order

- Execution wave:
- Depends on:
- Required inputs before start:
- Can run in parallel with:
- Unblocks:
- Gate condition:
- Start policy: current wave only / wait for prerequisite / optional
- Hard gates that must stop work:

## In Scope

- ...

## Out Of Scope

- ...

## Allowed Context

This branch may use only:

- this brief
- files explicitly listed here
- approved summaries explicitly included here
- user messages inside this branch thread

## Forbidden Assumptions

- Do not assume access to the master session history.
- Do not treat decisions made here as globally accepted.
- Do not read or summarize sibling branch raw context.
- Do not merge raw branch, worker, or explainer history into the master session.
- In Autopilot, return a short completion report automatically unless a hard gate is present.
- In Strict, wait for explicit master/user confirmation before completion or merge.

## Expected Artifacts

- ...

## Completion Criteria

- ...

## Global Decision Rule

If the user makes or implies a decision that affects other branches, architecture, scope, naming, deadlines, acceptance criteria, or project goals, do not treat it as globally binding. Record it under "Proposed Global Decisions", mark a hard gate, and return to master.

## Completion Report Requirements

When the branch appears done, produce a completion report automatically in Autopilot, or after confirmation in Strict, with:

- result summary
- artifacts and files
- local decisions
- proposed global decisions
- validation or checks
- risks
- handoff capsule with goal, current state, authoritative artifacts, decisions, verification, remaining risks, next action, suggested skills, and redactions / omitted raw data
- suggested merge note
