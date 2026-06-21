# Debug Skill Report: reviewer-lite integration run

## Verdict
- Impact: mixed
- Confidence: high
- One-line reason: the skill chain produced a valid, reviewed implementation with strong evidence, but exposed avoidable friction in plan readiness modeling, reviewer path handling, production-report parsing, and debug-skill continuous tracing.

## Evidence Used
- Skill files: `spec2plan/SKILL.md`, `plan2do/SKILL.md`, `reviewer/SKILL.md`, `debug-skill/SKILL.md`, `skill-tokenless/SKILL.md`, `context-engineering/SKILL.md`, `edit-orchestration/SKILL.md`.
- Conversation / trace: user requested `spec2plan + plan2do + reviewer + debug-skill`; execution plan, patches, validations, reviewer subagent repair, final report.
- Artifacts / diffs: `.codex/work/20260621-reviewer-lite-gate/spec.md`, `.codex/work/20260621-reviewer-lite-gate/plan.md`, `.codex/work/20260621-reviewer-lite-gate/execution/tasks.json`, `.codex/work/20260621-reviewer-lite-gate/review.md`, `.codex/work/20260621-reviewer-lite-gate/artifacts/production-report.md`, `.codex/work/20260621-reviewer-lite-gate/artifacts/final-report.md`, `.codex/work/20260621-reviewer-lite-gate/artifacts/debug-skill-trace.md`.
- Commands / validation: `validate_plan_contract.py --mode light` -> VALID; `compile_execution.py` -> wrote `execution/tasks.json`; `validate_skill_production.py --stage draft/final` -> VALID; `pre_review_ready.py --stage draft/final` -> VALID; `validate_review_report.py` -> VALID; `validate_execution.py` -> VALID; quick_validate passed for five changed skills.
- External reuse sources: `https://github.com/obra/superpowers`, `https://github.com/plandex-ai/plandex`, `https://github.com/Aider-AI/aider`, `https://github.com/pre-commit/pre-commit`, `https://github.com/NousResearch/hermes-agent-self-evolution`.
- Missing evidence: exact hidden model reasoning is unavailable; initial reviewer subagent transcript is summarized via Paseo activity and final repaired review.

## Execution Trace
1. Trigger: user asked to execute the confirmed spec with `spec2plan`, `plan2do`, `reviewer`, while using `debug-skill` to track skill trajectory and optimization points.
2. Skill instructions loaded: `spec2plan`, `plan2do`, `reviewer`, `debug-skill`, plus support skills `skill-tokenless`, `context-engineering`, `edit-orchestration`.
3. Decisions: use light `spec2plan`; use primary-agent `plan2do`; require Skill Production Gate; route final review through heavy reviewer subagent.
4. Actions: created validated `plan.md`, compiled `tasks.json`, edited five skill entrypoints plus `reviewer/references/lite-gate-integration.md`, wrote task artifacts, production report, debug trace, and final report.
5. Failures / friction: long `rtk proxy cat` outputs were compressed; initial plan modeled finalization as a pending non-review task before reviewer; draft production-report validator flagged `BLOCK` inside a grep command; default reviewer provider `claude` was unavailable; first reviewer report used the wrong workspace path and returned false `REVISE`.
6. Recovery: re-read targeted ranges; repaired plan to satisfy `pre_review_ready.py`; reworded deterministic-validator command in production report; relaunched reviewer with `provider: codex`; sent one reviewer repair prompt with corrected absolute/cwd-relative paths.
7. Verification: all final validators passed; reviewer returned `PASS`; execution state is complete.
8. Result: implementation outcome is high quality, but the trajectory shows four reusable skill/tool improvement opportunities.

## Effectiveness
- Quality: high; final artifact satisfies spec and passed independent reviewer gate.
- Efficiency: medium; extra cycles came from preventable validator/modeling/path issues.
- Evidence use: high; final result cites spec, plan, execution state, production report, review, and validator outputs.
- Context handling: medium-high; focused context worked, but compressed command output forced extra targeted reads.
- Tooling: medium; validators caught real lifecycle problems, but one validator false-positive was caused by text scanning.
- Verification: high; all material gates passed.
- User friction: low; no extra user questions after spec confirmation.
- Reuse discipline: medium; pattern sources were recorded, but live external source review happened mostly after implementation, not continuously during execution.

