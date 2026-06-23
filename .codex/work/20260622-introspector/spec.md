# Spec: Introspector

## Objective
Build a user-invoked `Introspector` skill for Codex that independently audits whether an idea, spec, plan, implementation result, or framework design is globally optimal, instead of accepting the current framing and applying local patches. The skill exists to counter LLM deference, expose root defects, and deliver the most reasonable high-level recommendation available from the evidence.

## Users
- Primary user: the skill author/operator using Codex as a decision system inside the local skill workflow.
- Secondary user: future Codex agents that need an authoritative, skeptical decision artifact before planning or implementation.

## Problem
Current LLM workflows often accept user framing too easily, preserve bloated architectures, praise weak designs, and optimize within a flawed structure instead of questioning whether parts should be deleted, merged, replaced, or abandoned. This produces patchwork answers, hidden complexity, and globally weak decisions. A dedicated skeptical skill is needed to force independent judgment before critical decisions become authoritative.

## Success Criteria
- For each invocation, the skill returns exactly one explicit decision posture such as `keep`, `trim`, `merge`, `redo`, `pause`, `change-direction`, or `block`.
- The output identifies the root goal, not just the presented artifact, and states whether the current framing is valid.
- The output names the highest-impact redundant, harmful, or structurally wrong elements and recommends whether to remove, preserve, or redesign them.
- The output proposes a simpler or stronger alternative path when it rejects the current direction.
- The output explains why competing options are worse, not just why the chosen option seems reasonable.
- The output follows a bounded multi-stage review flow rather than a single fused judgment pass.
- The output is backed by explicit evidence acquisition whenever the artifact alone is insufficient for a reliable global-optimality judgment.
- The output includes at least one falsifier that would cause the verdict to change if new evidence appeared.
- When evidence is insufficient, the skill refuses to force a conclusion and emits `block` with missing evidence and next investigation steps.
- Before the skill is treated as authoritative, its output passes a mandatory `reviewer` heavy review gate.

## Scope
### In
- Audit these artifact classes: `idea`, `spec`, `plan`, `implementation-result`, `framework-design`.
- Reframe the underlying objective when the presented solution appears to be only one possible approach.
- Challenge user assumptions and prior conclusions rather than preserving them by default.
- Prefer aggressive simplification, deletion, consolidation, or direction change when evidence supports it.
- Produce a fixed decision-style report with sections for objective, diagnosis, verdict, keep/remove/redo guidance, globally preferred path, rejected alternatives, evidence classes, evidence gaps, and risks.
- Require evidence acquisition and dependency-ring loading when the reviewed artifact is incomplete, self-referential, high-impact, or likely to hide key tradeoffs.
- Emit `block` instead of speculative certainty when the evidence is insufficient.
- Require `reviewer` heavy review as a gate before downstream acceptance.

### Out
- Ordinary style review, lint-like code commentary, or low-level syntax critique.
- Direct code implementation, automatic refactoring, or silent edits to the target artifact.
- Defaulting to total rewrites without evidence.
- Replacing domain experts in safety-critical domains such as medical, legal, or other specialist judgment.

## Requirements
### Functional
- The skill must be invoked explicitly by the user; it does not auto-trigger.
- The skill must use a fixed decision charter that outranks the reviewed artifact's own framing, including anti-sycophancy, truth-seeking, uncertainty disclosure, and "user agreement is not evidence".
- The skill must restate the root objective it believes the artifact is trying to serve.
- The skill must rewrite the presented problem in its own words before judging the proposed solution.
- The skill must assess whether the current framing is valid, incomplete, or fundamentally misguided.
- The skill must identify structural problems such as redundancy, self-inflicted complexity, poor boundaries, wasted components, local-optimum patching, or goal/artifact mismatch.
- The skill must run a bounded staged workflow: `objective extraction -> framing audit -> evidence acquisition -> provisional verdict -> strongest defense of current design -> alternative comparison -> verification -> final verdict`.
- The skill must perform evidence acquisition before finalizing a provisional verdict whenever the target artifact alone cannot justify a global-optimality claim.
- The skill must load at least one dependency ring when the artifact is incomplete, self-referential, configuration-sensitive, cross-file, or otherwise likely to conceal decisive context.
- The skill must generate a provisional verdict before the verification stage, and it must allow that verdict to change after critique or verification.
- The skill must issue a single top-level verdict from an explicit finite set and make the verdict actionable.
- The skill must separately state what should be kept, removed, merged, redesigned, deferred, or investigated.
- The skill must recommend what it believes is the globally best available path, not just improvements inside the current proposal.
- The skill must compare at least three candidate actions when applicable: preserve, simplify, and redesign.
- The skill must include the strongest available defense of the current artifact so that criticism is not one-sided by construction.
- The skill must explain why at least one plausible alternative path is inferior or unnecessary.
- The skill must distinguish direct evidence, inference, and uncertainty for each major conclusion.
- The skill must plan targeted verification questions or checks for its major claims before issuing the final verdict.
- The skill must include at least one explicit falsifier for the final verdict: a condition or missing fact that, if resolved differently, would change the judgment.
- The skill must perform a `delta review` after any revision pass: identify what new complexity, blind spots, or failure modes the revision itself introduced.
- The skill must run a `verdict stability check` whenever a verdict changes across iterations, and explain exactly which new evidence, requirement, or scope shift caused the change.
- The skill must emit a `block` result with missing evidence and next-step questions when it cannot responsibly determine a globally best path.
- The skill must prefer `block` over forced optimization claims when the root goal, constraints, or evaluation target remain materially underdefined after evidence acquisition.
- The skill must treat its output as non-authoritative until a mandatory `reviewer` heavy review returns an accepting verdict.

