# reviewer v2 Implementation Plan

Mode: light
Risk level: Medium
Confidence: High

## Goal

Implement `reviewer v2` from `.codex/work/20260621-reviewer-v2/spec.md`: add lite/heavy review routing, deterministic review report validation, reviewer subagent cleanup guidance, source-path evidence checks, realistic forward-test artifacts, and clearer `plan2do` verification evidence messaging.

## Non-Goals

- Do not create a separate `reviewer-lite` skill.
- Do not force `idea-refine`, `interview-me`, `spec2plan`, or `plan2do` to call `reviewer`.
- Do not change `plan2do` task status semantics or final-success semantics.
- Do not build a GitHub PR bot, daemon, scheduler, external service, or vendored third-party framework.
- Do not commit git changes.

## Evidence Inspected

- Confirmed spec: `.codex/work/20260621-reviewer-v2/spec.md`.
- Prior debug audit: `.codex/work/20260621-reviewer/artifacts/debug-skill-audit.md`.
- Current reviewer implementation: `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`, `reviewer/references/subagent-dispatch.md`, `reviewer/references/review-rubrics.md`.
- Current plan2do validator: `plan2do/scripts/validate_execution.py`.
- Current plan2do execution contract: `plan2do/references/execution-contract.md`.
- Skill creation guidance: `.system/skill-creator/SKILL.md`.
- Plan contract: `spec2plan/references/plan-contract.md`.
- Artifact contract: `spec2plan/references/artifact-contract.md`.
- Execution contract: `plan2do/references/execution-contract.md`.
- Review rubric: `plan2do/references/review-rubric.md`.
- Local repo status: `git status --short`.

## Spec Summary

`reviewer v2` keeps one `reviewer` skill while adding an internal route preflight that chooses `lite`, `heavy`, or `blocked`. Lite reviews stay inline by default for low-risk artifacts. Heavy reviews use isolated reviewer subagents by default for risky artifacts. Mandatory isolation can force subagent use for lite reviews. Reviewer reports must become machine-checkable through a Python validator. Reviewer subagents must be archived or killed after their synthesized report is collected. `plan2do` must clarify verification evidence expectations without changing behavior.

## Domain Language Check

- Canonical skill name: `reviewer`.
- Canonical routes: `lite`, `heavy`, `blocked`.
- Canonical verdicts: `PASS`, `REVISE`, `BLOCK`.
- Canonical sub-verdict labels for v2: `Alignment Result` and `Quality Result` instead of sub-section `Verdict` lines.
- Canonical reviewer options: `focus`, `max_findings`, `adversarial`, `save-review`, `no-commands`, `mandatory-isolation`.
- Canonical cleanup actions: archive or kill reviewer subagent, then retain only the synthesized report in main context.
- No term conflict found with current skill files.

## Current Context

The workspace contains a v1 `reviewer` skill and a confirmed v2 spec. `reviewer` currently has documentation-only behavior and no scripts directory. `plan2do/scripts/validate_execution.py` already checks final completion and verification evidence; the only intended plan2do change is clearer messaging or documentation around accepted verification evidence. Existing untracked work under `.codex/work/20260621-reviewer/`, `.codex/work/20260621-reviewer-v2/`, and `reviewer/` belongs to this reviewer workstream.

## Implementation Map

- Files:
  - `reviewer/SKILL.md`: route preflight, lite/heavy semantics, mandatory isolation, source evidence checks, validator guidance.
  - `reviewer/references/review-report-template.md`: v2 report schema and lite/heavy report shapes without verdict label ambiguity.
  - `reviewer/references/subagent-dispatch.md`: reviewer subagent lifecycle and cleanup guidance.
  - `reviewer/references/review-rubrics.md`: optional source-compliance and local-guidance checks if needed for report clarity.
  - `reviewer/scripts/validate_review_report.py`: deterministic report validator with embedded self-test fixtures.
  - `plan2do/scripts/validate_execution.py`: clearer error text for missing verification evidence.
  - `plan2do/references/execution-contract.md`: concrete examples of acceptable verification evidence.
  - `.codex/work/20260621-reviewer-v2/artifacts/`: task evidence, forward-test reports, review output, and final report.
- Symbols / APIs:
  - New CLI: `python3 reviewer/scripts/validate_review_report.py <report.md>`.
  - New CLI self-test: `python3 reviewer/scripts/validate_review_report.py --self-test`.
  - Existing validator function impacted only by error message: `_verification_evidence` and the missing-verification error in `plan2do/scripts/validate_execution.py`.
