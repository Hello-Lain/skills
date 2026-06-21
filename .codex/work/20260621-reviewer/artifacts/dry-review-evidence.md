# Dry Review Evidence

## Review: Fixture A

- Artifact Type: `idea-refine` output
- Confidence: High
- Review Route: inline
- Verdict: BLOCK

### Review Basis
- Goal: dry-review Fixture A as an `idea-refine` artifact.
- Artifact: `/data/lcq/.codex/skills/.codex/work/20260621-reviewer/artifacts/dry-review-fixtures.md` lines 5-15.
- Sources: `/data/lcq/.codex/skills/reviewer/SKILL.md`, `/data/lcq/.codex/skills/reviewer/references/review-report-template.md`, `/data/lcq/.codex/skills/reviewer/references/subagent-dispatch.md`, `/data/lcq/.codex/skills/reviewer/references/review-rubrics.md`, `/data/lcq/.codex/skills/idea-refine/SKILL.md`.
- Constraints: read-only review of source files; write only this evidence artifact; no nested reviewer subagents.
- Validators: no executable validators run; fixture is a static artifact review.

### Rubric
- Target user and success criteria: named user plus observable success.
- Divergence: 5-8 variations and 2-3 clustered directions exist.
- Stress-test: each clustered direction covers value, feasibility, differentiation, assumptions, and kill conditions.
- Exit gate: MVP, Not Doing, save-confirm question, and final-direction prerequisites all present.

### Subagent Isolation
- Route: inline.
- Reason: user explicitly forbade nested reviewer subagents.
- Packet: fixture excerpt plus reviewer, generic rubric, subagent-dispatch, report-template, and `idea-refine` contract.
- Raw transcript handling: not applicable.

### Alignment Verdict
- Result: BLOCK — violates the `idea-refine` mandatory exit gate.

### Quality Verdict
- Result: REVISE — promising direction, but too incomplete to accept as final artifact.

### Findings
- [critical] Exit gate evidence missing.
  Evidence: Fixture A lists one direction, user, MVP, risks, Not Doing, but no HMW statement, success criteria, sharpening questions, variations, clusters, stress-tests, assumptions with validation/kill conditions, or save-confirm question.
  Criterion: `idea-refine/SKILL.md` mandatory exit gate.
  Impact: artifact can sound final while skipping required ideation and validation.
  Fix Type: rerun upstream skill.
  Revision: rerun `idea-refine` and add all required gate sections before treating it as final.
- [major] Success criteria absent.
  Evidence: target user is present, but no observable success metric or decision criterion appears in lines 7-15.
  Criterion: reviewer rubric for specific target user plus observable success criteria.
  Impact: future spec/planning cannot judge whether the direction solves the problem.
  Fix Type: patch current artifact.
  Revision: define measurable outcomes, e.g. reproducibility-card completeness, rerun setup recovery rate, or time saved.

### Revision Instructions
- Add the missing `idea-refine` gate sections, especially variations, clusters, stress-tests, assumptions, success criteria, and save-confirm question.
- Keep the existing direction as one candidate, not the whole refinement output.

### Recheck Plan
- Re-read only revised Fixture A plus `idea-refine/SKILL.md` exit-gate checklist.
- Verify each mandatory gate item is explicitly present.

### Residual Risks
- No user transcript exists, so some missing steps may have occurred elsewhere; require artifact-local evidence before passing.

## Review: Fixture B

- Artifact Type: code diff review
- Confidence: High
- Review Route: inline
- Verdict: REVISE

### Review Basis
- Goal: dry-review Fixture B as a code diff; prioritize correctness and tests, not style.
- Artifact: `/data/lcq/.codex/skills/.codex/work/20260621-reviewer/artifacts/dry-review-fixtures.md` lines 17-30.
- Sources: `/data/lcq/.codex/skills/reviewer/SKILL.md`, `/data/lcq/.codex/skills/reviewer/references/review-report-template.md`, `/data/lcq/.codex/skills/reviewer/references/subagent-dispatch.md`, `/data/lcq/.codex/skills/reviewer/references/review-rubrics.md`.
- Constraints: read-only review of source files; write only this evidence artifact; no nested reviewer subagents.
- Validators: tests not run; fixture provides diff only, no repo path or test command beyond context.

### Rubric
- Correctness: changed behavior matches requirement for equality at expiry.
- Tests: changed boundary behavior has regression coverage.
- Regression risk: before/after expiry cases remain expected.
- Scope: diff avoids unrelated behavior changes.

