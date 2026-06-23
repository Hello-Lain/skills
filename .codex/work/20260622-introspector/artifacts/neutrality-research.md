# Introspector Neutrality Research

## Goal
Capture mature public patterns for keeping LLM judgments neutral, evidence-driven, and resistant to user framing so `Introspector` can reuse proven mechanisms instead of relying on vague "be skeptical" guidance.

## Sources
- OpenAI Model Spec: https://model-spec.openai.com/2025-12-18.html
- Anthropic Constitutional AI: https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback
- Claude Constitution: https://www.anthropic.com/constitution
- Self-Refine paper: https://arxiv.org/abs/2303.17651
- Reflexion paper: https://arxiv.org/abs/2303.11366
- Chain-of-Verification paper: https://aclanthology.org/2024.findings-acl.212/

## Reusable Patterns

### 1. Principle Layer Above User Framing
- `Model Spec` and `Claude's Constitution` both separate stable behavior rules from the current user request.
- Reuse for `Introspector`: define a fixed decision charter that outranks the reviewed artifact's own framing.
- Immediate implication: the skill must evaluate "is the framing itself wrong?" before optimizing inside it.

### 2. Draft -> Critique -> Revise
- `Constitutional AI` and `Self-Refine` both use an explicit self-critique pass before accepting a draft.
- Reuse for `Introspector`: require an initial diagnosis, then a critique of that diagnosis, then a revised verdict.
- Immediate implication: no first-pass answer can become the final verdict.

### 3. Separate Critique Role From Final Verdict
- `Self-Refine` works because feedback is not mixed into the initial generation step.
- Reuse for `Introspector`: split the workflow into `diagnose`, `challenge`, `compare alternatives`, `verify`, `decide`.
- Immediate implication: the skill should not generate a recommendation and justification in one fused pass.

### 4. Verification Questions Before Final Decision
- `Chain-of-Verification` adds planned verification questions before committing to a final answer.
- Reuse for `Introspector`: after choosing a provisional verdict, generate targeted checks that could falsify it.
- Immediate implication: every major conclusion should have at least one explicit verification question or evidence test.

### 5. Explicit Evidence / Inference Separation
- `Model Spec` pushes honesty, uncertainty, and highlighting possible misalignments.
- Reuse for `Introspector`: mark each major claim as direct evidence, inference, or unresolved uncertainty.
- Immediate implication: the skill can say `block` without pretending confidence.

### 6. Anti-Sycophancy As A Named Rule
- `Model Spec` names "Don't be sycophantic" directly instead of burying it in style guidance.
- Reuse for `Introspector`: add a hard rule that agreement with the user or existing design is never evidence.
- Immediate implication: "the user said so" and "the system already exists" cannot count toward a verdict.

### 7. Compare Against Simpler Baselines
- Mature alignment and review systems do not assume a larger intervention is better.
- Reuse for `Introspector`: compare `keep`, `trim`, and `redo` even when the draft leans toward one of them.
- Immediate implication: global optimum must beat a simpler baseline, not just criticize the current artifact.

### 8. Use Memory Only For Error Patterns
- `Reflexion` stores reflective feedback to improve later attempts.
- Reuse for `Introspector`: if memory is added later, store recurring failure modes, not prior verdicts as authority.
- Immediate implication: preserve lessons like "missed hidden dependencies" or "overweighted elegance", but do not preload conclusions.

## Design Moves For The Spec
- Add a fixed decision charter above user instructions.
- Add a mandatory multi-stage workflow: objective extraction, framing audit, provisional verdict, strongest countercase, alternative comparison, verification, final verdict.
- Require at least one simplifying baseline and one strongest defense of the current design.
- Require a `block` path when verification questions fail or evidence is missing.
- Require report sections for evidence class, rejected alternatives, and falsifiers.
- Keep `reviewer` heavy review as the external gate because self-critique alone is not enough.

## What Not To Copy
- Do not copy constitutional/safety language wholesale; `Introspector` needs decision-quality rules, not general assistant policy.
- Do not copy research loops with indefinite iteration; use bounded passes to avoid performative self-critique.
- Do not use persistent memory for verdicts in v1; it will bias later reviews.