- Tests:
  - Embedded validator self-test fixtures for valid lite, valid heavy, missing top-level verdict, duplicate top-level verdict, invalid route, invalid severity, missing major evidence, missing local source, and `PASS` with major finding.
  - Skill validator: `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`.
  - Plan2do validator smoke on existing reviewer-v2 workspace after final report exists.
- Commands:
  - `python3 reviewer/scripts/validate_review_report.py --self-test`.
  - `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-reviewer-v2/artifacts/valid-lite-review.md`.
  - `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-reviewer-v2/artifacts/valid-heavy-review.md`.
  - `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`.
  - `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer-v2`.
- Data / migration impact: Not applicable because changes are local skill docs, a local validator script, and work artifacts. No user data, schema, network service, or deployment state changes.

## Assumptions

- Python 3 is available because existing skill validators use Python 3.
- Standard-library-only validation is sufficient for reviewer report structure.
- Reviewer subagent cleanup can be exercised through available subagent tooling; if unavailable, the forward-test artifact will record the concrete blocker and expected route.
- v2 validator may accept only v2 report schema for new reports while treating v1 reports as historical evidence.

## User Inputs Needed

No user input is needed before execution because the user explicitly approved the v2 spec and requested `spec2plan`, `plan2do`, and `reviewer` implementation.

## Proposed Approach

First implement the deterministic validator because it defines the report contract. Then update reviewer docs and templates to reference the v2 contract and routing rules. Then clarify plan2do verification evidence messaging. Then run validator self-tests, skill validation, and reviewer forward-tests. Finish with a reviewer audit and execution validation.

## Scenario Probes

- Low-risk lite review: a small documentation or metadata artifact should be classified `lite`, stay inline, avoid broad file reads, and pass the report validator.
- High-risk heavy review: a plan or code-behavior artifact should be classified `heavy`, use a reviewer subagent when available, and record cleanup result.
- Mandatory isolation lite review: a small artifact with `mandatory-isolation` should use a subagent when available or return `BLOCK` if mandatory isolation cannot be satisfied.
- Source path check: a report citing a missing local path as evidence should fail unless the source is explicitly marked missing or unavailable.
- Plan2do evidence clarity: missing verification evidence should produce an error that names `*verification*.md` and `Verification` line examples.

## Dependency Graph

- Task 1 creates the validator contract needed by Tasks 2 and 4.
- Task 2 updates reviewer instructions and report schema to match the validator.
- Task 3 clarifies plan2do verification evidence and is independent of Task 2 after Task 1 exists.
- Task 4 depends on Tasks 1-3 because it validates both reviewer v2 behavior and plan2do messaging.
- Task 5 depends on all implementation and validation tasks.

## Task Breakdown

### Task 1: Add reviewer report validator

- Description: Create `reviewer/scripts/validate_review_report.py` with standard-library parsing for v2 lite/heavy reports, evidence checks, severity/verdict consistency, route validation, source-path existence checks, and embedded self-test fixtures.
- Worker role: coding
- Wave: 1
- Acceptance criteria: `reviewer/scripts/validate_review_report.py` exists, is executable through `python3`, validates good lite/heavy fixtures, rejects malformed fixtures, and uses no external dependencies.
- Verification: Run `python3 reviewer/scripts/validate_review_report.py --self-test`.
- Concrete edits: Add `reviewer/scripts/validate_review_report.py` and write `.codex/work/20260621-reviewer-v2/artifacts/task1-validator.md`.
- Interfaces / contracts changed: New local CLI `reviewer/scripts/validate_review_report.py`.
- Test cases: Valid lite report, valid heavy report, missing top-level verdict, duplicate top-level verdict, invalid route, invalid severity, missing major evidence, missing local source, `PASS` with major finding.
- Pre-check commands: Run `test ! -e reviewer/scripts/validate_review_report.py`.
- Post-check commands: Run `python3 reviewer/scripts/validate_review_report.py --self-test`.
- Dependencies: None.
- Files likely touched: `reviewer/scripts/validate_review_report.py`, `.codex/work/20260621-reviewer-v2/artifacts/task1-validator.md`.
- Writable scope: `reviewer/scripts/validate_review_report.py`, `.codex/work/20260621-reviewer-v2/artifacts/task1-validator.md`.
- Output artifact: `.codex/work/20260621-reviewer-v2/artifacts/task1-validator.md`.
- Estimated scope: M

