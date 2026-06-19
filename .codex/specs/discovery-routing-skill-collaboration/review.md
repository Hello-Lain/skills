Salvaged-From-Worker: review-1

### Findings
Artifact write blocked by approval infrastructure. Complete review body:

```markdown
# Review: Collaboration Semantics

Verdict: PASS

## Scope Reviewed

- `idea-refine/references/discovery-routing.md`
- `interview-me/references/discovery-routing.md`
- `spec2plan/references/discovery-routing.md`
- Authoritative plan: `.codex/plans/discovery-routing-skill-collaboration/plan.md`

## Findings

No blocking findings.

## Verification

Required command passes:

```bash
rtk grep -n "Route to idea-refine\\|Route to interview-me\\|Route to spec2plan\\|Avoid Loops" idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md spec2plan/references/discovery-routing.md
```

Evidence:

- 12 matches across 3 files.
- Each file contains:
  - `Route to idea-refine when:`
  - `Route to interview-me when:`
  - `Route to spec2plan when:`
  - `## Avoid Loops`

## Semantic Checks

Prompt: "I want to build an AI agent dashboard, but maybe this is not best."

Expected route: `idea-refine`.

Result: PASS. Route signals cover uncertainty, competing directions, stress-testing, weak motivation, and unclear success model.

Prompt: "We chose the lightweight CLI helper; now turn it into a spec."

Expected route: `interview-me`.

Result: PASS. Entry criteria require a selected direction, and route signals cover incomplete requirements, success criteria, constraints, risks, scope, and confirmed spec creation.

Prompt: "Here is the confirmed spec; make a worker-wave implementation plan."

Expected route: `spec2plan`.

Result: PASS. Route signals cover confirmed specs, executable plans, implementation sequencing, task breakdown, worker waves, validation, and rollout planning.

Prompt: "Here is a rough one-pager idea; make a plan."

Expected route: upstream before planning.

Result: PASS. `spec2plan` entry criteria require a confirmed spec or equivalent clear requirements; raw ideas or unconfirmed directions route upstream.

## Loop Risk

PASS. Loop controls are explicit and coherent:

- route only one step upstream at a time;
- no repeated bouncing without user confirmation;
- downstream skills must not fill upstream gaps;
- `idea-refine` must not create full specs;
- `interview-me` must not create execution plans;
- explicit user override records assumptions and continues.

## Exit Criteria

PASS. Each skill has clear exit artifact:

- `idea-refine` exits with a recommended direction, rejected alternatives, assumptions, risks, and context for requirement questions.
- `interview-me` exits with confirmed spec, scope, non-goals, success criteria, constraints, and enough detail for planning.
- `spec2plan` exits with executable plan, task sequence, dependencies, validation, risks, rollback, ownership, and no hidden product/spec gaps.

## Byte-Identity Check

PASS. The three routing reference files are byte-identical by `cmp -s` checks.

## Residual Risk

Low. Duplicated references can drift later. Current text mitigates this with the byte-identity instruction, but future validation should keep checking byte identity.

## Required Fix

None.
```

### Verification
- See worker result; artifact was salvaged by run_wave.py after worker write failure.
