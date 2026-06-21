# Spec: reviewer

## Objective

Build `reviewer`, a general-purpose Codex skill for on-demand quality review of arbitrary artifacts. It should inspect the user's goal, the artifact under review, any available source-of-truth rules, and the artifact's expected lifecycle stage, then decide whether the artifact is acceptable, needs revision, or is blocked.

The first high-value use case is reviewing outputs from the `idea-refine -> interview-me -> spec2plan -> plan2do` pipeline so direction, requirements, plans, and execution results remain aligned. The skill must also work outside that pipeline for code quality, research idea feasibility, specs, plans, docs, reviews, and other quality-gate scenarios.

## Users

- Primary: Codex agents that need an independent quality gate before accepting, handing off, or acting on an artifact.
- Secondary: users who want a structured critique of code, research ideas, product directions, specs, plans, execution results, or other written outputs.
- Tertiary: future workflow skills that may call `reviewer` as an optional quality gate without making it a mandatory global gate.

## Problem

The current discovery-to-execution skill chain has strong per-skill workflows, but no shared revision mechanism that can independently judge whether an artifact is good enough and still aligned with upstream intent.

Current failure modes:

- `idea-refine` can produce a polished idea that fails its own feasibility, novelty, or assumption-quality bar.
- `interview-me` can produce a spec that sounds complete but misses success criteria, scope, non-goals, or binding constraints.
- `spec2plan` can produce a plan that is formally structured but not executable, not vertically sliced, or inconsistent with the spec.
- `plan2do` can finish tasks while missing acceptance criteria, review quality, or behavioral alignment.
- Code review and research idea review need different criteria, but the reviewer should not require a custom skill for every artifact type.

External prior art considered: Superpowers uses composable skills, explicit design signoff, implementation plans, task-level review, and two-stage review patterns. `reviewer` should reuse the mature principle of source-grounded, stage-aware review, but remain a standalone Codex skill rather than a full workflow replacement.

Additional mature-project mechanisms to reuse:

- Reflection loop pattern from LangGraph: producer output, independent critique, revise only when critique exists, stop when no material critique remains. `reviewer` should expose this as a bounded optional recheck loop, not an infinite self-improvement loop.
- LLM-as-judge rubric pattern from LangGraph/open eval frameworks: evaluate against named criteria before issuing the pass/fail decision. `reviewer` should always print its rubric before findings.
- Review packet pattern from Superpowers: review against a short implementation description, requirements/plan, and exact diff or artifact range. `reviewer` should build a compact review packet before judging.
- Read-only reviewer isolation from Superpowers: reviewer must inspect, not mutate. `reviewer` review-only mode must forbid edits and branch/index mutation.
- Severity triage and feedback reception from Superpowers: fix critical/important issues, note minor issues, and push back on technically wrong feedback with evidence. `reviewer` should include a "feedback validity" step for consumers so review output is not blindly applied.
- Dual-verdict task review from Superpowers subagent-driven development: separate "spec compliance" from "code/artifact quality". `reviewer` should use separate alignment and quality verdict axes internally, then collapse them into the top-level verdict.
- Adversarial review proposal from Superpowers: self-review is often confirmatory, while a dedicated "break the plan" pass catches silent failures such as wrong commands, missing environment activation, fragile regexes, and drifting mappings. `reviewer` should include an adversarial mode for plans, code, and research ideas.
- Cost lesson from Superpowers release notes: subagent review loops can add large latency without measurable quality gain for routine specs/plans. `reviewer` should use one isolated reviewer subagent by default, and escalate to multiple specialized subagents only for high-risk, high-ambiguity, broad, or explicitly requested cases.
- PR review trigger pattern from OpenHands: reviews should be explicitly requested by label/reviewer-style triggers and customizable by local guidelines. `reviewer` should remain on-demand and should load local project guidance before generic rules.
- PR-Agent configuration pattern: review axes such as tests, security, ticket/spec compliance, effort, split-ability, max findings, and extra instructions are configurable. `reviewer` should support the same idea as review options without requiring a config file in v1.
- Evaluation-framework pattern from Promptfoo/OpenAI Evals/Inspect: convert subjective review into assertions, scorers, thresholds, and repeatable reports where possible. `reviewer` should prefer executable validators and explicit acceptance checks over pure prose judgment.
- Trajectory/log artifact pattern from SWE-agent: preserve enough query/action/observation evidence to reproduce why a review passed or failed. `reviewer` should emit concise evidence receipts, while quarantining large logs outside active context.
- Agent-PR risk pattern from GitHub guidance: agent-generated code can look clean and pass tests while still adding redundancy or quiet technical debt. `reviewer` code review must include reuse/debt checks, not only test status and style.
- VS Code subagent pattern: subagents keep focused work, research, parallel analysis, and review perspectives outside the main context, returning only concise summaries. `reviewer` should run review in a subagent by default when subagent tooling is available.
- Multi-perspective subagent review pattern: correctness, security, performance, architecture, and quality lenses can run independently then be synthesized. `reviewer` should use this only when the review packet is broad enough to justify parallel reviewers.
- Subagent recursion guard pattern: nested subagents are disabled by default in VS Code to avoid loops. `reviewer` subagents must not spawn further reviewer subagents in v1.
- OpenHands customization pattern: repository review guidance can supplement default rules without forking the reviewer. `reviewer` should load local `AGENTS.md`, project review docs, and skill contracts as additive guidance, then resolve conflicts explicitly.
- Aider check-loop pattern: automated lint/test commands can be run after changes and used as repair signals. `reviewer` should treat available commands as check evidence, while still requiring source-contract alignment.

