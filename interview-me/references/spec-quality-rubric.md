# Spec Quality Rubric

Run this before treating a spec as final.

## Hard Fail

- Success criteria are not testable.
- Scope has no explicit out-of-scope.
- Requirements repeat solution labels instead of user-visible behavior.
- Constraints are generic words without thresholds, examples, or affected surfaces.
- Acceptance checks cannot be run or judged by a future agent.
- Unresolved guesses are written as facts.
- The user did not explicitly approve the restated intent.

## Upgrade Rules

- Convert adjectives to measures: "fast" -> target latency, throughput, or workflow time.
- Convert artifacts to outcomes: "dashboard" -> decision it enables.
- Convert architecture requests to pain: "clean architecture" -> specific coupling, duplication, or change cost to reduce.
- Convert AI requests to boundaries: autonomy level, inputs, outputs, failure handling, human approval.
- Keep implementation notes separate from requirements unless the user made them binding constraints.

## Minimum Final Spec

- Objective: who, what, why.
- Users: primary user first.
- Problem: current pain and trigger.
- Success Criteria: observable checks.
- Scope In/Out: v1 boundary and non-goals.
- Requirements: functional and only meaningful non-functional requirements.
- Constraints: binding limits.
- Assumptions To Validate: guesses with validation method.
- Risks: failure modes and mitigations.
- Acceptance Checks: commands, manual checks, or review criteria.
- Open Questions: blockers that remain.

## Template

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
- [ ] [Assumption] - [validation method]

## Risks
- [Risk] - [mitigation]

## Acceptance Checks
- [How the user/agent verifies done.]

## Open Questions
- [Question requiring user input before implementation.]
```
