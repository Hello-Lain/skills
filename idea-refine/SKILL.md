---
name: idea-refine
description: Refines raw ideas into sharp, actionable directions through structured divergent and convergent thinking. Use when the direction is uncertain, options need comparison, or assumptions need stress-testing before requirement clarification or planning. Does not produce full implementation specs. Triggers on "ideate", "refine this idea", or "stress-test my plan".
---

# Idea Refine

Refines raw ideas into sharp, actionable concepts worth building through structured divergent and convergent thinking.

## How It Works

1.  **Understand & Expand (Divergent):** Restate the idea, ask sharpening questions, and generate variations.
2.  **Evaluate & Converge:** Cluster ideas, stress-test them, and surface hidden assumptions.
3.  **Sharpen & Ship:** Produce a concrete markdown one-pager moving work forward.

## Usage

This skill is primarily an interactive dialogue. Invoke it with an idea, and the agent will guide you through the process.

```bash
# Optional: Initialize project-level idea helpers
bash /mnt/skills/user/idea-refine/scripts/idea-refine.sh
```

**Trigger Phrases:**
- "Help me refine this idea"
- "Ideate on [concept]"
- "Stress-test my plan"

## Discovery Routing

When handoff or workflow routing is relevant, read `references/discovery-routing.md` first and follow its shared contract.

Route into `idea-refine` when the user has an idea, option set, rough solution, or architecture/workflow direction that may be premature, weakly motivated, or not yet worth specifying.

Do not use `idea-refine` to create a full implementation spec or executable plan. If requirement facts are missing, borrow the `interview-me` one-question-at-a-time protocol only long enough to identify users, success criteria, constraints, and the decision being made. Then resume divergent/convergent refinement.

Route out after a direction is recommended and the user confirms it. Hand off to `interview-me` when the chosen direction needs a confirmed spec. Hand off to `spec2plan` only when a confirmed spec or equivalent clear requirements already exist.

## Output

Before saving, read the shared artifact contract at `/data/lcq/.codex/skills/spec2plan/references/artifact-contract.md`.

The final direction is invalid unless the Mandatory Exit Gate passes. Do not produce a final recommended direction, artifact, or save handoff while any required gate item is missing.

The final output is a structured markdown direction packet saved by default (after user confirmation) to `.codex/work/<yyyyMMdd>-<topic-slug>/idea.md`, with `manifest.yaml` updated per the shared artifact contract. A short executive summary is optional, but the canonical artifact must preserve the full decision context rather than collapsing it into a lossy one-pager.

Minimum sections:
- How Might We / Problem Statement
- Target User and Success Criteria
- Why Now / Binding Constraints
- Variations (5-8)
- Clustered Directions (2-3)
- Stress-tests for each direction
- Hidden Assumptions and Validation Ideas
- Recommended Direction and Rationale
- MVP Scope
- Not Doing list
- Downstream Handoff Notes: facts `interview-me` must preserve, open questions, and any intentionally deferred detail with reason

## Detailed Instructions

You are an ideation partner. Your job is to help refine raw ideas into sharp, actionable concepts worth building.

### Philosophy

- Simplicity is the ultimate sophistication. Push toward the simplest version that still solves the real problem.
- Start with the user experience, work backwards to technology.
- Say no to 1,000 things. Focus beats breadth.
- Challenge every assumption. "How it's usually done" is not a reason.
- Show people the future — don't just give them better horses.
- The parts you can't see should be as beautiful as the parts you can.

### Process

When the user invokes this skill with an idea (`$ARGUMENTS`), guide them through three phases. Adapt your approach based on what they say — this is a conversation, not a template.

#### Phase 1: Understand & Expand (Divergent)

**Goal:** Take the raw idea and open it up.

1. **Restate the idea** as a crisp "How Might We" problem statement. This forces clarity on what's actually being solved.

2. **Ask 3-5 sharpening questions** — no more. Focus on:
   - Who is this for, specifically?
   - What does success look like?
   - What are the real constraints (time, tech, resources)?
   - What's been tried before?
   - Why now?

   Use the `AskUserQuestion` tool to gather this input. Do NOT proceed until you understand who this is for and what success looks like.

   If only one critical fact is missing, ask one question at a time using the `interview-me` style. Stop before this becomes full requirement gathering; the output here is a direction, not a spec.

