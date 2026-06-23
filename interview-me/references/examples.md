# Interview Examples

## Ambiguous Feature

User: "Build me an AI dashboard for support."

```text
HYPOTHESIS: You want support leads to understand and act on support workload, and "AI dashboard" may be the first solution that came to mind.
CONFIDENCE: ~35% - missing: primary user, success metric, binding constraint, v1 scope, non-goals

Q: Who is the first user this must work for?
GUESS: A support team lead, because "dashboard" usually implies monitoring and prioritization rather than direct customer action.
UNLOCKS: Whether the spec should optimize for executive summary, agent workflow, or ops triage.
```

## Performance Request

User: "Make search faster, don't overthink it."

```text
HYPOTHESIS: You want a small performance improvement to the existing search path without a broad redesign.
CONFIDENCE: ~45% - missing: baseline, target, workload, acceptable tradeoffs, acceptance check

Q: What is the one search path and target metric that matters most?
GUESS: The normal user-facing query path, measured by p95 latency, because "make search faster" is otherwise too broad to verify.
UNLOCKS: The acceptance check and whether the fix can be local or needs architecture work.
```

## Refactor Request

User: "Clean up auth."

```text
HYPOTHESIS: You want to reduce maintenance risk in auth, and "clean up" may mean a refactor rather than changed user behavior.
CONFIDENCE: ~30% - missing: pain, preserved behavior, affected surfaces, risk, acceptance checks, non-goals

Q: What current auth pain should disappear after this work?
GUESS: Duplicated token/session logic, because "clean up auth" usually points to change-risk rather than a new feature.
UNLOCKS: Whether the spec should target module boundaries, bug risk, test coverage, or developer ergonomics.
```

## Direction-Derived Spec

If `interview-me` starts from a saved `idea.md`, the final `spec.md` should preserve and expand it explicitly:

```markdown
## Upstream Context
- Source artifact(s): `.codex/work/20260623-local-restaurant-regulars/idea.md`
- Chosen direction to preserve: keep known regulars ordering direct with near-zero restaurant effort
- Deferred / dropped upstream details: pricing deferred because packaging is still open; no direction detail dropped

## Objective
Help independent restaurant owners retain repeat customers through direct reorders so they reduce commission paid to delivery platforms.

## Success Criteria
- A future agent can verify direct reorder flow works end to end.
- The spec keeps v1 scoped away from discovery marketplace and delivery logistics.

## Constraints
- No custom driver network in v1.
- Restaurant-side setup must stay near-zero.
```
