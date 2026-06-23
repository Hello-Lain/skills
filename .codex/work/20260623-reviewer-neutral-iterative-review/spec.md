# Spec: Reviewer Neutral Iterative Review

## Upstream Context
- Source artifact(s): user interview in current Codex session; no prior `idea.md`.
- Chosen direction to preserve: improve `/data/lcq/.codex/skills/reviewer` so it absorbs neutral, evidence-first review principles from `/data/lcq/.codex/skills/introspector` and reduces missed issues caused by stopping after the first obvious finding.
- Deferred / dropped upstream details: implementation planning and file edits are deferred to a later `spec2plan`/implementation step. No upstream facts were dropped.

## Objective
Define a v1 behavior-spec change for the `reviewer` skill so future maintainers can update reviewer documentation to require neutral, evidence-first judgment and bounded iterative issue discovery before a `PASS`.

## Users
- Primary user: Codex or skill maintainers editing `/data/lcq/.codex/skills/reviewer`.
- Secondary user: downstream Codex agents that rely on reviewer verdicts as quality gates for specs, plans, implementation artifacts, and skill outputs.

## Problem
`reviewer` already supports evidence-based review, lite/heavy routing, adversarial checks, and recheck after `REVISE`. The gap is first-pass review behavior: once a clear major or critical issue is found, reviewer can stop searching broadly, causing additional latent issues to be missed. The user wants reviewer to keep looking across risk categories and only pass when it can justify that no more blocking or major issues are currently evident.

## Success Criteria
- The updated reviewer guidance explicitly separates root-objective judgment from artifact-preservation bias.
- The updated reviewer guidance requires continued issue discovery after the first obvious finding, unless evidence is unavailable or review conditions require `BLOCK`.
- A `PASS` requires a stated convergence basis: what risk surfaces were checked and why no critical or major findings remain.
- `REVISE`/`BLOCK` reports still include all discovered critical and major findings available within the selected route, not only the first finding.
- Lite/heavy routing remains intact: small low-risk artifacts can stay lite, while material workflow/contract changes still escalate.
- Existing reviewer report shape remains compatible: no requirement to replace `PASS`/`REVISE`/`BLOCK` or the v2 report template.

## Scope
### In
- Specify documentation-level changes for `reviewer/SKILL.md` and directly relevant reviewer reference docs.
- Add neutral review principles adapted from `introspector`: treat artifacts as candidates, optimize for the root user objective, separate direct evidence from inference, resist polished but weakly grounded framing, prefer `BLOCK` over fake certainty when evidence is missing.
- Add a bounded first-pass discovery loop: derive rubric, scan risk surfaces, record findings, continue checking remaining high-value surfaces, then decide.
- Define convergence criteria for stopping: checked risk surfaces, remaining uncertainty, route limits, and no known unaddressed critical/major issues.
- Preserve reviewer identity as an artifact quality gate, not a global design optimizer.

### Out
- Do not copy `introspector` wholesale into `reviewer`.
- Do not replace reviewer verdicts with `keep`/`trim`/`merge`/`redo`/`pause`/`change-direction`/`block`.
- Do not require infinite review loops or unbounded context loading.
- Do not make every review heavy.
- Do not rewrite validator scripts in v1.
- Do not introduce incompatible report format changes.

## Requirements
### Functional
- Reviewer documentation must state that finding one obvious issue is not sufficient to stop review.
- Reviewer must continue looking for other critical and major issues across the artifact's relevant rubric categories before final verdict.
- Reviewer must use a bounded loop with at least these conceptual steps:
  - reconstruct source goal/root objective;
  - audit artifact framing for bias, incompleteness, or misplaced optimization;
  - derive rubric from live contracts and source evidence;
  - scan relevant risk surfaces;
  - record direct evidence, inference, and uncertainty separately when material;
  - decide whether more evidence is required, route escalation is required, or convergence is justified;
  - issue exactly one final reviewer verdict.
- Reviewer must define a PASS convergence statement in `Residual Risks` or `Recheck Plan`, naming the main surfaces checked and any route-limited uncertainty.
- Reviewer must define that `REVISE` and `BLOCK` should still report all known critical/major findings discovered during the bounded pass, not stop at the first.
- Reviewer must preserve max-findings semantics: caps may limit minor/nit output after critical issues are included, but may not hide critical findings.
- Reviewer must make escalation explicit when the selected route cannot inspect enough evidence to judge the artifact fairly.

### Non-Functional
- Documentation should stay concise and avoid duplicating the full `introspector` workflow or schema.
- The change must be compatible with existing reviewer lite/heavy routes, report template, validation script, and consumer-skill contracts.
- The wording should reduce sycophancy and premature acceptance without making reviewer hostile or needlessly expensive.

## Constraints
- v1 is documentation/reference behavior only; no script or validator refactor is required.
- Existing reviewer output format and top-level verdicts must remain compatible.
- Reviewer remains a quality gate, not a replacement for `introspector` global-optimality review.
- Review loops must be bounded by route, evidence availability, and material risk.

## Assumptions To Validate
- [ ] `reviewer/references/review-report-template.md` can express convergence via existing sections such as `Review Basis`, `Recheck Plan`, and `Residual Risks` without schema changes - validate before implementation.
- [ ] `validate_review_report.py` will not require changes if the report shape is preserved - validate by running it on any updated sample/report if implementation adds one.
- [ ] The best v1 edit location is `reviewer/SKILL.md` plus possibly one reference doc - validate by reading current reviewer references during planning.

## Risks
- Overcorrecting into heavy-review-by-default - mitigate by preserving route preflight and bounded evidence rules.
- Copying too much `introspector` semantics - mitigate by importing principles, not verdict taxonomy or full schema.
- Creating vague "keep searching" language that agents ignore - mitigate with explicit convergence and risk-surface requirements.
- Making review impossible to finish - mitigate with bounded loop, route limits, and `BLOCK` when evidence is insufficient.
- Report template incompatibility - mitigate by using existing sections unless implementation proves a schema update is needed.

## Acceptance Checks
- Read `/data/lcq/.codex/skills/reviewer/SKILL.md` and confirm it explicitly forbids stopping after the first obvious issue.
- Confirm reviewer guidance requires a bounded discovery/convergence step before `PASS`.
- Confirm reviewer guidance imports neutral evidence-first principles from `introspector` without copying its verdict taxonomy.
- Confirm lite/heavy route rules still allow cheap low-risk review and escalation for material risk.
- Confirm existing report template compatibility is preserved, or any schema change is explicitly justified and validator-compatible.
- Run focused validation after implementation, at minimum:
  - `python3 reviewer/scripts/validate_review_report.py <representative-report.md>` when a report fixture exists or is updated.
  - Any project-owned skill validation used for reviewer changes, if available in the implementation plan.

## Open Questions
- Should implementation add a named reference section such as "Issue Discovery Loop", or keep the change entirely in `SKILL.md`?
- Should reviewer report template gain an explicit "Convergence" field, or should existing `Residual Risks`/`Recheck Plan` sections carry that information?