### Subagent Isolation
- Route: inline.
- Reason: user explicitly forbade nested reviewer subagents.
- Packet: fixture diff and context plus reviewer/code-quality rubric.
- Raw transcript handling: not applicable.

### Alignment Verdict
- Result: PASS — `expiry <= now` matches requirement that exact-`now` tokens are rejected.

### Quality Verdict
- Result: REVISE — behavior fix lacks equality regression coverage.

### Findings
- [major] Equality boundary test missing.
  Evidence: fixture context states existing tests cover before and after `now`, but not equality.
  Criterion: code-quality rubric requires tests for changed behavior and boundary cases.
  Impact: the exact regression being fixed can silently revert.
  Fix Type: patch current artifact.
  Revision: add a test asserting `is_expired(now, now)` returns true while retaining before/after cases.

### Revision Instructions
- Add a focused equality test for token expiry at `now`.
- Run the affected auth test file or smallest available test target and record command/outcome.

### Recheck Plan
- Inspect revised diff for the equality test.
- Verify before, equal, and after cases are covered.

### Residual Risks
- Timezone, type, and clock-source behavior cannot be judged from the minimal diff.

## Review: Fixture C

- Artifact Type: research idea feasibility review
- Confidence: Medium
- Review Route: inline
- Verdict: REVISE

### Review Basis
- Goal: dry-review Fixture C as a research idea feasibility review and label unsupported novelty/background claims.
- Artifact: `/data/lcq/.codex/skills/.codex/work/20260621-reviewer/artifacts/dry-review-fixtures.md` lines 32-42.
- Sources: `/data/lcq/.codex/skills/reviewer/SKILL.md`, `/data/lcq/.codex/skills/reviewer/references/review-report-template.md`, `/data/lcq/.codex/skills/reviewer/references/subagent-dispatch.md`, `/data/lcq/.codex/skills/reviewer/references/review-rubrics.md`.
- Constraints: read-only review of source files; write only this evidence artifact; no nested reviewer subagents.
- Validators: no web/literature search run; novelty/background judged only for support present in artifact.

### Rubric
- Problem: concrete field/user and important failure mode.
- Novelty: claim is scoped and evidence level stated.
- Feasibility: data, labels, retrieval method, verifier inputs, and cost are realistic.
- Evaluation: metrics, baselines, controls, expected signal, and stop condition are defined.
- MVP: small test isolates the core claim.

### Subagent Isolation
- Route: inline.
- Reason: user explicitly forbade nested reviewer subagents.
- Packet: fixture research idea plus reviewer research-feasibility rubric.
- Raw transcript handling: not applicable.

### Alignment Verdict
- Result: PASS — artifact addresses the requested research feasibility shape.

### Quality Verdict
- Result: REVISE — feasible seed, but novelty, measurement, and MVP controls are under-specified.

### Findings
- [major] Unsupported novelty claim.
  Evidence: line 38 claims "no one has combined retrieval and verifier models for chart QA" with no literature search, citation, scope boundary, or evidence level.
  Criterion: research rubric requires novelty claim to be scoped and evidence level stated.
  Impact: proposal may overclaim contribution and choose weak baselines.
  Fix Type: patch current artifact.
  Revision: label as unsupported pending literature review; scope by dataset/task/model era or replace with a narrower claim.
- [major] Hallucination metric undefined.
  Evidence: line 40 names "hallucination rate" but gives no operational definition, annotator protocol, automatic judge, or examples.
  Criterion: evaluation requires metric, dataset/input, control, expected signal, cost, and stop condition.
  Impact: MVP may not measure the claimed effect.
  Fix Type: patch current artifact.
  Revision: define hallucination categories, measurement method, threshold for improvement, and stop condition.
- [major] MVP lacks controls and feasibility details.
  Evidence: line 42 says "test on 200 examples"; retrieval index, public dataset choice, verifier model, label cost, and baseline parity are unspecified.
  Criterion: MVP must test the core claim without full-scale buildout.
  Impact: a 200-example test may be noisy or confounded by retrieval/model choices.
  Fix Type: patch current artifact.
  Revision: name dataset, sampling, baselines, retrieval method, verifier, annotation/judge process, and minimum detectable effect.

### Revision Instructions
- Mark novelty/background claims as unsupported until a literature scan supports them.
- Tighten the MVP into a controlled 200-example experiment with named data, baselines, metrics, cost, and stop condition.

### Recheck Plan
- Re-read revised idea for scoped novelty, defined hallucination metric, and executable MVP protocol.
- If novelty remains central, run or cite a literature search before upgrading confidence.