## Success Criteria

- Given a user goal plus artifact, `reviewer` identifies artifact type and lifecycle stage with stated confidence.
- Given a known skill artifact, it reads the relevant `SKILL.md` and directly linked contracts/rubrics needed to judge that artifact.
- Given an unknown artifact type, it derives an explicit review rubric from the user's goal, artifact type, source evidence, and general quality principles.
- Every review returns exactly one verdict: `PASS`, `REVISE`, or `BLOCK`.
- Reviews include evidence-backed findings with severity, affected artifact section, violated criterion, and concrete revision instructions.
- Reviews distinguish quality defects from style preferences and unsupported reviewer guesses.
- Reviews can cover at least these v1 domains: pipeline artifacts, code quality, research idea feasibility, specs/plans/docs, and execution-result acceptance.
- A downstream agent can use the review output to redo or patch the original artifact without needing hidden context.
- Routine reviews finish in one pass unless critical evidence is missing or the user explicitly asks for a revise loop.
- High-risk reviews can enter an adversarial "try to break it" pass and return fix-type routing: patch artifact, rewrite upstream spec, revisit idea, or ask user.

## Scope

### In

- Create a new skill folder named `reviewer`.
- Define trigger metadata for broad review use: quality gate, revise, audit, critique, review artifact, code quality, research idea feasibility, spec/plan/result review.
- Define an intake protocol that collects or infers:
  - user goal;
  - artifact path or pasted artifact;
  - artifact type;
  - expected stage;
  - applicable source-of-truth files;
  - whether review should be blocking or advisory.
- Define a review packet protocol containing:
  - goal and stage;
  - artifact under review;
  - source-of-truth list;
  - applicable validators or commands;
  - constraints and non-goals;
  - optional review options such as focus area, max findings, adversarial mode, and save-review.
- Define a subagent dispatch contract containing:
  - exact review packet;
  - read-only instruction;
  - no nested subagents;
  - required output schema;
  - allowed commands or no-command constraint;
  - evidence format;
  - maximum findings;
  - handoff path for saved review artifacts.
