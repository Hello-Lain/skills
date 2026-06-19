# Discovery Routing Skill Collaboration Plan

Mode: light
Risk level: Medium
Confidence: High

## Goal
Implement shared Discovery Routing plus lightweight handoff contracts so `idea-refine`, `interview-me`, and `spec2plan` collaborate with clear responsibilities:

- `idea-refine`: decide the right direction to build.
- `interview-me`: turn a chosen direction into an implementation-ready spec.
- `spec2plan`: turn a confirmed spec into an executable plan.

## Non-Goals
- Do not implement the skill changes in this planning pass.
- Do not merge `idea-refine` and `interview-me`.
- Do not add a new router skill.
- Do not change unrelated skill behavior or existing user edits.
- Do not run implementation agents from this plan unless the user explicitly approves execution.

## Evidence Inspected
- `/data/lcq/.codex/skills/idea-refine/SKILL.md`
- `/data/lcq/.codex/skills/idea-refine/frameworks.md`
- `/data/lcq/.codex/skills/idea-refine/refinement-criteria.md`
- `/data/lcq/.codex/skills/interview-me/SKILL.md`
- `/data/lcq/.codex/skills/spec2plan/SKILL.md`
- `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- `/data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py`
- `git status --short` output showing existing dirty files in this repo.

## Spec Summary
Create a shared routing contract that prevents premature specs, avoids looping between skills, and provides a smooth pipeline:

```text
Idea or direction uncertainty -> idea-refine
Confirmed direction with missing requirements -> interview-me
Confirmed spec needing execution plan -> spec2plan
```

Update all three skills so they reference the same routing semantics and only hand off when their exit criteria are met.

## Domain Language Check
- Use `Discovery Routing` for the shared gate.
- Use `handoff` only for explicit workflow transfer with entry and exit criteria.
- Use `direction` for the product/solution choice produced by `idea-refine`.
- Use `spec` for the confirmed requirements artifact produced by `interview-me`.
- Use `plan` for the executable task artifact produced by `spec2plan`.
- Avoid `mutual invocation` language because it implies uncontrolled recursion.

## Current Context
- `idea-refine` already supports divergent/convergent idea work and saves ideas under `.codex/ideas/[idea-name].md`.
- `interview-me` already produces confirmed specs under `.codex/specs/[topic]/spec.md` and mentions downstream handoff to `idea-refine`, `spec-driven-development`, and `spec2plan`.
- `spec2plan` already consumes specs and emits `.codex/plans/<task-slug>/plan.md`.
- The repo has unrelated dirty changes. Implementation must preserve them and only touch planned files.

## Assumptions
- Shared routing can live as duplicated reference files under each involved skill for skill portability.
- A single canonical text block can be duplicated deliberately, with comments indicating it should stay in sync.
- No code changes are required beyond Markdown skill instructions and optional interface metadata updates.
- Existing validation scripts only validate `spec2plan` plan structure, not semantic skill behavior.

## User Inputs Needed
- None before drafting this plan.
- Before implementation, user should confirm whether duplicated routing references are acceptable or whether they prefer one central shared reference path.

## Proposed Approach
Use duplicated `references/discovery-routing.md` files in `idea-refine`, `interview-me`, and `spec2plan`, then add short handoff sections in each `SKILL.md`.

This keeps each skill self-contained while giving all three the same decision language. It avoids a fourth router skill and avoids uncontrolled bidirectional recursion.

## Scenario Probes
- User says: "I want to build an AI agent dashboard, but maybe this is not best." Route to `idea-refine`.
- User says: "We chose the lightweight CLI helper; now turn it into a spec." Route to `interview-me`.
- User says: "Spec is confirmed; make an executable plan." Route to `spec2plan`.
- `interview-me` discovers the artifact is a premature solution. Pause spec and route once to `idea-refine`.
- `idea-refine` lacks user/success/constraint facts. Ask one interview-style question at a time, then resume idea refinement.
- `spec2plan` receives an unconfirmed idea one-pager instead of a confirmed spec. Refuse planning and route back to `interview-me` or `idea-refine` depending on missing artifact.

## Dependency Graph
```text
Task 1: Create canonical Discovery Routing reference
  -> Task 2: Update idea-refine handoff
  -> Task 3: Update interview-me handoff
  -> Task 4: Update spec2plan collaboration gate
  -> Task 5: Validate docs and plan contract
  -> Task 6: Review coherence
