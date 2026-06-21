---
name: plan2do
description: Execute an existing spec2plan-generated plan.md with quality gates, review, bounded rework, artifact reporting, and context hygiene. Use when Codex needs to implement, execute, run, complete, or finish a plan; when a user asks to turn a plan.md into done work; when verification/review/rework discipline is needed; or when plan execution must keep the primary-agent context clean. Defaults to primary-agent execution; use codex2codex only when explicitly requested.
---

# Plan2Do

Execute a `spec2plan` `plan.md` to completion. Own mode selection, context hygiene, task execution, verification, review, rework guidance, and final acceptance.

## Resources

- Always read `references/execution-contract.md` before executing a plan or judging completion.
- Read `references/failure-policy.md` when verification, review, scope, tooling, or context checks fail.
- Read `references/review-rubric.md` before writing a review artifact or final acceptance.
- Use `scripts/compile_execution.py <plan.md>` to create `execution/tasks.json` for non-trivial primary-agent execution.
- Re-running `scripts/compile_execution.py` preserves existing task statuses; use `--reset-status` only when intentionally restarting execution.
- Use `scripts/validate_execution.py <plan-workspace>` before final success when `execution/tasks.json` exists.
- Use `scripts/pre_review_ready.py <plan-workspace> --stage draft --require-production-report --require-final-report` before launching a final reviewer for new skills, material skill changes, validator/script changes, workflow/safety changes, or metadata changes.
- Always use `/data/lcq/.codex/skills/context-engineering` for focused context, artifact quarantine, rehydration, decision packets, and context capsules.
- For plans that create or materially update skills, require a Skill Production Gate report validated by `skill-tokenless/scripts/validate_skill_production.py <report> --stage draft` before reviewer launch and `--stage final` before final success.
- Use `/data/lcq/.codex/skills/codex2codex` only when the user explicitly requests `codex2codex`.

## Intake

1. Locate the `plan.md`: use the user-provided path, or infer the current `.codex/work/<yyyyMMdd>-<topic>/plan.md` only when unambiguous.
2. Rehydrate the plan source-of-truth: `Goal`, `Task Breakdown`, `Step-by-Step Plan`, `Validation Plan`, `Rollback / Recovery Plan`, `Abort Criteria`, and `Execution Handoff`.
3. Confirm each executable task has acceptance criteria, verification, writable scope, output artifact, and dependency order.
4. For non-trivial plans, compile the plan with `scripts/compile_execution.py` and use `execution/tasks.json` as the execution checklist.
5. Stop before edits if the plan is invalid, ambiguous, or conflicts with the latest user instruction.

## Self-Bootstrap

If the plan creates or updates `plan2do` itself, do not claim the skill was available before its `SKILL.md` existed. Use the confirmed spec/plan as the bootstrap contract, create the skill, then re-read `plan2do/SKILL.md` and `references/execution-contract.md` before continuing under this skill.

## Mode Selection

- Default: primary-agent execution.
- Use `codex2codex` only when the user explicitly says `codex2codex`, asks for worker isolation, or names that backend.
- In both modes, the primary agent owns final acceptance and must not report completion after failed verification or failed review.

## Primary-Agent Workflow

1. Use `context-engineering` gate rules for context packs: write one wave-level pack by default for a coherent non-trivial wave, and write task-level packs only for risk, ambiguity, failure, confidence loss, or cross-cutting scope.
2. Execute tasks in dependency order, respecting writable scope and preserving unrelated dirty work.
3. Store large logs, raw diffs, review notes, context packs, and execution summaries under the plan workspace `artifacts/`.
4. Run task verification from the plan whenever safe.
5. Review changed behavior for functional completeness, regression risk, architecture simplicity, and over-engineering.
6. If review or verification fails, write primary-agent rework guidance before fixing.
7. Repeat bounded rework, then validate `execution/tasks.json` artifacts when present.
8. Either pass or stop with a blocker report.

## Codex2Codex Workflow

When explicitly requested, compile/run through `codex2codex` using the plan path. Keep worker transcripts out of active context; accept only artifact summaries, review verdicts, validation status, and blockers. The primary agent still writes rework guidance and final acceptance.

## Quality Gates

Completion requires:

- all required plan tasks completed or explicitly blocked;
- acceptance criteria satisfied;
- verification commands passed, or blocked with concrete cause;
- review `PASS` for non-trivial plans, or documented review exemption;
- Skill Production Gate report validated for new skills, material skill changes, validator/script changes, workflow/safety changes, or metadata changes;
- pre-review readiness passes before launching final reviewer when the plan has `execution/tasks.json`;
- no known functional gaps, material regressions, or unnecessary architecture complexity;
- final report with mode, tasks, changed files, verification, review verdict, rework cycles, artifacts, blockers, and omitted raw data.
- `scripts/validate_execution.py <plan-workspace>` passes when `execution/tasks.json` exists.

False completion is forbidden: failing verification, failed review, missing artifacts, repeated unresolved failures, or unresolved user approval needs must stop as incomplete.

## Rework

Use at most two fix cycles per failed task or review scope unless the user changes the limit. Before each cycle, write rework guidance that names the evidence, defect, required change, writable scope, and verification. If the same issue persists after the limit, stop with a blocker report.

## Completion

Finish with a concise report. Cite artifact paths instead of pasting raw logs or transcripts. State verification commands and outcomes exactly.
