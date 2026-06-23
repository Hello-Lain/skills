# Skill Production Report

- Skill: `reviewer`
- Change Type: material-update
- Verdict: PASS

## Behavior Lock
- Preserved: reviewer trigger scope, `PASS|REVISE|BLOCK` verdicts, lite/heavy/blocked route preflight, v2 report shape, report validation command, subagent safety rules, consumer lite-gate contract, `max_findings` critical-finding behavior, read-only review safety.
- Changed intentionally: added neutral artifact-as-candidate framing, source-goal optimization, framing audit, bounded issue discovery, explicit prohibition on stopping after one obvious issue, PASS convergence basis, and all-known critical/major reporting for `REVISE`/`BLOCK`.
- Fallbacks: if evidence is insufficient, reviewer escalates route or returns `BLOCK`; if mandatory isolation cannot be satisfied, reviewer returns `BLOCK`.

## Token Budget
- Before: `reviewer/SKILL.md` 160 lines.
- After: `reviewer/SKILL.md` 166 lines and `reviewer/references/review-report-template.md` 64 lines.
- Moved to references: no new reference file; convergence uses existing `Recheck Plan` and `Residual Risks`.

## Deterministic Validators
- `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`: PASS
- `python3 reviewer/scripts/validate_review_report.py --self-test`: PASS
- `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260623-reviewer-neutral-iterative-review/plan.md --mode light`: PASS

## Scenario Gate
- Scenario: reviewer sees one obvious major issue in a spec/plan and is tempted to stop.
- RED/control: prior `reviewer/SKILL.md` required rubric and source/intrinsic quality review but did not explicitly say that finding one obvious issue is insufficient, did not require bounded issue discovery, and did not require PASS convergence wording.
- GREEN/retest: patched `reviewer/SKILL.md` now requires scanning every material rubric surface available in route, continuing after one obvious finding, reporting all known critical/major findings, and stating convergence in `Residual Risks` or `Recheck Plan`.
- Cleanup: not launched.

## Reviewer Gate
- Mode: heavy
- Route: inline
- Verdict: PASS
- Report: `.codex/work/20260623-reviewer-neutral-iterative-review/artifacts/review-final.md`
- Cleanup: not launched

## Reuse Attribution
| Source | URL | Borrowed idea | Component | Adoption | Target change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- |
| Introspector skill | local:/data/lcq/.codex/skills/introspector | candidate artifact, source-goal optimization, framing audit, evidence classes, bounded loop | reviewer workflow docs | adapted | neutral reviewer behavior and issue-discovery convergence | rejected verdict taxonomy and full report schema because reviewer must keep `PASS|REVISE|BLOCK` |
| Reviewer existing template | local:/data/lcq/.codex/skills/reviewer/references/review-report-template.md | `Recheck Plan` and `Residual Risks` sections | reviewer report shape | adapted | convergence evidence without schema expansion | rejected new `Convergence` field to preserve validator compatibility |

## Changed Files
- `reviewer/SKILL.md`
- `reviewer/references/review-report-template.md`

## Residual Risks
- Existing adjacent uncommitted reviewer diff about harness-policy inline-heavy fallback was preserved and not reverted.
