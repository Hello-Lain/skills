# Debug Skill Report: reviewer implementation workflow

## Verdict
- Impact: net-positive
- Confidence: high
- One-line reason: the skill stack produced a valid `reviewer` skill and caught material quality gaps before completion, but it paid extra latency/artifact cost and exposed two contract ambiguities.

## Evidence Used
- Skill files: `plan2do/SKILL.md`; `spec2plan/SKILL.md`; `.system/skill-creator/SKILL.md`; `context-engineering/SKILL.md`; `edit-orchestration/SKILL.md`; `reviewer/SKILL.md`; `debug-skill/SKILL.md`.
- Conversation / trace: visible tool timeline from the previous turn, including source rehydration, `apply_patch` edits, validators, reviewer subagents, rework, and final validation.
- Artifacts / diffs: `.codex/work/20260621-reviewer/spec.md`; `.codex/work/20260621-reviewer/plan.md`; `execution/tasks.json`; `artifacts/task*.md`; `artifacts/rework-guidance-1.md`; `artifacts/dry-review-evidence.md`; `review.md`; `artifacts/final-report.md`.
- Commands / validation: `quick_validate.py` -> `Skill is valid!`; `validate_execution.py` initially failed for missing `*verification*.md`, then passed with `VALID`; `grep` checks for frontmatter, metadata, `$reviewer`, and placeholders.
- External reuse sources: Superpowers subagent-driven development; Superpowers issue #1120; PR-Agent/Qodo ticket-context review docs; OpenHands PR-review docs; local `debug-skill/references/hermes-reuse.md`.
- Missing evidence: raw full subagent transcripts are not saved as artifacts; spec2plan's original plan-generation turn predates this trace and is inferred from plan/manifest artifacts; reviewer dry reviews used fixtures, not real user production artifacts.

## Execution Trace
1. Trigger: user requested `spec2plan` + `plan2do` implementation of confirmed `reviewer` spec, then reviewer audit.
2. Skill instructions loaded: `plan2do`, `context-engineering`, `skill-creator`, `edit-orchestration`, later `reviewer`; `spec2plan` evidence came from existing `plan.md`.
3. Decisions: primary-agent execution; preserve upstream skills; scaffold `reviewer`; keep review mode read-only; use isolated reviewer subagents where available.
4. Actions: completed scaffold, wrote `SKILL.md`, references, metadata, task artifacts, dry-review fixtures/evidence, final report, and execution state.
5. Failures / friction: generated metadata initially lost `$reviewer`; initial reviewer audit returned `REVISE`; dry-run subagent stalled before writing; `validate_execution.py` failed until `task5-verification.md` existed; `review.md` briefly cited a nonexistent local `AGENTS.md`.
6. Recovery: patched metadata; wrote `rework-guidance-1.md`; added review options/adversarial/recheck/feedback-validity sections; removed fixture answer leakage; reran reviewer; added verification artifact; corrected false source citation.
7. Verification: final `quick_validate.py` passed, final reviewer recheck passed, final `validate_execution.py` passed.
8. Result: `reviewer/` implemented with direct references and `.codex/work/20260621-reviewer/` contains execution evidence.

## Effectiveness
- Quality: high. Reviewer caught substantive spec gaps that the implementer missed.
- Efficiency: medium. Multiple subagent waits and fixture generation added latency; likely justified for creating a new review skill, but too heavy for routine docs-only edits.
- Evidence use: high. Source files, validators, execution artifacts, and reviewer findings were rehydrated before acceptance.
- Context handling: medium-high. Raw subagent transcript stayed out of final report; one wave context artifact helped; however, several artifacts were created to satisfy validator mechanics rather than task understanding.
- Tooling: medium. `quick_validate.py` and `validate_execution.py` were useful hard gates; `validate_execution.py` error was correct but non-obvious because a `## Verification` heading did not satisfy its regex.
- Verification: high for structural quality; medium for behavioral generalization because dry reviews used fixtures.
- User friction: low. No unnecessary question was asked; progress updates were frequent.
- Reuse discipline: medium. The implementation reused patterns from mature projects in the spec, but the actual execution did not reuse a reusable report/schema validator for reviewer format beyond manual checks.

## Findings
- major: `reviewer` report contract has a verdict-count ambiguity. Evidence: `reviewer/references/review-report-template.md` says "Include exactly one top-level `Verdict:` line" while the template also uses `Verdict:` under alignment and quality verdicts; final `review.md` contains three `- Verdict: PASS` lines. Impact: scripts or humans may overcount verdicts, and validators like `validate_execution.py` can pass based on a sub-verdict if the top-level line is malformed.
- major: `plan2do` execution validator has an undocumented verification-evidence shape. Evidence: final report had `## Verification`, but `validate_execution.py` failed until `artifacts/task5-verification.md` existed because its regex expects a line beginning with `Verification` or a `*verification*.md` file. Impact: avoidable rework and possible false blocker for future agents.
- minor: Dry-review acceptance evidence was fixture-based, not real-world forward-testing. Evidence: `artifacts/dry-review-fixtures.md` and `artifacts/dry-review-evidence.md`; final `review.md` lists this as residual risk. Impact: good smoke coverage, but weaker evidence that `reviewer` generalizes under real user context.
- minor: A transient false citation reached `review.md`. Evidence: final validation found `/data/lcq/.codex/skills/AGENTS.md` missing, then patched `review.md` to "user-provided AGENTS instructions." Impact: recovered before final report, but shows source-basis fields need existence checks.
- minor: Review overhead was high for part of the task. Evidence: two reviewer subagents plus one dry-run subagent, repeated waits, dry fixtures, and recheck loop. Impact: acceptable for a review skill bootstrap, but should not become default for simple mechanical edits.