### Task 2: Update reviewer v2 workflow docs

- Description: Update reviewer instructions and references for preflight route selection, lite/heavy report schema, mandatory isolation, source existence checks, subagent cleanup, and validator usage.
- Worker role: coding
- Wave: 2
- Acceptance criteria: `reviewer/SKILL.md` describes `lite`, `heavy`, and `blocked` preflight; `review-report-template.md` removes ambiguous sub-section `Verdict:` labels; `subagent-dispatch.md` requires archive or kill cleanup after report collection; all validator references point to `reviewer/scripts/validate_review_report.py`.
- Verification: Run `grep -R "Alignment Verdict\\|Quality Verdict" -n reviewer/SKILL.md reviewer/references/review-report-template.md reviewer/references/subagent-dispatch.md || true` and verify no v2 template uses those ambiguous headings; run `python3 reviewer/scripts/validate_review_report.py --self-test`.
- Concrete edits: Patch `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`, and `reviewer/references/subagent-dispatch.md`; write `.codex/work/20260621-reviewer-v2/artifacts/task2-reviewer-docs.md`.
- Interfaces / contracts changed: Reviewer report schema changes from v1 to v2 for new reports.
- Test cases: Validator self-test fixtures remain green after docs changes.
- Pre-check commands: Run `sed -n '1,220p' reviewer/SKILL.md` and `sed -n '1,180p' reviewer/references/review-report-template.md`.
- Post-check commands: Run `python3 reviewer/scripts/validate_review_report.py --self-test` and `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`.
- Dependencies: Task 1.
- Files likely touched: `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`, `reviewer/references/subagent-dispatch.md`, `.codex/work/20260621-reviewer-v2/artifacts/task2-reviewer-docs.md`.
- Writable scope: `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`, `reviewer/references/subagent-dispatch.md`, `.codex/work/20260621-reviewer-v2/artifacts/task2-reviewer-docs.md`.
- Output artifact: `.codex/work/20260621-reviewer-v2/artifacts/task2-reviewer-docs.md`.
- Estimated scope: M

### Task 3: Clarify plan2do verification evidence

- Description: Clarify accepted verification evidence in `plan2do` docs and validator error text without changing validator semantics.
- Worker role: coding
- Wave: 3
- Acceptance criteria: `plan2do/references/execution-contract.md` names concrete accepted verification evidence examples, and `plan2do/scripts/validate_execution.py` missing-verification error names the same examples while preserving `_verification_evidence` behavior.
- Verification: Run `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer` and confirm it still returns `VALID`.
- Concrete edits: Patch `plan2do/references/execution-contract.md` and the missing-verification error string in `plan2do/scripts/validate_execution.py`; write `.codex/work/20260621-reviewer-v2/artifacts/task3-plan2do-message.md`.
- Interfaces / contracts changed: Human-facing documentation and error text only.
- Test cases: Existing successful reviewer execution workspace remains valid.
- Pre-check commands: Run `grep -n "missing verification evidence\\|Verification section" plan2do/scripts/validate_execution.py plan2do/references/execution-contract.md`.
- Post-check commands: Run `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer`.
- Dependencies: Task 1.
- Files likely touched: `plan2do/references/execution-contract.md`, `plan2do/scripts/validate_execution.py`, `.codex/work/20260621-reviewer-v2/artifacts/task3-plan2do-message.md`.
- Writable scope: `plan2do/references/execution-contract.md`, `plan2do/scripts/validate_execution.py`, `.codex/work/20260621-reviewer-v2/artifacts/task3-plan2do-message.md`.
- Output artifact: `.codex/work/20260621-reviewer-v2/artifacts/task3-plan2do-message.md`.
- Estimated scope: S

### Task 4: Run reviewer v2 forward tests