- Define a source hierarchy for review:
  - latest user goal and explicit constraints;
  - local `AGENTS.md`;
  - relevant upstream artifact such as `idea.md`, `spec.md`, or `plan.md`;
  - relevant `SKILL.md`;
  - directly linked contracts, rubrics, validators, or acceptance criteria;
  - current files/diffs/tests when reviewing code or execution results;
  - external references only when requested or necessary.
- Define autonomous rubric generation:
  - use existing skill gates/contracts for known artifacts;
  - derive criteria for unknown artifacts;
  - name assumptions and confidence;
  - fail closed when evidence is missing for a high-impact judgment.
- Define output schema:
  - `Verdict`;
  - `Artifact Type`;
  - `Review Basis`;
  - `Rubric`;
  - `Alignment Verdict`;
  - `Quality Verdict`;
  - `Findings`;
  - `Revision Instructions`;
  - `Recheck Plan`;
  - `Evidence Receipts`;
  - `Subagent Isolation`;
  - `Residual Risks`.
- Define known-skill review adapters for:
  - `idea-refine`;
  - `interview-me`;
  - `spec2plan`;
  - `plan2do`;
  - `skill-creator` when reviewing skill definitions.
- Define generic adapters for:
  - code quality;
  - research idea feasibility;
  - documentation/process quality;
  - implementation/execution result acceptance.
- Provide concise reference files for review rubrics if needed, while keeping `SKILL.md` lean.
- Add `agents/openai.yaml` metadata consistent with the new skill.
- Validate the skill folder with the skill validation script.

### Out

- Do not make `reviewer` a mandatory gate in `idea-refine`, `interview-me`, `spec2plan`, or `plan2do` v1.
- Do not automatically rewrite or patch the reviewed artifact unless the user separately asks for implementation.
- Do not execute full original-stage workflows on behalf of other skills.
- Do not claim objective truth for subjective strategy judgments; state evidence, assumptions, and uncertainty.
- Do not require web search for every review. Use it only for current, niche, high-stakes, or explicitly requested external evidence.
- Do not create a large framework with many speculative adapters before the general review protocol works.

## Requirements

### Functional

- `reviewer` must start by identifying what is being reviewed and what "good" means for that artifact.
- `reviewer` must rehydrate authoritative sources before making a quality judgment.
- `reviewer` must derive a review rubric before listing findings.
- `reviewer` must use known skill definitions as review contracts when reviewing artifacts produced by those skills.
- `reviewer` must treat summaries, previous reviews, old plans, logs, and generated docs as navigation, not authority.
- `reviewer` must assemble a compact review packet before making a verdict.
- `reviewer` must run the actual critique in an isolated subagent by default when subagent tooling is available.
- `reviewer` must pass only the review packet, not the full main-thread conversation, into the reviewer subagent.
- `reviewer` must keep reviewer subagent output to the final report, evidence receipts, and blocker notes; raw subagent transcripts stay out of active main context unless needed for debugging.
- `reviewer` must fall back to inline review only when subagent tooling is unavailable, unsafe, or disproportionate for a trivial artifact, and must state the fallback reason.
- `reviewer` must specify whether the review was `subagent`, `multi-subagent`, or `inline`, plus why that route was chosen.
- `reviewer` must make the main agent a coordinator only: prepare packet, launch reviewer, receive report, sanity-check report format, and present results without silently rewriting the reviewer verdict.
- `reviewer` must run a lightweight contradiction check in the main agent before presenting results: verify findings cite evidence, verdict matches severities, and revision instructions are actionable.
- `reviewer` must not leak user-private or irrelevant conversation history into the subagent prompt.
- `reviewer` must not let reviewer subagents spawn further reviewer subagents in v1.
- `reviewer` must remain read-only unless the user separately asks it to implement revisions.
- `reviewer` must produce separate internal judgments for:
  - alignment with goal/source contract;
  - intrinsic artifact quality.
- `reviewer` must label each finding with severity:
  - `critical`: artifact is unsafe, misleading, unexecutable, or directionally wrong;
  - `major`: artifact fails an important requirement or quality gate;
  - `minor`: artifact is usable but should be tightened;
  - `nit`: optional polish only, excluded from blocking verdicts.
