---
name: spec2plan
description: "Convert specs, PRDs, issues, or clear requirements into executable, codex2codex-ready plan.md task plans. Use for implementation sequencing, dependency graphs, vertical slicing, worker/wave decomposition, acceptance criteria, validation planning, parallelization, or heavy production-grade planning. Heavy mode must invoke $codex2codex for meight-style worker coordination, QUESTION pushback, supervised review, rollback/monitoring scrutiny, and clean main-agent context. Replaces planning-and-task-breakdown and plan-grill."
---

# Spec2Plan

Turn a spec into an executable `plan.md`. Treat the plan as the source for codex2codex worker orchestration: every task must be small, dependency-ordered, vertically sliced where possible, and include worker role, wave, writable scope, verification, and output artifact. Do not implement during this skill unless the user explicitly asks after reviewing the plan.

## Mode

- Use `light` by default for clear specs, low-risk work, normal task breakdowns, or when the user wants speed.
- Use `heavy` when the user asks for heavy/production-grade planning, plan hardening, multi-worker coordination, clean context isolation, risky refactors, migrations, auth/billing/security, data/schema changes, CI/CD/infra, deployment/ops, rollback, unclear blast radius, or stakeholder-facing plans.
- If risk is ambiguous, choose `heavy`; if scope is tiny and safe, choose `light`.

## Resources

- Always read `references/plan-contract.md` before drafting or validating a plan.
- Before saving a plan or plan-adjacent artifact, read the shared artifact contract at `references/artifact-contract.md`.
- Read `references/discovery-routing.md` when the source artifact's maturity is ambiguous or the request may be an idea, direction, or incomplete spec rather than planning-ready requirements.
- For `heavy`, also read `references/heavy-mode.md` and load `$codex2codex` from `/data/lcq/.codex/skills/codex2codex`.
- Validate with `scripts/validate_plan_contract.py <plan.md> --mode light|heavy`; this hard gate also checks `plan2do/scripts/compile_execution.py` compatibility.
- Validate heavy worker artifacts with `scripts/validate_subagent_artifact.py <phase> <artifact.md>`.
- Validation is a hard gate: after drafting a candidate `plan.md`, run the validator; if it fails, revise the draft from the exact errors and rerun. Do not report, hand off, or treat a plan as saved-ready until validation passes.

## Discovery Routing Gate

Use `spec2plan` only after a confirmed spec or equivalent clear requirements exist. The upstream pipeline is:

```text
idea-refine -> interview-me -> spec2plan
```

- `idea-refine` chooses and stress-tests the direction; it is not a planning substitute.
- `interview-me` turns a chosen direction into a confirmed spec; it is not a planning substitute.
- If the input is an unconfirmed idea one-pager, weak direction, competing options, or a premature solution, do not draft a plan. Route through Discovery Routing to `idea-refine` or `interview-me` unless the user explicitly accepts recorded assumptions and asks to proceed.
- If requirements are mostly clear but not stored as a formal spec, ask only for the missing planning-critical facts or record explicit assumptions before planning.
- Do not hide unresolved product-direction or spec-quality gaps as implementation assumptions.

## Output

- Default light path: project-level `.codex/work/<yyyyMMdd>-<topic-slug>/plan.md` unless the user provides a path.
- Default heavy path: project-level `.codex/work/<yyyyMMdd>-<topic-slug>/plan.md` unless the user provides a path.
- If the source spec lives at `.codex/work/<yyyyMMdd>-<topic-slug>/spec.md`, reuse that topic workspace for the plan: `.codex/work/<yyyyMMdd>-<topic-slug>/plan.md`.
- If the source spec is outside the shared workspace, create or reuse `.codex/work/<yyyyMMdd>-<topic-slug>/`, record the external source path in `manifest.yaml`, and write the plan there unless the user provides a path.
- Keep per-phase heavy artifacts under `.codex/work/<yyyyMMdd>-<topic-slug>/subagents/`.
- Write plans, questions, and final responses in the user's language.
- Keep commands, paths, env vars, identifiers, package names, API names, and errors exact.

## Light Workflow

1. Read the spec plus enough nearby code/docs to avoid invented assumptions.
2. Map implementation evidence first: files, symbols/APIs, tests, commands, data impact, dependencies, vertical slices, task sizes, validation, risks, open questions, and safe parallel waves.
3. Main agent writes the plan directly.
4. Run `scripts/validate_plan_contract.py <plan.md> --mode light`, including execution compiler compatibility.
5. If validation fails, patch the draft from the validator errors and rerun step 4. Repeat until `VALID`, or stop with the exact blocking errors.
6. Report path, validation status, key risks/open questions, and that implementation was not executed.