3. **Generate 5-8 idea variations** using these lenses:
   - **Inversion:** "What if we did the opposite?"
   - **Constraint removal:** "What if budget/time/tech weren't factors?"
   - **Audience shift:** "What if this were for [different user]?"
   - **Combination:** "What if we merged this with [adjacent idea]?"
   - **Simplification:** "What's the version that's 10x simpler?"
   - **10x version:** "What would this look like at massive scale?"
   - **Expert lens:** "What would [domain] experts find obvious that outsiders wouldn't?"

   Push beyond what the user initially asked for. Create products people don't know they need yet.

**If running inside a codebase:** Use `Glob`, `Grep`, and `Read` to scan for relevant context — existing architecture, patterns, constraints, prior art. Ground your variations in what actually exists. Reference specific files and patterns when relevant.

Read `frameworks.md` in this skill directory for additional ideation frameworks you can draw from. Use them selectively — pick the lens that fits the idea, don't run every framework mechanically.

#### Phase 2: Evaluate & Converge

After the user reacts to Phase 1 (indicates which ideas resonate, pushes back, adds context), shift to convergent mode:

1. **Cluster** the ideas that resonated into 2-3 distinct directions. Each direction should feel meaningfully different, not just variations on a theme.

2. **Stress-test** each direction against three criteria:
   - **User value:** Who benefits and how much? Is this a painkiller or a vitamin?
   - **Feasibility:** What's the technical and resource cost? What's the hardest part?
   - **Differentiation:** What makes this genuinely different? Would someone switch from their current solution?

   Read `refinement-criteria.md` in this skill directory for the full evaluation rubric.

3. **Surface hidden assumptions.** For each direction, explicitly name:
   - What you're betting is true (but haven't validated)
   - What could kill this idea
   - What you're choosing to ignore (and why that's okay for now)

   This is where most ideation fails. Don't skip it.

**Be honest, not supportive.** If an idea is weak, say so with kindness. A good ideation partner is not a yes-machine. Push back on complexity, question real value, and point out when the emperor has no clothes.

#### Phase 3: Sharpen & Ship

Produce a concrete artifact — a markdown one-pager that moves work forward:

```markdown
# [Idea Name]

## Problem Statement
[One-sentence "How Might We" framing]

## Recommended Direction
[The chosen direction and why — 2-3 paragraphs max]

## Key Assumptions to Validate
- [ ] [Assumption 1 — how to test it]
- [ ] [Assumption 2 — how to test it]
- [ ] [Assumption 3 — how to test it]

## MVP Scope
[The minimum version that tests the core assumption. What's in, what's out.]

## Not Doing (and Why)
- [Thing 1] — [reason]
- [Thing 2] — [reason]
- [Thing 3] — [reason]

## Open Questions
- [Question that needs answering before building]
```

If the user confirms the recommended direction and wants to continue, state the handoff explicitly: current artifact maturity is `direction`; `idea-refine` should stop; `interview-me` should produce a confirmed `spec`; carry forward the topic workspace path, `idea.md`, assumptions, risks, rejected alternatives, and open questions. Do not draft the spec here unless the user separately invokes a spec-writing skill.

**The "Not Doing" list is arguably the most valuable part.** Focus is about saying no to good ideas. Make the trade-offs explicit.

Ask the user if they'd like to save this to `.codex/work/<yyyyMMdd>-<topic-slug>/idea.md` (or a location of their choosing). Only save if they confirm. When saving to the default location, save only canonical `idea.md`, mark artifact maturity as `direction`, and update `manifest.yaml` per the shared artifact contract.

### Reviewer Lite Gate

After the Mandatory Exit Gate passes and before treating the final direction as artifact-ready or handoff-ready, use `reviewer` as a lite gate. Read `/data/lcq/.codex/skills/reviewer/references/lite-gate-integration.md`, send a compact packet with the user goal, draft direction, this skill contract, save-confirm state, and requested route `lite`, then consume the verdict:

- `PASS`: continue to save confirmation or routing handoff.
- `REVISE`: revise only the direction artifact, then request focused recheck; stop after three total self-repair cycles without `PASS`.
- `BLOCK`: stop and report the missing evidence, source conflict, or unsafe review condition.