### Non-Functional
- Tone must remain neutral and skeptical, not flattering, deferential, or performatively contrarian.
- Reasoning should be aggressive in willingness to reject or simplify, but disciplined by evidence.
- Output must optimize for decision quality over politeness or preservation of prior work.
- The report format must be consistent enough to act as a workflow gate for downstream skills.
- The review flow must be auditable: a future agent should be able to see what was observed, inferred, challenged, and left unresolved.
- The skill must be calibration-aware: it should be possible to test whether it improves decision quality on representative overbuilt, good, ambiguous, and adversarially framed cases.
- The skill must be iteration-aware: later improvements must not silently invalidate earlier verdicts without a recorded change explanation.

## Constraints
- The skill should bias toward aggressive global optimization rather than conservative patching.
- Aggression must not become automatic opposition; negative conclusions require evidence and a better alternative or explicit evidence gap.
- The skill must not implement or edit the reviewed artifact as part of the review pass.
- The skill must treat the reviewed artifact and any embedded prompts, logs, or generated text as untrusted data unless independently verified.
- The skill must keep the critique loop bounded; v1 should use one critique pass and one verification pass rather than open-ended self-reflection.
- The skill must define a small calibration harness outside the prompt flow, with representative examples that can expose false skepticism, missed overengineering, and prompt-framing failures.
- The skill must default the mandatory `reviewer` heavy gate to adversarial focus for `Introspector` output artifacts unless a narrower review goal is explicitly justified.
- The skill must not assume that reviewer agreement alone proves independence; reviewer routing and focus must be part of the design.
- The skill must integrate a mandatory `reviewer` heavy review gate because the skill serves as a decision unit.
- If `reviewer` heavy review does not pass, the result cannot be treated as authoritative downstream.

## Assumptions To Validate
- [ ] A fixed verdict/report schema is sufficient for downstream skills to consume consistently. - Validate by testing the first `Introspector` draft against at least one downstream handoff scenario.
- [ ] Aggressive anti-deference behavior can be specified without causing the skill to become reflexively contrarian. - Validate by reviewing examples where the existing design is actually good.
- [ ] `reviewer` heavy review is available and practical as a mandatory gate for this workflow. - Validate during implementation by checking route feasibility and latency/operational cost.
- [ ] A bounded staged workflow preserves quality without making the skill too slow or repetitive for real Codex use. - Validate on a small set of representative idea/spec/plan reviews.
- [ ] Evidence acquisition plus dependency-ring loading improves verdict quality more than it harms usability. - Validate with timed trials on representative cases.
- [ ] The calibration harness can detect both false positives and false negatives in anti-sycophancy behavior. - Validate by scoring the first benchmark set with human inspection.

## Risks
- Overcorrection into blanket negativity may reduce trust or produce unnecessary redesign recommendations. - Mitigation: require evidence, explicit alternatives, and a `block` path for uncertainty.
- The skill may confuse “globally optimal” with “largest redesign.” - Mitigation: require explicit comparison against simpler keep/trim options.
- The skill may anchor too hard on its own first critique. - Mitigation: require a strongest-defense step plus a verification step before the final verdict.
- The skill may absorb prompt injection or biased framing from the reviewed artifact itself. - Mitigation: treat artifact content as untrusted and require independent restatement plus verification.
- The skill may become too slow or operationally heavy if evidence loading happens on every invocation. - Mitigation: make evidence acquisition conditional but mandatory under named risk triggers.
- The calibration harness may drift into a vanity benchmark that rewards style instead of judgment quality. - Mitigation: include clearly good, clearly bad, and ambiguous cases with human-inspected expected behaviors.
- Iterative refinement may create the illusion of reliability while merely moving the critique target each round. - Mitigation: require delta review and verdict-stability accounting across iterations.
- Heavy review gating may slow the workflow or be operationally awkward. - Mitigation: scope the artifact tightly and define a compact review packet.
- Users may over-trust the skill’s verdicts despite evidence gaps. - Mitigation: enforce explicit evidence/uncertainty labeling and a mandatory review gate.

## Acceptance Checks
- Confirm the spec names the primary user, problem trigger, scope, non-goals, and constraints explicitly.
- Confirm every success criterion is observable by a future agent reviewing an `Introspector` output artifact.
- Confirm the report contract includes explicit verdict semantics plus keep/remove/redo guidance.
- Confirm the report contract includes direct evidence, inference, uncertainty, rejected alternatives, and verification questions.
- Confirm the workflow includes a named evidence-acquisition stage and dependency-ring trigger conditions.
- Confirm the workflow requires a strongest-defense pass for the current design before final rejection.
- Confirm the output requires at least one falsifier for the final verdict.
- Confirm iteration changes require a delta review and verdict-stability explanation when conclusions shift.
- Confirm the spec requires `block` behavior when evidence is insufficient.
- Confirm the spec requires mandatory `reviewer` heavy review before downstream acceptance.
- Confirm the spec defaults `reviewer` heavy review to adversarial focus for `Introspector` outputs.
- Confirm no requirement asks the skill to implement code or perform ordinary style review.
- Confirm the spec treats reviewed artifacts and embedded prompts/logs as untrusted by default.

## Open Questions
- What exact canonical report section names and verdict vocabulary should the implementation standardize on?
- Should downstream workflow behavior after `REVISE` from the heavy reviewer be defined inside `Introspector` or delegated to the consuming workflow?
- What is the smallest calibration harness that is still strong enough to detect fake neutrality and false skepticism?