## Findings
- major: `spec2plan`/plan contract under-specified pre-review task modeling. Evidence: initial plan had a post-review finalization Task 8, but `plan2do/scripts/pre_review_ready.py` draft mode allows only review tasks to remain pending. Impact: plan needed repair after execution began; a future agent could deadlock reviewer launch.
- major: `reviewer` subagent path handling caused a false critical finding. Evidence: first reviewer used `/data/lcq/.codex/work/20260621-reviewer-lite-gate/` instead of `/data/lcq/.codex/skills/.codex/work/20260621-reviewer-lite-gate/`, then claimed workspace artifacts were missing. Impact: false `REVISE` and one repair cycle.
- major: `skill-tokenless` production-report validator over-matched `BLOCK` in a command string. Evidence: draft report failed with `PASS production report cannot include BLOCK validator outcomes` because a grep regex contained `BLOCK`; removing the token from the command text made validation pass. Impact: validator can force wording workarounds and obscure real status parsing.
- minor: `debug-skill` has no explicit lightweight in-run trace mode. Evidence: useful trace was captured manually in `debug-skill-trace.md`, while full reuse search/report requirements are heavy for continuous execution. Impact: continuous tracking depends on operator discipline.
- minor: `rtk proxy cat` compression hid required lines in long skill files. Evidence: follow-up `sed -n` reads were needed for `spec2plan` and `reviewer`. Impact: extra context/tool cycles.
- minor: `reviewer` create-agent default provider mismatch. Evidence: `create_agent` with default provider failed: `No client registered for provider 'claude'`; explicit `provider: codex` worked. Impact: route execution friction outside reviewer core semantics.

## Reuse Search
- Defect: plan/reviewer workflows need reliable handoff, path evidence, and staged review readiness.

| Source project/repo | Source link | Mature signal | Borrowed idea | Reusable component/CLI/schema | Adoption mode | Target skill change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Superpowers | https://github.com/obra/superpowers | agent workflow repo focused on task/review handoffs | explicit task artifacts and final review handoff | no direct local component | pattern-only | Add reviewer packet path checklist and task-led final review discipline | runtime differs from Codex skills |
| Plandex | https://github.com/plandex-ai/plandex | established AI coding workflow with pending changes review | review generated changes before apply/accept | no direct local component | pattern-only | Keep reviewer gate before artifact authority, not after final reporting | product architecture differs |
| Aider | https://github.com/Aider-AI/aider | mature coding assistant with edit/test feedback loop | tight edit -> test -> repair loop | CLI exists but not needed for Markdown skill docs | rejected | Could inspire rework loop wording | adding CLI dependency is unnecessary |
| pre-commit | https://github.com/pre-commit/pre-commit | mature hook framework | deterministic gates should parse exact outcomes | hook schema/CLI | rejected | Improve production-report validator status parsing | framework is overkill; local parser fix is enough |
| Hermes Agent Self-Evolution | https://github.com/NousResearch/hermes-agent-self-evolution | upstream pattern already mapped in `debug-skill/references/hermes-reuse.md` | dataset/constraints/fitness/candidate promotion gates | local `skill_audit_core.py` adaptation exists | adapted | Add lightweight trace mode plus deep audit mode to `debug-skill` | direct dependency too heavy |

- Search boundary: GitHub/project pages for mature workflow patterns; no dependency adoption recommended.
- No mature component found: no direct component should replace local plan/reviewer validators; pattern-only adoption is enough.
- Reuse-to-candidate mapping: Superpowers/Plandex -> path and handoff hardening; pre-commit -> validator parsing discipline; Hermes -> trace/audit mode split.

## Candidate Improvements
| Candidate | Target surface | Reuse source | Summary | Benefit | Risk | Fitness |
| --- | --- | --- | --- | --- | --- | --- |
| A | `reviewer/references/subagent-dispatch.md` | Superpowers, Plandex | Require packets to include both cwd-relative and absolute artifact paths; reviewer must run `pwd`/path existence checks before claiming missing evidence. | Prevents false missing-artifact findings. | Slightly longer reviewer packets. | High |
| B | `plan2do/references/execution-contract.md` + `spec2plan/references/plan-contract.md` | Superpowers, pre-commit | State that pre-review draft readiness requires all non-review tasks complete; finalization after reviewer should be coordinator acceptance, not a pending non-review task. | Prevents reviewer-launch deadlocks and plan repair churn. | Needs precise wording to avoid blocking legitimate final report updates. | High |
| C | `skill-tokenless/scripts/validate_skill_production.py` | pre-commit | Parse validator outcomes from bullet result fields instead of scanning the entire deterministic validator section for `BLOCK`. | Removes false positives from command strings. | Script change needs self-test updates. | High |
| D | `debug-skill/SKILL.md` | Hermes Agent Self-Evolution | Add two modes: lightweight in-run trace artifact and final deep audit with external reuse search/candidate scoring. | Makes continuous tracking cheap while preserving rigorous final audits. | Could be skipped unless trigger wording is crisp. | Medium-high |

## Recommendation
- Recommended action: create a follow-up spec/plan for four targeted fixes; do not patch now without explicit approval.
- Target files: `reviewer/references/subagent-dispatch.md`, `plan2do/references/execution-contract.md`, `spec2plan/references/plan-contract.md`, `skill-tokenless/scripts/validate_skill_production.py`, `debug-skill/SKILL.md`.
- Verification: add/update self-tests for `validate_skill_production.py`; run reviewer report validation; run `spec2plan` plan validator on a fixture with final-review pending only; run debug-skill helper self-test.
- Reuse rationale: adopt workflow patterns only; direct external dependencies are not justified.
- Execute now: no; requires explicit user approval.