- `reviewer` must map severity to verdict:
  - `PASS`: no critical or major findings; minor/nit items may remain;
  - `REVISE`: at least one major finding, or several minor findings that reduce usability;
  - `BLOCK`: at least one critical finding, missing source-of-truth evidence required for judgment, or artifact cannot be reviewed safely.
- `reviewer` must include concrete rewrite instructions for every critical and major finding.
- `reviewer` must include a recheck plan that says what to inspect after revision.
- `reviewer` must include evidence receipts for material findings, citing file paths, artifact sections, command outputs, validator results, or explicitly named missing evidence.
- `reviewer` must support optional review knobs:
  - `focus`: restrict review to a named concern such as security, feasibility, tests, or scope;
  - `max_findings`: cap findings while preserving all critical findings;
  - `adversarial`: actively try to falsify the artifact;
  - `save`: write a review artifact under the active workspace when requested.
- `reviewer` must use executable validators when available and safe, such as plan validators, test commands, lint/type checks, schema checks, or existing project scripts.
- `reviewer` must not equate "tests passed" with artifact acceptance; it must still check requirement alignment, hidden debt, missing edge cases, and over/under-building.
- `reviewer` must route each critical/major issue by fix type:
  - patch current artifact;
  - revise upstream artifact;
  - rerun upstream skill;
  - ask user;
  - stop as unsafe or unsupported.
- `reviewer` must advise consumers to verify review feedback before blindly applying it when the finding depends on inference rather than direct evidence.
- For code quality review, `reviewer` must prioritize correctness, regressions, test gaps, API/data/security risk, maintainability, and unnecessary complexity.
- For research idea feasibility review, `reviewer` must prioritize problem clarity, novelty, feasibility, data availability, evaluation path, baseline comparison, risk, cost, and falsifiability.
- For `idea-refine` review, `reviewer` must check the mandatory exit gate, user/value clarity, variation quality, clustered tradeoffs, assumptions, MVP, and Not Doing list.
- For `interview-me` review, `reviewer` must check explicit confirmation, user/why/success/constraints/scope/non-goals, testable acceptance checks, and unresolved assumptions.
- For `spec2plan` review, `reviewer` must check plan-contract compliance, implementation map, task executability, dependencies, writable scopes, verification, rollback, risks, and plan self-review.
- For `plan2do` review, `reviewer` must check task completion evidence, verification outcomes, review verdict, rework handling, artifact reporting, and false-completion risk.

### Non-Functional

- Keep the skill body concise and route detailed rubrics to directly linked references only when needed.
- Prefer deterministic review structure over long prose.
- Keep reviews actionable and terse enough that another agent can apply them directly.
- Avoid overfitting to the four pipeline skills; the general review protocol must work for arbitrary artifacts.
- Preserve user work and avoid destructive actions.
- Use primary/local sources before external summaries.
- Report verification gaps explicitly.
- Default to one isolated reviewer subagent for context hygiene. Use inline review only for trivial artifacts or unavailable subagent tooling. Use multiple specialized reviewer subagents only when risk, ambiguity, breadth, or user instruction justifies the cost.
- Keep large logs, full diffs, and trajectories out of active output unless needed; cite stored artifacts or concise evidence instead.

## Constraints

- The skill lives under `/data/lcq/.codex/skills/reviewer`.
- The skill name must be lowercase hyphen-case: `reviewer`.
- Manual file edits must use `apply_patch`.
- The implementation must follow the local skill system conventions:
  - required `SKILL.md`;
  - recommended `agents/openai.yaml`;
  - optional `references/` only for reusable rubric details.
- The implementation should use `skill-creator` validation flow, including `quick_validate.py`.
- The v1 integration mode is on-demand/advisory. Existing skills may mention `reviewer` later, but this spec does not require modifying them.
- External project patterns are inspiration only. Do not vendor third-party code or copy long prompt templates unless license and maintenance implications are explicitly reviewed.