### Residual Risks
- Actual novelty and dataset availability remain unverified without external literature/data inspection.

## Review: Fixture D

- Artifact Type: adversarial plan review
- Confidence: High
- Review Route: inline
- Verdict: BLOCK

### Review Basis
- Goal: dry-review Fixture D adversarially; break commands, assumptions, dependencies, handoff, rollback.
- Artifact: `/data/lcq/.codex/skills/.codex/work/20260621-reviewer/artifacts/dry-review-fixtures.md` lines 44-52.
- Sources: `/data/lcq/.codex/skills/reviewer/SKILL.md`, `/data/lcq/.codex/skills/reviewer/references/review-report-template.md`, `/data/lcq/.codex/skills/reviewer/references/subagent-dispatch.md`, `/data/lcq/.codex/skills/reviewer/references/review-rubrics.md`.
- Constraints: read-only review of source files; write only this evidence artifact; no nested reviewer subagents.
- Validators: commands not run; plan excerpt lacks repo path, env setup, dependency info, or safe execution scope.

### Rubric
- Executability: exact files, commands, env, dependencies, and ordering are sufficient.
- Verification: tests/checks prove CLI behavior and docs.
- Rollback: rollback is concrete and safe for user work.
- Handoff: final status includes evidence, changed files, commands, and limitations.
- Adversarial resilience: paths, hidden approval needs, assumptions, and failure cases are addressed.

### Subagent Isolation
- Route: inline.
- Reason: user explicitly forbade nested reviewer subagents.
- Packet: plan excerpt plus reviewer adversarial-plan rubric.
- Raw transcript handling: not applicable.

### Alignment Verdict
- Result: BLOCK — plan does not meet executable-plan expectations.

### Quality Verdict
- Result: BLOCK — too vague to execute safely or verify.

### Findings
- [critical] Plan is not executable.
  Evidence: steps only say edit `cli.py`, run `python tests.py`, update README; no repo path, CLI framework, command contract, parsing behavior, data source, config, or acceptance criteria.
  Criterion: plan review requires exact files, commands, dependencies, writable scopes, and verification.
  Impact: implementer can build the wrong command or fail immediately on missing paths/deps.
  Fix Type: revise upstream artifact.
  Revision: define `sync-data` inputs/outputs, exact files, dependency/env setup, task order, acceptance checks, and expected CLI behavior.
- [critical] Rollback can destroy unrelated user work.
  Evidence: "revert the files" does not distinguish plan edits from pre-existing user changes.
  Criterion: adversarial plan review checks writable scopes, rollback, and user-work safety.
  Impact: rollback instruction risks overwriting unrelated changes.
  Fix Type: revise upstream artifact.
  Revision: require pre-change diff capture, list touched files, and rollback only the plan-owned hunks.
- [major] Verification command likely brittle.
  Evidence: `python tests.py` assumes a root-level test file and correct interpreter; no venv, package install, test selection, or CLI smoke command is specified.
  Criterion: executable plans need concrete validators and dependency/env assumptions.
  Impact: verification may not run or may miss the new CLI command.
  Fix Type: revise upstream artifact.
  Revision: specify env activation/install, focused unit tests, and a smoke command such as invoking `sync-data` with a fixture.
- [major] Handoff lacks evidence.
  Evidence: "tell user it works" omits changed files, commands run, results, skipped checks, known risks, and rollback notes.
  Criterion: handoff should support independent verification.
  Impact: consumer cannot trust or reproduce completion.
  Fix Type: revise upstream artifact.
  Revision: require final report with changed files, exact commands/outcomes, limitations, and follow-up risks.

### Revision Instructions
- Replace the excerpt with an executable plan: command contract, file map, env/deps, tests, docs, safe rollback, and evidence-based handoff.
- Add adversarial checks for missing files, failing deps, bad input, partial sync, and user-work preservation.

### Recheck Plan
- Re-read revised plan and try to dry-run each command/path mentally.
- Verify rollback protects unrelated diffs and handoff includes evidence.

### Residual Risks
- Without repo context, the correct CLI framework, test runner, and data-sync semantics remain unknown.

## Summary

- Exercised reviewer acceptance checks: live skill-contract rehydration, report-template shape, inline isolation fallback, rubric-before-findings, alignment vs quality split, verdict/severity consistency, evidence-cited findings, concrete revision instructions, skipped-validator reasons, adversarial plan review, code boundary-test review, research novelty support labeling, and `idea-refine` exit-gate enforcement.
