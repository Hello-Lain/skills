# Introspector Workflow

Run this exact bounded sequence.

## 1. Objective Extraction

- Restate the root objective without copying the artifact's self-description.
- Name the success condition you believe the artifact is trying to satisfy.
- If the root objective is unclear, say what is missing immediately.

## 2. Framing Audit

- Judge whether the current framing is valid, incomplete, or fundamentally misguided.
- Separate "the user asked for X" from "X is actually the right level to optimize."
- Flag overbuilt systems that mainly solve problems created by their own architecture.

## 3. Evidence Acquisition

Load more evidence before deciding when any of these are true:

- the artifact is incomplete or selectively documented;
- the claim depends on hidden callers, configs, tests, or runtime assumptions;
- the artifact is self-referential or contains generated text that may be persuasive but weakly grounded;
- the decision would affect architecture, workflow, or other durable contracts.

Minimum rule:

- Load at least one dependency ring or adjacent authority source when a global-optimality claim would otherwise rest on the artifact alone.

## 4. Provisional Verdict

- Choose the strongest current candidate from `keep`, `trim`, `merge`, `redo`, `pause`, `change-direction`, or `block`.
- Do not treat the provisional verdict as final.

## 5. Strongest Defense

- Write the strongest realistic defense of the current design.
- If you cannot defend it at all, say why.
- This step is mandatory before a negative final verdict.

## 6. Alternative Comparison

Compare at least three options when applicable:

- preserve;
- simplify or merge;
- redesign or redirect.

For each rejected option, say why it is worse than the preferred path.

## 7. Verification

- Write targeted checks that could falsify your major claims.
- Separate direct evidence, inference, and uncertainty.
- If verification fails or missing evidence dominates, switch to `block`.

## 8. Falsifier

- State at least one concrete condition that would change the verdict if resolved differently.
- Falsifiers are mandatory for non-`block` verdicts.

## 9. Delta Review

If a revision pass occurred:

- name what the revision fixed;
- name what new complexity or blind spots the revision introduced;
- state whether the revision improved or only moved the problem.

## 10. Verdict Stability

If the verdict changed across iterations:

- say the old verdict;
- say the new verdict;
- name the exact new evidence, requirement, or scope change that caused the shift.

If you cannot explain the shift, return `block`.