## Reuse Search
- Defect: verdict/schema ambiguity, heavyweight review loops, weak ticket/source alignment, and skill self-improvement gates.

| Source project/repo | Source link | Mature signal | Borrowed idea | Reusable component/CLI/schema | Adoption mode | Target skill change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `obra/superpowers` subagent-driven development | https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md | explicit task review model, fresh subagents, spec + quality verdicts | keep isolated reviewers and dual quality axes, but require complete review package | `scripts/review-package` concept is reusable as a pattern | adapted | add a reviewer report/schema validator or package checklist | direct import rejected; harness-specific and broader than this skill |
| `obra/superpowers` issue #1120 | https://github.com/obra/superpowers/issues/1120 | real user cost report on review loops | complexity gate before full review loop; combine or skip review for mechanical tasks | no component; issue-derived pattern | pattern-only | add complexity gate to `reviewer` or `plan2do` recheck guidance | no direct component |
| PR-Agent/Qodo ticket context | https://docs.pr-agent.ai/core-abilities/fetching_ticket_context/ | production PR-review tool with ticket compliance labels | explicit source/ticket compliance axis and unrelated-content check | config options such as `require_ticket_analysis_review` and `check_pr_additional_content` | pattern-only | add optional source-compliance labels or review options in reviewer config later | direct dependency rejected; PR-specific and service-oriented |
| OpenHands PR review workflow | https://docs.openhands.dev/sdk/guides/github-workflows/pr-review | official workflow docs; label/reviewer triggers; custom skill hook | on-demand review trigger plus repo-local custom review skill | GitHub workflow template is reusable for PR contexts | adapted | keep reviewer on-demand and allow local guidance/custom skill as source | direct workflow rejected; current skill is local artifact review, not GitHub Actions |
| Hermes reuse mapping in `debug-skill` | `debug-skill/references/hermes-reuse.md` | existing local adaptation with self-test | evidence dataset, constraints, candidate fitness, redaction | `skill_audit_core.py` primitives | direct | use report skeleton and candidate scoring for skill audit | heavier GEPA/DSPy loop rejected without explicit optimization request |

- Search boundary: searched mature GitHub/official docs around Superpowers review loops, OpenHands PR review, PR-Agent/Qodo review configuration, and Hermes self-evolution patterns.
- No mature component found: no drop-in Codex `reviewer` report-schema validator found; best option is a small local script modeled after existing `validate_execution.py` and `skill_audit_core.py`.
- Reuse-to-candidate mapping: Candidate A draws from Superpowers + existing validators; Candidate B draws from Superpowers issue #1120; Candidate C draws from PR-Agent/OpenHands source-alignment triggers.

## Candidate Improvements
| Candidate | Target surface | Reuse source | Summary | Benefit | Risk | Fitness |
| --- | --- | --- | --- | --- | --- | --- |
| A | `reviewer/scripts/validate_review_report.py` plus SKILL.md reference | Superpowers review package pattern; local `validate_execution.py` | Add deterministic validator for exactly one top-level verdict, valid sub-verdicts, evidence fields, and severity/verdict consistency. | High quality gain; prevents report false-pass. | Low-medium maintenance; script must track template. | high |
| B | `reviewer/SKILL.md` Review Options | Superpowers issue #1120 | Add complexity gate: trivial/mechanical -> inline lightweight review; integration/design/high-risk -> subagent/adversarial. | High efficiency gain; reduces over-review. | Medium: under-review if classification too permissive. | high |
| C | `reviewer/references/review-rubrics.md` | PR-Agent/Qodo; OpenHands | Add optional source-compliance/unrelated-content checks and local-guidance discovery checklist. | Medium quality gain for specs/plans/code reviews. | Low; mostly reference guidance. | medium |

## Recommendation
- Recommended action: no immediate mutation; next approved iteration should implement Candidate A first, then Candidate B.
- Target files: `reviewer/SKILL.md`; `reviewer/references/review-report-template.md`; optional `reviewer/scripts/validate_review_report.py`.
- Verification: quick validate skill; run validator against current `review.md`, dry-review evidence, and intentionally malformed reports.
- Reuse rationale: deterministic report validation addresses the highest-impact ambiguity with low scope; complexity gating addresses the main efficiency defect documented by Superpowers users.
- Execute now: no; requires explicit user approval.