- Description: Create forward-test review artifacts for lite inline, heavy subagent, and mandatory-isolation behavior; validate each generated report with the new validator and record subagent cleanup result.
- Worker role: coding
- Wave: 4
- Acceptance criteria: `valid-lite-review.md` passes validator, `valid-heavy-review.md` passes validator, mandatory-isolation behavior is recorded, and a cleanup status is recorded for every reviewer subagent launched by this task.
- Verification: Run `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-reviewer-v2/artifacts/valid-lite-review.md` and `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-reviewer-v2/artifacts/valid-heavy-review.md`.
- Concrete edits: Write `.codex/work/20260621-reviewer-v2/artifacts/valid-lite-review.md`, `.codex/work/20260621-reviewer-v2/artifacts/valid-heavy-review.md`, `.codex/work/20260621-reviewer-v2/artifacts/mandatory-isolation-review.md`, `.codex/work/20260621-reviewer-v2/artifacts/task4-forward-tests.md`.
- Interfaces / contracts changed: Not applicable because this task writes evidence artifacts only.
- Test cases: Lite inline report, heavy subagent report, mandatory-isolation report or blocked note when isolation is unavailable.
- Pre-check commands: Run `python3 reviewer/scripts/validate_review_report.py --self-test`.
- Post-check commands: Run validator commands for lite and heavy reports; run `grep -n "Cleanup" .codex/work/20260621-reviewer-v2/artifacts/task4-forward-tests.md`.
- Dependencies: Tasks 1, 2, and 3.
- Files likely touched: `.codex/work/20260621-reviewer-v2/artifacts/valid-lite-review.md`, `.codex/work/20260621-reviewer-v2/artifacts/valid-heavy-review.md`, `.codex/work/20260621-reviewer-v2/artifacts/mandatory-isolation-review.md`, `.codex/work/20260621-reviewer-v2/artifacts/task4-forward-tests.md`.
- Writable scope: `.codex/work/20260621-reviewer-v2/artifacts/valid-lite-review.md`, `.codex/work/20260621-reviewer-v2/artifacts/valid-heavy-review.md`, `.codex/work/20260621-reviewer-v2/artifacts/mandatory-isolation-review.md`, `.codex/work/20260621-reviewer-v2/artifacts/task4-forward-tests.md`.
- Output artifact: `.codex/work/20260621-reviewer-v2/artifacts/task4-forward-tests.md`.
- Estimated scope: M

### Task 5: Final validation and reviewer audit

- Description: Run complete validation for reviewer v2, perform a final reviewer audit, write final execution artifacts, and validate plan2do execution state.
- Worker role: review
- Wave: 5
- Acceptance criteria: Skill quick validation passes, reviewer report validator self-test passes, final reviewer audit returns `PASS`, `execution/tasks.json` marks all tasks complete, and `validate_execution.py` returns `VALID`.
- Verification: Run `python3 reviewer/scripts/validate_review_report.py --self-test`, `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`, and `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer-v2`.
- Concrete edits: Write `.codex/work/20260621-reviewer-v2/review.md`, `.codex/work/20260621-reviewer-v2/artifacts/task5-validation.md`, `.codex/work/20260621-reviewer-v2/artifacts/task5-verification.md`, and `.codex/work/20260621-reviewer-v2/artifacts/final-report.md`.
- Interfaces / contracts changed: Not applicable because this task validates completed work.
- Test cases: Final audit checks validator, report schema, lite/heavy routing, subagent cleanup, source evidence handling, and plan2do message clarity.
- Pre-check commands: Run `python3 reviewer/scripts/validate_review_report.py --self-test` and `git status --short`.
- Post-check commands: Run `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer-v2`.
- Dependencies: Task 4.
- Files likely touched: `.codex/work/20260621-reviewer-v2/review.md`, `.codex/work/20260621-reviewer-v2/artifacts/task5-validation.md`, `.codex/work/20260621-reviewer-v2/artifacts/task5-verification.md`, `.codex/work/20260621-reviewer-v2/artifacts/final-report.md`.
- Writable scope: `.codex/work/20260621-reviewer-v2/review.md`, `.codex/work/20260621-reviewer-v2/artifacts/task5-validation.md`, `.codex/work/20260621-reviewer-v2/artifacts/task5-verification.md`, `.codex/work/20260621-reviewer-v2/artifacts/final-report.md`.
- Output artifact: `.codex/work/20260621-reviewer-v2/review.md`.
- Estimated scope: M

## Step-by-Step Plan