## Assumptions To Validate

- [ ] A single generic review protocol can cover most artifact types without becoming vague. Validate by forward-testing at least one known-skill artifact and one non-pipeline artifact.
- [ ] Known skill review adapters can be expressed as compact routing rules rather than long duplicated rubrics. Validate by reading existing skill gates and checking token cost.
- [ ] `PASS/REVISE/BLOCK` is sufficient for downstream workflow decisions. Validate by using the output to revise an artifact.
- [ ] Research idea feasibility review can be useful without always requiring web/literature search. Validate by separating conceptual feasibility from evidence-backed novelty claims.
- [ ] Code quality review can use existing repo context tools without duplicating the behavior of normal code review. Validate on a small diff.

## Risks

- Over-broad triggering could cause the skill to hijack ordinary questions. Mitigation: frontmatter should say use for artifact quality review, revision, critique, or gatekeeping, not all analysis.
- Rubric generation could become subjective. Mitigation: require review basis, source hierarchy, confidence, and evidence per finding.
- The skill could duplicate existing skill contracts and drift. Mitigation: read live `SKILL.md` and linked contracts instead of copying long rubrics.
- Findings could be too abstract to drive rework. Mitigation: require concrete revision instructions and recheck plan for major/critical findings.
- Reviews could over-block creative idea work. Mitigation: distinguish exploratory artifacts from execution-ready artifacts and calibrate verdict by lifecycle stage.
- Reviews could miss code behavior without reading enough context. Mitigation: require one dependency ring or tests/diffs when code impact is material.
- Independent review loops could waste time on routine artifacts. Mitigation: default to one isolated subagent, cap recheck loops, and require explicit escalation reason for multi-subagent or adversarial passes.
- LLM judge output could be unstable. Mitigation: require rubric-first review, evidence receipts, deterministic validators when available, and separate alignment/quality verdicts.
- Reviewer feedback could be wrong but sound authoritative. Mitigation: require consumers to verify inferred findings and allow evidence-backed pushback.

## Acceptance Checks

- `reviewer/SKILL.md` exists with valid frontmatter and concise usage instructions.
- `reviewer/agents/openai.yaml` exists and matches `SKILL.md`.
- Any reference files are directly linked from `SKILL.md` and only cover reusable details.
- Running `/data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer` passes.
- A dry review of an `idea-refine` artifact produces:
  - artifact type;
  - review basis including `idea-refine/SKILL.md`;
  - rubric;
  - `PASS/REVISE/BLOCK`;
  - evidence-backed findings;
  - revision instructions.
- A dry review of a code diff or code artifact produces correctness-first findings and does not focus on style-only issues.
- A dry review of a research idea produces feasibility/novelty/evaluation/data-risk findings and labels unsupported claims.
- A dry adversarial review of a plan attempts to break commands, assumptions, dependencies, and handoff steps before returning `PASS`.
- Review output includes alignment verdict, quality verdict, top-level verdict, fix-type routing, and evidence receipts.
- Review-only use leaves git status unchanged except for an optional saved review artifact explicitly requested by the user.
- When subagent tooling is available, a dry review uses an isolated reviewer subagent and returns only the synthesized report to the main context.
- When subagent tooling is unavailable, a dry review states the inline fallback reason.
- The skill does not modify reviewed artifacts during review-only use.
- Existing `idea-refine`, `interview-me`, `spec2plan`, and `plan2do` behavior remains unchanged unless the user later requests integration edits.

## Open Questions

- Should a later v2 add optional handoff hooks inside the four pipeline skills that suggest `reviewer` before handoff?
- Should `reviewer` save review artifacts under the active `.codex/work/<topic>/artifacts/` workspace by default, or only when the user asks?
- Should known adapters include machine-checkable validators where available, or keep v1 purely instructional?
- Should research idea reviews optionally integrate `literature-rag` for novelty/background checks when the user asks for evidence-backed feasibility?