## Heavy Workflow

1. Main agent inspects only enough context to build a compact task packet: objective, spec source, repo status, constraints, likely files/docs, output path, output language, redaction rules, executable plan fields, and `no implementation`.
2. Invoke `$codex2codex` inside a task subagent as the adaptive multi-agent shell; pass this skill's heavy-mode packet, contract, worker phases, validators, and artifact paths.
3. Require `$codex2codex` to coordinate read-only `planner`, `reviewer`, and `synthesizer` workers through supervised meight loops; it may add consult/arbiter workers if needed.
4. Save each terminal phase artifact under `.codex/work/<yyyyMMdd>-<topic-slug>/subagents/<phase>.md`, then validate: `scripts/validate_subagent_artifact.py <phase> <artifact.md>`.
5. Write `plan.md` from the synthesizer artifact body exactly; do not replace it with main-agent synthesis.
6. Run `scripts/validate_plan_contract.py <plan.md> --mode heavy`.
7. If validation fails, send the exact validator errors back through `$codex2codex` once for repair, rewrite `plan.md` from the repaired synthesizer output, and rerun step 6. If still invalid, stop before handoff with the exact blocking errors.
8. Report generated path, artifact dir, validation status, `$codex2codex` cleanup status, key risks/open questions, and that implementation/ops were not executed.

## Context Hygiene

- Keep raw specs, logs, diffs, and worker transcripts out of the final answer; cite paths instead.
- In heavy mode, keep main context to task packet, `$codex2codex` status digests, validated artifact summaries, and final plan path.
- If a heavy worker artifact is missing, invalid, interrupted, non-`complete`, or raises unresolved `QUESTION:`, use `$codex2codex` `reply`/`follow` once with the validator/error context. If still invalid, stop before writing/updating `plan.md`.
- If final plan validation fails in any mode, keep raw validator output in artifacts or a short error note and repair from current source; do not let an invalid canonical `plan.md` reach `Execution Handoff`.
- No single-agent fallback in heavy mode. `$codex2codex`/meight unavailability is a blocking failure.
- Redact secrets, credentials, tokens, private personal data, and unnecessary raw logs.

## Planning Rules

- Use the upstream planning pattern: dependency graph first, then vertical slices, then checkpoints.
- Add an `Implementation Map` before tasking: concrete files, symbols/APIs, tests, commands, and data/migration impact.
- Prefer `S`/`M` tasks. Split `XL`; split `L` unless it is one coherent slice.
- Assign `Wave` so dependencies run earlier and same-wave implementation tasks do not overlap writable paths.
- Set `Worker role` to `coding`, `devops`, `review`, `consult`, or `sa`; use `review` for independent PASS/FAIL review tasks.
- Put exact repo-relative paths in `Writable scope`; conservative directory globs are acceptable only when exact files are not knowable before implementation.
- Put exact commands/checks in `Verification`; if not runnable yet, state the concrete future command plus prerequisite.
- Put concrete edit hints, interface/contract impact, test cases, pre-check commands, and post-check commands in each task.
- Put a non-empty value on the same line as every required task field; supporting bullets may follow, but a blank field line followed by a nested bullet containing `:` can fail the execution compiler.
- Make `Step-by-Step Plan` micro-executable: each step should take 2-5 minutes and include an exact path, symbol/API, command, or output artifact.
- Do not use placeholder execution language such as `TBD`, `TODO`, `later`, `as needed`, `relevant files`, `appropriate tests`, `etc.`, `相关`, `必要时`, or `适当`; move true unknowns to `Assumptions` or `Open Questions`.
- Put `Output artifact` under `.codex/work/<yyyyMMdd>-<topic-slug>/artifacts/` or `review*.md` in that workspace so `$codex2codex scripts/plan_to_tasks.py` can compile the plan into `tasks.md`.
- Ensure artifact parent directories are creatable before execution, and prefer one artifact per worker so `$codex2codex` can validate or salvage outputs deterministically.
- Add `Plan Self-Review` before `Execution Decision` and explicitly confirm task executability, test coverage, unknown handling, rollback/abort specificity, and fresh-agent handoff.
- Before execution, run `$codex2codex scripts/run_plan.py <plan.md> --dry-run` when available; treat missing scopes, overlapping writes, or bad artifact paths as plan defects.
