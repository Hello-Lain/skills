---
name: spec2plan
description: "Convert specs, PRDs, issues, or clear requirements into executable plan.md task plans. Use for lightweight task breakdowns from a spec, implementation sequencing, acceptance criteria, validation planning, dependency ordering, parallelization, or heavy production-grade planning. Heavy mode must invoke $codex2codex for meight-style worker coordination, QUESTION pushback, supervised review, rollback/monitoring scrutiny, and clean main-agent context. Replaces planning-and-task-breakdown and plan-grill."
---

# Spec2Plan

Turn a spec into an executable `plan.md`. Do not implement during this skill unless the user explicitly asks after reviewing the plan.

## Mode

- Use `light` by default for clear specs, low-risk work, normal task breakdowns, or when the user wants speed.
- Use `heavy` when the user asks for heavy/production-grade planning, plan hardening, multi-worker coordination, clean context isolation, risky refactors, migrations, auth/billing/security, data/schema changes, CI/CD/infra, deployment/ops, rollback, unclear blast radius, or stakeholder-facing plans.
- If risk is ambiguous, choose `heavy`; if scope is tiny and safe, choose `light`.

## Resources

- Always read `references/plan-contract.md` before drafting or validating a plan.
- For `heavy`, also read `references/heavy-mode.md` and load `$codex2codex` from `/data/lcq/.codex/skills/codex2codex`.
- Validate with `scripts/validate_plan_contract.py <plan.md> --mode light|heavy`.
- Validate heavy worker artifacts with `scripts/validate_subagent_artifact.py <phase> <artifact.md>`.

## Output

- Default light path: `plan.md` in the repo/task root unless the user provides a path.
- Default heavy path: `.spec2plan/<task-slug>/plan.md` unless the user provides a path.
- Write plans, questions, and final responses in the user's language.
- Keep commands, paths, env vars, identifiers, package names, API names, and errors exact.

## Light Workflow

1. Read the spec plus enough nearby code/docs to avoid invented assumptions.
2. Map dependencies, vertical slices, task sizes, validation, risks, and open questions.
3. Main agent writes the plan directly.
4. Run `scripts/validate_plan_contract.py <plan.md> --mode light`.
5. Report path, validation status, key risks/open questions, and that implementation was not executed.

## Heavy Workflow

1. Main agent inspects only enough context to build a compact task packet: objective, spec source, repo status, constraints, likely files/docs, output path, output language, redaction rules, and `no implementation`.
2. Invoke `$codex2codex` inside a task subagent as the adaptive multi-agent shell; pass this skill's heavy-mode packet, contract, worker phases, validators, and artifact paths.
3. Require `$codex2codex` to coordinate read-only `planner`, `reviewer`, and `synthesizer` workers through supervised meight loops; it may add consult/arbiter workers if needed.
4. Save each terminal phase artifact under `<plan-dir>/subagents/<phase>.md`, then validate: `scripts/validate_subagent_artifact.py <phase> <artifact.md>`.
5. Write `plan.md` from the synthesizer artifact body exactly; do not replace it with main-agent synthesis.
6. Run `scripts/validate_plan_contract.py <plan.md> --mode heavy`.
7. Report generated path, artifact dir, validation status, `$codex2codex` cleanup status, key risks/open questions, and that implementation/ops were not executed.

## Context Hygiene

- Keep raw specs, logs, diffs, and worker transcripts out of the final answer; cite paths instead.
- In heavy mode, keep main context to task packet, `$codex2codex` status digests, validated artifact summaries, and final plan path.
- If a heavy worker artifact is missing, invalid, interrupted, non-`complete`, or raises unresolved `QUESTION:`, use `$codex2codex` `reply`/`follow` once with the validator/error context. If still invalid, stop before writing/updating `plan.md`.
- No single-agent fallback in heavy mode. `$codex2codex`/meight unavailability is a blocking failure.
- Redact secrets, credentials, tokens, private personal data, and unnecessary raw logs.