1. Read `.codex/work/20260621-reviewer-v2/spec.md`, `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`, `reviewer/references/subagent-dispatch.md`, and `plan2do/scripts/validate_execution.py`.
2. Add `reviewer/scripts/validate_review_report.py` with CLI parsing, report parsing, source-path checks, severity/verdict checks, and `--self-test`.
3. Run `python3 reviewer/scripts/validate_review_report.py --self-test` and write `.codex/work/20260621-reviewer-v2/artifacts/task1-validator.md`.
4. Patch `reviewer/references/review-report-template.md` to define v2 top-level verdict, route, mode, alignment result, and quality result without ambiguous sub-verdict labels.
5. Patch `reviewer/SKILL.md` to add preflight routing, lite/heavy route rules, mandatory isolation, validator usage, and source-existence behavior.
6. Patch `reviewer/references/subagent-dispatch.md` to add dispatch, collect, archive or kill cleanup, cleanup evidence, and fallback handling.
7. Run `python3 reviewer/scripts/validate_review_report.py --self-test` and `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`; write `.codex/work/20260621-reviewer-v2/artifacts/task2-reviewer-docs.md`.
8. Patch `plan2do/scripts/validate_execution.py` missing-verification error string and `plan2do/references/execution-contract.md` final-acceptance evidence guidance.
9. Run `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer`; write `.codex/work/20260621-reviewer-v2/artifacts/task3-plan2do-message.md`.
10. Create `.codex/work/20260621-reviewer-v2/artifacts/valid-lite-review.md` and validate it with `python3 reviewer/scripts/validate_review_report.py .codex/work/20260621-reviewer-v2/artifacts/valid-lite-review.md`.
11. Launch one reviewer subagent for a heavy review fixture when subagent tooling is available; save `.codex/work/20260621-reviewer-v2/artifacts/valid-heavy-review.md`, then archive or kill that subagent and record cleanup in `.codex/work/20260621-reviewer-v2/artifacts/task4-forward-tests.md`.
12. Exercise mandatory-isolation behavior with `.codex/work/20260621-reviewer-v2/artifacts/mandatory-isolation-review.md` or record a `BLOCK` reason when mandatory isolation cannot be satisfied.
13. Run validator commands for lite and heavy review artifacts; write `.codex/work/20260621-reviewer-v2/artifacts/task4-forward-tests.md`.
14. Run final validation commands, perform a final reviewer audit, and write `.codex/work/20260621-reviewer-v2/review.md`.
15. Write `.codex/work/20260621-reviewer-v2/artifacts/task5-validation.md`, `.codex/work/20260621-reviewer-v2/artifacts/task5-verification.md`, and `.codex/work/20260621-reviewer-v2/artifacts/final-report.md`.
16. Run `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer-v2`.

## Parallelization

Tasks are sequential. Task 1 defines the validator contract. Task 2 depends on that contract. Task 3 is semantically independent but follows Task 1 so its validation artifact can use the same execution workspace. Task 4 depends on reviewer v2 docs and validator behavior. Task 5 depends on all implementation and forward-test evidence.

## Files / Components Likely Affected

- `reviewer/SKILL.md`
- `reviewer/references/review-report-template.md`
- `reviewer/references/subagent-dispatch.md`
- `reviewer/scripts/validate_review_report.py`
- `plan2do/scripts/validate_execution.py`
- `plan2do/references/execution-contract.md`
- `.codex/work/20260621-reviewer-v2/plan.md`
- `.codex/work/20260621-reviewer-v2/execution/tasks.json`
- `.codex/work/20260621-reviewer-v2/artifacts/*.md`
- `.codex/work/20260621-reviewer-v2/review.md`

## Owners / Responsibilities

- Primary agent: writes code/docs/artifacts, runs validation, preserves user work, and owns final acceptance.
- Reviewer subagent: performs heavy review forward-test and final reviewer audit when launched.
- User: no action during execution unless a blocker requires a product decision or tool permission.

## Validation Plan

- Validate plan before execution: `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer-v2/plan.md --mode light`.
- Compile execution checklist: `python3 /data/lcq/.codex/skills/plan2do/scripts/compile_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer-v2/plan.md`.
- Validate reviewer script: `python3 reviewer/scripts/validate_review_report.py --self-test`.
- Validate reviewer skill: `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer`.
- Validate lite and heavy reports with `reviewer/scripts/validate_review_report.py`.
- Validate prior reviewer v1 execution remains valid: `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer`.
- Validate final execution: `python3 /data/lcq/.codex/skills/plan2do/scripts/validate_execution.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer-v2`.

## Rollout Plan

No deployment rollout is needed. The updated local skills become available from `/data/lcq/.codex/skills/reviewer` and `/data/lcq/.codex/skills/plan2do` after files are saved.