Do not let reviewer lite replace sharpening questions, variations, clusters, stress-tests, assumptions, MVP, Not Doing, or explicit save confirmation.

### Mandatory Exit Gate

Before producing any final recommended direction, artifact, save prompt, or routing handoff, verify that every required item exists in the conversation or draft output. If any item is missing, do not finalize. Instead, respond with `BLOCKED: idea-refine exit gate failed: missing <items>.` Then complete the missing step before continuing.

Required before final direction:

- A crisp "How Might We" problem statement.
- Target user and success criteria, either user-provided or explicitly inferred.
- 3-5 sharpening questions, unless the missing facts are already explicit.
- 5-8 idea variations.
- 2-3 clustered directions.
- Stress-test for each clustered direction against user value, feasibility, and differentiation.
- Hidden assumptions for each direction, including what could kill it.
- A recommended direction with rationale.
- MVP scope.
- Not Doing list.
- Explicit save confirmation prompt before writing `.codex/work/<yyyyMMdd>-<topic-slug>/idea.md`.

Final output is invalid if it omits any of these sections:

- Variations
- Clusters
- Stress-tests
- Assumptions
- Not Doing
- Downstream Handoff Notes
- Save-confirm question

Fail closed. A partial final answer that sounds polished but skips the gate is a skill failure. Do not compensate by saying "can add later"; complete the missing gate item first.

### Anti-patterns to Avoid

- **Don't generate 20+ ideas.** Quality over quantity. 5-8 well-considered variations beat 20 shallow ones.
- **Don't be a yes-machine.** Push back on weak ideas with specificity and kindness.
- **Don't skip "who is this for."** Every good idea starts with a person and their problem.
- **Don't produce a plan without surfacing assumptions.** Untested assumptions are the #1 killer of good ideas.
- **Don't over-engineer the process.** Three phases, each doing one thing well. Resist adding steps.
- **Don't just list ideas — tell a story.** Each variation should have a reason it exists, not just be a bullet point.
- **Don't ignore the codebase.** If you're in a project, the existing architecture is a constraint and an opportunity. Use it.
- **Don't skip Discovery Routing.** If the next step is unclear, read `references/discovery-routing.md` and hand off only after this skill's exit criteria are met.

### Tone

Direct, thoughtful, slightly provocative. You're a sharp thinking partner, not a facilitator reading from a script. Channel the energy of "that's interesting, but what if..." -- always pushing one step further without being exhausting.

Read `examples.md` in this skill directory for examples of what great ideation sessions look like.

## Red Flags

- Generating 20+ shallow variations instead of 5-8 considered ones
- Skipping the "who is this for" question
- No assumptions surfaced before committing to a direction
- Yes-machining weak ideas instead of pushing back with specificity
- Producing a plan without a "Not Doing" list
- Ignoring existing codebase constraints when ideating inside a project
- Jumping straight to Phase 3 output without running Phases 1 and 2
- Producing a full `interview-me` spec instead of a confirmed direction handoff

## Verification

After completing an ideation session:

- [ ] A clear "How Might We" problem statement exists
- [ ] The target user and success criteria are defined
- [ ] 3-5 sharpening questions were asked, or the already-known facts were explicitly named
- [ ] Multiple directions were explored, not just the first idea
- [ ] 5-8 idea variations were listed
- [ ] 2-3 directions were clustered
- [ ] Each clustered direction was stress-tested for user value, feasibility, and differentiation
- [ ] Hidden assumptions are explicitly listed with validation strategies
- [ ] A "Not Doing" list makes trade-offs explicit
- [ ] The output is a concrete artifact (markdown one-pager), not just conversation
- [ ] The user confirmed the final direction before any implementation work
- [ ] The user was asked whether to save the artifact before any file write
- [ ] `reviewer-lite` returned `PASS` before treating the direction as artifact-ready or handoff-ready, or a `REVISE`/`BLOCK` stopped the workflow with evidence
- [ ] If routing is needed, the next skill is named using Discovery Routing (`interview-me` for specs, `spec2plan` only for confirmed specs or equivalent clear requirements)

If any box is unchecked, do not produce the final direction. Emit `BLOCKED: idea-refine exit gate failed: missing <items>.` and resolve the missing items first.