```

Tasks 2, 3, and 4 depend on Task 1. Task 5 depends on Tasks 2-4. Task 6 depends on Task 5.

## Task Breakdown
### Task 1: Create shared Discovery Routing references

- Description: Add identical `references/discovery-routing.md` files for `idea-refine`, `interview-me`, and `spec2plan`, defining route signals, entry criteria, exit criteria, anti-loop rules, and the three-skill pipeline.
- Worker role: coding
- Wave: 1
- Acceptance criteria:
  - Each skill has `references/discovery-routing.md`.
  - The three files use the same canonical routing contract.
  - The contract names `idea-refine`, `interview-me`, and `spec2plan` roles explicitly.
  - The contract includes anti-loop guidance.
- Verification: `rtk diff idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md spec2plan/references/discovery-routing.md`
- Dependencies: None
- Files likely touched:
  - `idea-refine/references/discovery-routing.md`
  - `interview-me/references/discovery-routing.md`
  - `spec2plan/references/discovery-routing.md`
- Writable scope:
  - `idea-refine/references/discovery-routing.md`
  - `interview-me/references/discovery-routing.md`
  - `spec2plan/references/discovery-routing.md`
- Output artifact: `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-1-routing-reference.md`
- Estimated scope: S

### Task 2: Update idea-refine handoff instructions

- Description: Update `idea-refine/SKILL.md` to read `references/discovery-routing.md` when handoff or workflow routing is relevant; clarify that it may borrow interview-style questioning for missing critical facts but must not produce full implementation specs.
- Worker role: coding
- Wave: 2
- Acceptance criteria:
  - Frontmatter description distinguishes direction discovery from requirement clarification.
  - Body includes route-in and route-out rules.
  - Body says confirmed direction can hand off to `interview-me`.
  - Body says missing facts can use one-question-at-a-time interview protocol without producing a spec.
- Verification: `rtk grep -n "Discovery Routing\\|interview-me\\|spec2plan" idea-refine/SKILL.md`
- Dependencies: Task 1
- Files likely touched:
  - `idea-refine/SKILL.md`
- Writable scope:
  - `idea-refine/SKILL.md`
- Output artifact: `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-2-idea-refine.md`
- Estimated scope: S

### Task 3: Update interview-me handoff instructions

- Description: Update `interview-me/SKILL.md` to read `references/discovery-routing.md` when a request may be a premature solution; add a pause-and-route rule to `idea-refine` before writing a spec when direction quality is doubtful.
- Worker role: coding
- Wave: 2
- Acceptance criteria:
  - Frontmatter description no longer broadly claims all stress-test scenarios.
  - Body includes a route-to-`idea-refine` gate for premature or weak solution choices.
  - Body says resume `interview-me` only after a user-confirmed recommended direction exists.
  - Body preserves one-question-at-a-time and explicit confirmation rules.
- Verification: `rtk grep -n "Discovery Routing\\|idea-refine\\|spec2plan" interview-me/SKILL.md`
- Dependencies: Task 1
- Files likely touched:
  - `interview-me/SKILL.md`
- Writable scope:
  - `interview-me/SKILL.md`
- Output artifact: `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-3-interview-me.md`
- Estimated scope: S

### Task 4: Update spec2plan collaboration gate

- Description: Update `spec2plan/SKILL.md` so it only accepts confirmed specs or equivalent clear requirements, routes unconfirmed ideas/directions back through Discovery Routing, and documents the pipeline from `idea-refine` to `interview-me` to `spec2plan`.
- Worker role: coding
- Wave: 2
- Acceptance criteria:
  - Frontmatter description remains focused on executable planning.
  - Body says to read `references/discovery-routing.md` when source artifact maturity is ambiguous.
  - Body refuses to plan from an unconfirmed idea one-pager unless the user explicitly accepts assumptions or provides a confirmed spec.
  - Body identifies `idea-refine` and `interview-me` as upstream sources, not planning substitutes.
- Verification: `rtk grep -n "Discovery Routing\\|idea-refine\\|interview-me" spec2plan/SKILL.md`
- Dependencies: Task 1
- Files likely touched:
  - `spec2plan/SKILL.md`
- Writable scope:
  - `spec2plan/SKILL.md`
- Output artifact: `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-4-spec2plan.md`
- Estimated scope: S

### Task 5: Validate edited skill docs

- Description: Run structural checks and targeted text checks after Markdown edits.
- Worker role: devops
- Wave: 3
- Acceptance criteria:
  - `quick_validate.py` passes for all three skill folders if the validator is available.
  - Discovery Routing files are present.
  - Required handoff terms are discoverable with grep.
  - Existing unrelated dirty files are not reverted.
- Verification: `rtk python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py idea-refine && rtk python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py interview-me && rtk python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py spec2plan && rtk git diff -- idea-refine/SKILL.md interview-me/SKILL.md spec2plan/SKILL.md idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md spec2plan/references/discovery-routing.md`
- Dependencies: Tasks 2, 3, 4
- Files likely touched:
  - `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-5-validation.md`
- Writable scope:
  - `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-5-validation.md`
- Output artifact: `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-5-validation.md`
- Estimated scope: S

### Task 6: Review collaboration semantics

- Description: Perform a read-only review of the three-skill flow for trigger overlap, loop risk, missing exit criteria, and spec2plan accepting immature artifacts.
- Worker role: review
- Wave: 4
- Acceptance criteria:
  - Review returns PASS or FAIL.
  - Review checks at least three example user prompts across the routing pipeline.
  - Any FAIL includes exact file/section findings and suggested patch scope.
- Verification: `rtk grep -n "Route to idea-refine\\|Route to interview-me\\|Route to spec2plan\\|Avoid Loops" idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md spec2plan/references/discovery-routing.md`
- Dependencies: Task 5
- Files likely touched:
  - `.codex/specs/discovery-routing-skill-collaboration/review.md`
- Writable scope:
  - `.codex/specs/discovery-routing-skill-collaboration/review.md`
- Output artifact: `.codex/specs/discovery-routing-skill-collaboration/review.md`
- Estimated scope: S

## Step-by-Step Plan
1. Create `.codex/specs/discovery-routing-skill-collaboration/artifacts/`.
2. Add the canonical `discovery-routing.md` reference to all three skills.
3. Update `idea-refine/SKILL.md` with route-in, route-out, and interview-style-question borrowing rules.
4. Update `interview-me/SKILL.md` with pause-to-`idea-refine` rules for premature solutions.
5. Update `spec2plan/SKILL.md` with upstream artifact maturity checks and routing rules.
6. Run validators and grep checks.
7. Review semantic coherence with representative user prompts.
8. If review fails, patch only the failed sections and rerun validation.

## Parallelization
- Wave 1 must run alone because it defines the shared contract.
- Wave 2 tasks can run in parallel because they touch disjoint `SKILL.md` files.
- Wave 3 must run after Wave 2 because it validates all edits.
- Wave 4 must run last because it reviews the integrated flow.

## Files / Components Likely Affected
- `idea-refine/SKILL.md`
- `idea-refine/references/discovery-routing.md`
- `interview-me/SKILL.md`
- `interview-me/references/discovery-routing.md`
- `spec2plan/SKILL.md`
- `spec2plan/references/discovery-routing.md`
- `.codex/specs/discovery-routing-skill-collaboration/artifacts/`
- `.codex/specs/discovery-routing-skill-collaboration/review.md`

## Owners / Responsibilities
- Coding worker: Markdown edits and reference creation.
- Devops worker: validation commands and artifact logging.
- Review worker: semantic review for routing quality and loop risk.
- Main agent: preserve unrelated dirty work, consolidate final status, and avoid implementation unless approved.

## Validation Plan
- Validate skill folders with `.system/skill-creator/scripts/quick_validate.py` if available.
- Validate this plan with `spec2plan/scripts/validate_plan_contract.py .codex/plans/discovery-routing-skill-collaboration/plan.md --mode light`.
- Use targeted `rtk grep` checks for routing terms.
- Use `rtk git diff -- <planned files>` to inspect only intended changes.
- Optional forward-test after implementation with three prompts:
  - "I want an AI dashboard but maybe not sure this is best."
  - "We picked a CLI helper; interview me into a spec."
  - "Here is the confirmed spec; make a plan."

## Rollout Plan
- Not applicable for runtime rollout because this is local skill documentation.
- Operational rollout is replacement of skill docs in the local workspace after validation.

## Monitoring / Observability
- Observe future skill runs for:
  - Incorrect direct planning from raw ideas.
  - Repeated bouncing between `idea-refine` and `interview-me`.
  - `spec2plan` accepting unconfirmed ideas as specs.
  - Missed routing file reads when ambiguity exists.

## Documentation / ADR Updates
ADR: Not needed

The change is skill documentation and reference guidance. No architectural decision record is needed unless the user wants a broader skills-governance policy.

## Rollback / Recovery Plan
- Revert only the files touched by this plan if the new routing creates regressions.
- Preserve unrelated dirty files listed in `git status`.
- If duplicated references drift, restore them from the best validated copy and rerun grep checks.

## Abort Criteria
- User rejects duplicated reference files and requires a single shared source.
- Any skill validator fails for reasons unrelated to the planned changes and cannot be separated safely.
- Existing dirty changes in target files conflict with the planned edits.
- Review finds that routing instructions cause circular or contradictory behavior.

## Risks
- Medium: frontmatter descriptions are the trigger mechanism, so wording changes can affect skill activation.
- Medium: duplicated routing references can drift over time.
- Low: Markdown-only changes have no runtime risk.
- Low: overly strict `spec2plan` gating could block useful plans from well-formed but informal requirements.

## Open Questions
- Should the shared routing reference be duplicated per skill for portability or centralized in a top-level shared reference directory?
- Should `agents/openai.yaml` metadata be regenerated for skills whose frontmatter description changes?
- Should a future validator check that duplicated routing files are byte-identical?

## Execution Decision
Do not execute implementation yet. This plan is ready for user review and approval.

## Execution Handoff

- Goal: Implement shared Discovery Routing and lightweight handoffs for `idea-refine`, `interview-me`, and `spec2plan`.
- Current state: Plan drafted only; no skill implementation changes made by this plan.
- Authoritative artifacts: `.codex/plans/discovery-routing-skill-collaboration/plan.md`
- Decisions: Use duplicated per-skill routing references plus short handoff sections; avoid a new router skill.
- Verification: Run `rtk python spec2plan/scripts/validate_plan_contract.py .codex/plans/discovery-routing-skill-collaboration/plan.md --mode light`.
- Remaining risks: Trigger wording drift, duplicated reference drift, possible conflict with existing dirty edits.
- Next action: User approves, then execute Task 1 through Task 6.
- Suggested skills: `apply-patch`, `skill-creator`, `spec2plan`
- Redactions / omitted raw data: Full raw command outputs omitted; inspected paths listed above.