## Monitoring / Observability

Use validator command output, task artifacts under `.codex/work/20260621-reviewer-v2/artifacts/`, reviewer audit output at `.codex/work/20260621-reviewer-v2/review.md`, and final execution validation as observability evidence.

## Documentation / ADR Updates

ADR: Not needed. The changes are local skill workflow/documentation plus a local validation script. Update `reviewer` references and `plan2do` execution contract because workflow behavior and validation guidance change.

## Rollback / Recovery Plan

If implementation fails before final acceptance, revert only plan-owned changes in `reviewer/SKILL.md`, `reviewer/references/review-report-template.md`, `reviewer/references/subagent-dispatch.md`, `reviewer/scripts/validate_review_report.py`, `plan2do/scripts/validate_execution.py`, `plan2do/references/execution-contract.md`, and `.codex/work/20260621-reviewer-v2/` after confirming no user edits exist in those paths. If a validator fails, patch the smallest failing file and rerun that validator plus cheap regression checks.

## Abort Criteria

- Abort if an unexpected user edit appears inside the writable scope and conflicts with the planned change.
- Abort if `reviewer/scripts/validate_review_report.py --self-test` cannot pass without weakening acceptance checks.
- Abort if reviewer subagent cleanup cannot be attempted and the heavy forward-test cannot record a concrete cleanup blocker.
- Abort if final reviewer audit returns `BLOCK`.
- Abort if plan validation or execution validation cannot pass after two bounded rework cycles.

## Risks

- Validator rigidity may reject useful reports; mitigate by validating only structural safety invariants.
- Lite routing may under-review risky artifacts; mitigate with conservative escalation rules and `BLOCK` on unclear source authority.
- Subagent cleanup support may vary by tool; mitigate by recording archive or kill result and residual risk.
- Changing report labels can make v1 reports historical-only; mitigate by documenting v2 schema and using new validator for new reports.
- Plan2do error text changes could accidentally alter semantics; mitigate by changing only message text and validating existing successful execution workspace.

## Open Questions

- The v2 validator will validate v2 reports for new work; v1 reports remain historical evidence and are not required to pass v2 validation.
- Cleanup will use archive when available and kill when archive is unavailable or ineffective; the cleanup action will be recorded.
- `mandatory-isolation` will be accepted as both a review option and a dispatch packet field.

## Plan Self-Review

- Every task has exact writable scope and tasks are sequential, so same-wave write overlap is absent.
- Behavior changes have validator self-tests, skill validation, lite/heavy report validation, plan2do regression validation, and final reviewer audit coverage.
- Unknowns are recorded in `Assumptions` or `Open Questions`, not hidden in task text.
- Rollback and abort criteria identify exact files and failure classes.
- A fresh agent can execute Task 1 by reading this plan, the spec, and current reviewer files without raw chat context.

## Execution Decision

Proceed with primary-agent `plan2do` execution. The work is local, reversible, and medium-risk because it changes skill behavior and validation scripts but does not affect runtime services or user data.

## Execution Handoff

- Goal: Implement `reviewer v2` from `.codex/work/20260621-reviewer-v2/spec.md`.
- Current state: Spec exists; plan is ready for validation; reviewer v1 exists without scripts directory.
- Authoritative artifacts: `.codex/work/20260621-reviewer-v2/spec.md`, `.codex/work/20260621-reviewer-v2/plan.md`, `.codex/work/20260621-reviewer-v2/manifest.yaml`.
- Decisions: Use one `reviewer` skill with internal lite/heavy routes; add a standard-library validator; clarify plan2do evidence text only; validate with reviewer.
- Verification: Plan validator, execution compiler, reviewer validator self-test, skill quick validation, lite/heavy report validation, plan2do validation, final reviewer audit.
- Remaining risks: Subagent cleanup support depends on available tooling; v1 reports are historical and may not pass v2 schema.
- Next action: Run `python3 /data/lcq/.codex/skills/spec2plan/scripts/validate_plan_contract.py /data/lcq/.codex/skills/.codex/work/20260621-reviewer-v2/plan.md --mode light`.
- Suggested skills: `plan2do`, `reviewer`, `test-driven-development`, `edit-orchestration`, `context-engineering`.
- Redactions / omitted raw data: Raw prior subagent transcripts and long command outputs are omitted; artifact paths and validation commands are retained.
