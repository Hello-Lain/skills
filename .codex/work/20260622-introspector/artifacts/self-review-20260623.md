# Introspector Self-Review

- Artifact Type: self-review
- Confidence: Medium
- Verdict: `change-direction`

## Objective Extraction
- Reviewed artifact: `/data/lcq/.codex/skills/.codex/work/20260622-introspector/spec.md`
- Root objective: create a user-invoked Codex skill that resists user framing, identifies structural defects, and recommends the best available high-level path instead of patching local symptoms.
- Decision question: is the current `Introspector` design the globally best available approach for that objective?

## Framing Audit
- The current spec frames the problem primarily as a prompting and workflow-discipline problem.
- That framing is only partially valid.
- Direct evidence: the spec is rich in charter rules, stage ordering, and reviewer gating, but it does not require a concrete evidence-acquisition stage beyond restatement and verification questions.
- Inference: the current design overweights procedural skepticism and underweights calibrated evidence gathering and empirical self-audit.

## Provisional Verdict
- Provisional verdict: `change-direction`
- Reason: the current design is strong as a review protocol, but weak as a decision-quality system because it lacks a mandatory external evidence layer and an evaluation harness that can prove anti-sycophancy actually works.

## Strongest Defense Of Current Design
- The spec already contains several mature safeguards that many ad hoc critic prompts do not have: a fixed charter, anti-sycophancy, staged critique, explicit uncertainty, untrusted-artifact handling, and mandatory `reviewer` heavy gating.
- The bounded workflow is an advantage. It limits performative self-reflection and keeps the skill usable inside Codex.
- The current design is directionally aligned with the best public patterns found in `artifacts/neutrality-research.md`.
- A total rewrite would discard useful constraints that are already correct.

## Alternative Comparison
### Option A: `keep`
- Rejected.
- Why worse: leaves the largest weakness untouched. The current spec can critique a bad design, but it does not force fresh evidence collection when the reviewed artifact is incomplete, self-serving, or selectively documented.

### Option B: `trim`
- Rejected.
- Why worse: simplification alone does not fix the missing calibration layer. A slimmer prompt still fails if it cannot verify whether its skepticism is accurate.

### Option C: `redo`
- Rejected.
- Why worse: the core architecture is already useful. Rewriting from scratch would mostly recreate the existing charter, staged critique, and reviewer gate.

### Option D: `change-direction`
- Preferred.
- Why better: preserve the current critique core, but shift the center of gravity from "policy-heavy skeptical reviewer" to "evidence-first decision protocol with explicit calibration and adversarial evaluation."

## Keep / Remove / Redesign
### Keep
- Fixed decision charter above user framing.
- Bounded multi-stage workflow.
- Strongest-defense requirement.
- Explicit evidence / inference / uncertainty separation.
- Mandatory `reviewer` heavy gate.

### Remove
- Implicit assumption that verification questions alone are enough to support a final verdict.
- Implicit assumption that a heavy reviewer gate automatically provides epistemic independence.

### Redesign
- Add a mandatory `evidence acquisition` stage before provisional verdict finalization. The skill should have to name and load one dependency ring when the reviewed artifact is incomplete, high-impact, or self-referential.
- Add a mandatory `calibration harness` outside the prompt flow: a small benchmark set of overbuilt systems, good systems, ambiguous systems, and adversarially framed systems.
- Add a `falsifier requirement`: every final verdict must include one condition that would change the verdict if new evidence appears.
- Add a `reviewer independence rule`: the heavy gate should request adversarial review focus for this skill class by default, not generic confirmation review.
- Add a `scope stop rule`: when the root goal is underdefined, the skill should prefer `block` earlier instead of manufacturing a global-optimization claim.

## Verification Questions
- If the reviewed artifact hides important context, does the current spec force `Introspector` to fetch missing sources before deciding? No.
- If the current design looks elegant but lacks operating evidence, can the current spec distinguish "insufficient evidence" from "bad design" reliably? Not yet.
- Does the heavy reviewer gate guarantee independence from the same reasoning style that produced the original verdict? No.
- Is there any evaluation artifact that would let future agents measure whether anti-sycophancy improved decisions instead of just tone? No.

## Evidence Classes
- Direct evidence:
  - `/data/lcq/.codex/skills/.codex/work/20260622-introspector/spec.md`
  - `/data/lcq/.codex/skills/.codex/work/20260622-introspector/artifacts/neutrality-research.md`
- Inference:
  - The current design is stronger as a policy/workflow spec than as a calibrated decision system.
  - The reviewer gate is necessary but not sufficient for real independence.
- Uncertainty:
  - The actual implementation might recover some of these gaps if it embeds evidence loading and evaluation machinery that the current spec does not yet require explicitly.

## Final Verdict
- Verdict: `change-direction`
- Judgment: `Introspector` is not globally optimal in its current form.
- Best available path: keep the current charter and critique workflow, but redesign the skill around mandatory evidence acquisition, adversarial calibration, and explicit falsifiers. That path preserves what is already strong while fixing the highest-leverage structural gap.

## Risks
- Overcorrecting toward evidence gathering could make the skill too slow for routine use.
- A benchmark harness can itself encode bias if the corpus is one-sided.
- Default adversarial review may create false negatives unless bounded by clear evidence rules.
