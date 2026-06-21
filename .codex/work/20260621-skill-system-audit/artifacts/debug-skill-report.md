# Debug Skill Report: reviewer/edit-orchestration/plan2do/spec2plan/skill-tokenless

## Verdict
- Impact: mixed
- Confidence: high for local skill defects; medium for external reuse mapping
- One-line reason: the current skill set is useful and validates syntactic artifacts, but production quality still depends on agent memory instead of an enforced skill-production gate.

## Evidence Used
- Skill files:
  - `/data/lcq/.codex/skills/reviewer/SKILL.md`
  - `/data/lcq/.codex/skills/edit-orchestration/SKILL.md`
  - `/data/lcq/.codex/skills/plan2do/SKILL.md`
  - `/data/lcq/.codex/skills/spec2plan/SKILL.md`
  - `/data/lcq/.codex/skills/skill-tokenless/SKILL.md`
  - `/data/lcq/.codex/skills/.system/skill-creator/SKILL.md`
- Direct references/scripts inspected:
  - `reviewer/references/review-report-template.md`
  - `reviewer/references/subagent-dispatch.md`
  - `reviewer/references/review-rubrics.md`
  - `edit-orchestration/references/apply-patch.md`
  - `edit-orchestration/references/failure-recovery.md`
  - `edit-orchestration/references/route-matrix.md`
  - `edit-orchestration/references/tooling.md`
  - `plan2do/references/execution-contract.md`
  - `plan2do/references/failure-policy.md`
  - `plan2do/references/review-rubric.md`
  - `spec2plan/references/plan-contract.md`
  - `spec2plan/references/heavy-mode.md`
  - `spec2plan/references/discovery-routing.md`
  - `skill-tokenless/references/testing.md`
  - `skill-tokenless/references/validation.md`
  - `debug-skill/references/report-template.md`
  - `debug-skill/references/hermes-reuse.md`
- Conversation / trace:
  - User reported repeated patch failures during the reviewer-v2 work.
  - User requested a `reviewer` skill with lite/heavy routing, subagent isolation, cleanup, and integration into the idea/spec/plan/do pipeline.
  - Previous artifacts under `.codex/work/20260621-reviewer/` and `.codex/work/20260621-reviewer-v2/` show validator/rework/review loops and final validation.
- Artifacts / diffs:
  - `.codex/work/20260621-reviewer-v2/spec.md`
  - `.codex/work/20260621-reviewer-v2/plan.md`
  - `.codex/work/20260621-reviewer-v2/execution/tasks.json`
  - `.codex/work/20260621-reviewer-v2/artifacts/final-report.md`
  - `.codex/work/20260621-reviewer-v2/artifacts/reviewer-audit.md`
  - `.codex/work/20260621-reviewer-v2/review.md`
  - `.codex/work/20260621-reviewer/artifacts/debug-skill-audit.md`
- Commands / validation:
  - `python3 debug-skill/scripts/skill_audit_core.py --self-test` -> `SELF_TEST_OK`
  - `python3 reviewer/scripts/validate_review_report.py --self-test` -> `VALID`
  - `python3 plan2do/scripts/validate_execution.py .codex/work/20260621-reviewer-v2` -> `VALID`
  - `python3 spec2plan/scripts/validate_plan_contract.py .codex/work/20260621-reviewer-v2/plan.md --mode light` -> `VALID`
  - `for d in reviewer edit-orchestration plan2do spec2plan skill-tokenless; do python3 .system/skill-creator/scripts/quick_validate.py "$d"; done` -> all `Skill is valid!`
  - CodeGraph exploration of `validate_review_report`, `validate_execution`, `compile_execution`, and `validate_plan_contract` -> no covering tests found for key validator functions.
- External reuse sources:
  - `https://github.com/obra/superpowers` at `896224c4b1879920ab573417e68fd51d2ccc9072`
  - `https://github.com/plandex-ai/plandex` at `e2d772072efadbe41d2946d97d79be55532dbab5`
  - `https://github.com/Aider-AI/aider` at `5dc9490bb35f9729ef2c95d00a19ccd30c26339c`
  - `https://github.com/pre-commit/pre-commit` at `1553b465fd7ea42321ae0d04d1b41e706b89ae45`
  - `https://github.com/ast-grep/ast-grep` at `ad73dd07e3b42424662c4e133542e6905ec6a66d`
  - `https://github.com/openrewrite/rewrite` at `a8723b003dfa13d825bfd82b81027bec3f23c6cf`
  - `https://github.com/NousResearch/hermes-agent-self-evolution`
- Missing evidence:
  - No live replay transcript for every failed `apply_patch`; root cause is inferred from observed failure pattern and current edit-orchestration contract.
  - No stress test yet proving reviewer wait-budget cleanup under stalled subagents across many launches.
  - No dedicated unit-test suite for the validator scripts; only embedded self-tests and artifact validation exist.

## Execution Trace
1. Trigger: user asked for `bug-skill` deep audit of five skills after the previous workflow exposed failures.
2. Skill instructions loaded: `debug-skill`, `reviewer`, `context-engineering`, `codegraph-project-reader`, `edit-orchestration`, `plan2do`, `spec2plan`, `skill-tokenless`, plus relevant references.
3. Decisions:
   - `bug-skill` is not installed; use `debug-skill` as the closest available audit skill.
   - Treat summaries as navigation; re-read current skill files, refs, scripts, prior artifacts, and validators.
   - Do not modify target skills in this audit turn; produce a recommendation artifact first.
4. Actions:
   - Ran deterministic skill validators and current artifact validators.
   - Used CodeGraph for validator/script blast radius.
   - Shallow-cloned or checked mature GitHub projects for reusable quality-control patterns.
5. Failures / friction:
   - Initial `quick_validate.py` batch command failed because the script accepts one directory at a time.
   - GitHub raw `curl` intermittently timed out/reset; `git ls-remote` and shallow clones succeeded.
   - `rtk proxy` compressed long reads and hid snippets; exact `sed` reads were needed for evidence.
6. Recovery:
   - Re-ran `quick_validate.py` in a loop.
   - Used shallow clones in `/tmp/skill-audit-*` instead of raw curl.
   - Re-read relevant source in smaller exact chunks.
7. Verification:
   - All target skills pass `quick_validate.py`.
   - Existing reviewer-v2 plan/execution/report validators pass.
   - This report is scheduled for `reviewer` gate after creation.
8. Result:
   - Current system is directionally strong but has production-gate gaps. A shared Skill Production Gate is required.

## Effectiveness
- Quality: mixed. Skills encode strong practices, but some gates are advisory and can be skipped accidentally.
- Efficiency: mixed. Reviewer and plan2do reduce risk, but heavy review/subagent flows can overconsume tokens without explicit gate thresholds and cleanup proof.
- Evidence use: mostly strong. Validators and artifact paths exist; semantic validation remains shallow in places.
- Context handling: improved by reviewer isolation and context-engineering, but not consistently enforced across skill creation/update workflows.
- Tooling: partial. Existing validators catch malformed artifacts; missing patch payload linter and validator unit fixtures create blind spots.
- Verification: mixed. Structure validators pass; acceptance-to-evidence traceability is not yet enforced.
- User friction: high during patch failures and repeated review loops.
- Reuse discipline: improving. Mature external patterns are identified but not yet codified as local gates.

## Findings
- critical: No enforced Skill Production Gate connects `skill-creator`, `skill-tokenless`, deterministic validators, and `reviewer`. Evidence: `.system/skill-creator/SKILL.md` mentions `quick_validate.py`, `skill-tokenless/SKILL.md` says to run after skill-creator, and `reviewer/SKILL.md` defines quality gates, but no shared script/reference makes the combined pipeline mandatory. Impact: new or modified production skills can bypass tokenless behavior lock, forward tests, and reviewer gate.
- major: `plan2do` can report a structurally valid execution while acceptance evidence remains shallow. Evidence: `plan2do/scripts/validate_execution.py` checks task status, nonempty artifacts, final report status, review verdict, and a verification marker/artifact; it does not prove each task's planned verification commands were executed and passed. Impact: false completion remains possible if final report says verification happened without command-by-command trace.
- major: `spec2plan` and `plan2do` still depend on fragile Markdown field parsing for dependencies and artifacts. Evidence: `spec2plan/SKILL.md` warns that blank field lines and nested bullets with `:` can fail the compiler; `plan2do/scripts/compile_execution.py` parses fields from Markdown. Impact: valid-looking plans can compile incorrectly or require manual repair, especially with ranges such as `Tasks 1-3` or nested detail.
- major: `edit-orchestration` recovers from patch misses but under-specifies patch prevention. Evidence: `edit-orchestration/references/apply-patch.md` says patch small and recover after misses, but no deterministic preflight validates apply_patch payload grammar, hunk size, uniqueness, add-file blank-line prefixes, or stale anchor risk before execution. Impact: repeated patch failures waste time and can leave partial edits.
- major: `reviewer` schema is stronger now but not yet unified with `plan2do` review format. Evidence: `reviewer` uses `PASS|REVISE|BLOCK`; `plan2do/scripts/validate_execution.py` accepts `PASS|FAIL` review verdicts. Impact: one workflow may need parallel review artifacts or adapter logic, raising maintenance and validation risk.
- major: `reviewer` heavy subagent cleanup is policy, not stress-tested invariant. Evidence: `reviewer/SKILL.md` and `subagent-dispatch.md` require cancel/archive/kill after wait budget, but no local stress test proves cleanup under stalled agents. Impact: repeated review usage can hit subagent limits or leak context/cost.
- major: `skill-tokenless` is scoped as an optimization pass, not a production quality gate. Evidence: `skill-tokenless/SKILL.md` covers behavior lock, RED/GREEN, validation, and token compression, but the trigger description is mainly "reducing token cost"; no mandatory upstream integration exists. Impact: skill creation may treat tokenless as optional cleanup rather than required behavior-preservation and forward-test discipline.
- minor: `debug-skill` successfully demands reuse search, but the local workflow has no cacheable source-attribution artifact format. Evidence: this report had to manually collect source links, commit SHAs, and local clone evidence. Impact: future audits may repeat slow external research or lose attribution quality.

## Reuse Search
- Defect: missing enforced production gate for skills, weak patch preflight, shallow plan/execution validation, review cleanup/token cost risk.

| Source project/repo | Source link | Mature signal | Borrowed idea | Reusable component/CLI/schema | Adoption mode | Target skill change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- | --- |
| obra/superpowers | `https://github.com/obra/superpowers` | active methodology repo; has `requesting-code-review`, `subagent-driven-development`, and skill authoring flows | fresh subagent per task, review after each task, broad final review, file handoffs instead of transcript handoffs, durable progress ledger | prompt templates and review-package pattern | adapted | add reviewer-backed production gate and file-based reviewer packets; require cleanup ledger for subagents | direct copy rejected because Codex/Paseo tools and local skill contracts differ |
| plandex-ai/plandex | `https://github.com/plandex-ai/plandex` | terminal AI dev tool; README documents cumulative diff review sandbox | keep generated changes separate until reviewed/applied | pending diff/review sandbox concept | pattern-only | strengthen `edit-orchestration` review-before-apply path; add pre-apply artifact for large generated patches | direct integration rejected because Plandex runtime is too large for a skill gate |
| Aider-AI/aider | `https://github.com/Aider-AI/aider` | mature AI coding tool; repo-map, git, lint/test workflow | edit feedback loop with repo map and tests/lint after changes | lint/test command patterns, repo-map idea | pattern-only | make edit routes require exact affected files plus focused verification loop | direct integration rejected because adding aider as a required edit backend would be heavy and overlaps Codex |
| pre-commit/pre-commit | `https://github.com/pre-commit/pre-commit` | widely used multi-language hook framework | declarative hooks with deterministic per-file gates | `pre-commit` CLI and local hook schema | adapted/direct optional | add optional `.pre-commit`/local hook recipe for skill validation: quick_validate, reviewer report validation, plan/execution validators | direct mandatory install rejected; keep as optional project hook to avoid global dependency |
| ast-grep/ast-grep | `https://github.com/ast-grep/ast-grep` | AST structural search/rewrite CLI with YAML rules | structural search/rewrite instead of fragile text patches | `sg` / `ast-grep` CLI | direct optional | enhance `edit-orchestration` structural route; add self-check and sample rules for repeated code rewrites | not useful for Markdown-only skill docs; use only for code edits |
| openrewrite/rewrite | `https://github.com/openrewrite/rewrite` | mature recipe-based JVM refactoring framework | declarative recipes and dry-run reports for large rewrites | OpenRewrite recipes via Maven/Gradle | direct optional | keep in `edit-orchestration` for JVM migrations; not default | rejected for generic skills because setup is JVM-specific and heavy |
| NousResearch/hermes-agent-self-evolution | `https://github.com/NousResearch/hermes-agent-self-evolution` | self-evolution framework; already mapped in `debug-skill/references/hermes-reuse.md` | dataset/constraint/fitness scoring and explicit promotion gates | adapted parser/constraint/fitness primitives in `skill_audit_core.py` | adapted | keep debug-skill candidate scoring and reuse matrix; use it to rank production-gate candidates | direct GEPA/DSPy dependency rejected as too heavy for default Codex skill audits |

- Search boundary: GitHub repos and local clones only; no npm/PyPI package health analysis beyond repo reachability.
- No mature component found: no single mature project directly provides a Codex-native "skill production gate" combining `skill-creator`, token budget, reviewer isolation, plan execution, and validator adapters.
- Reuse-to-candidate mapping:
  - Candidate A uses Superpowers + pre-commit + Hermes.
  - Candidate B uses Plandex + ast-grep/OpenRewrite + Aider.
  - Candidate C uses Superpowers + reviewer subagent cleanup policies.

## Candidate Improvements
| Candidate | Target surface | Reuse source | Summary | Benefit | Risk | Fitness |
| --- | --- | --- | --- | --- | --- | --- |
| A. Skill Production Gate | `skill-tokenless` references/scripts, `.system/skill-creator`, `reviewer`, `plan2do` | Superpowers, pre-commit, Hermes | Add a shared `skill-production-gate.md` and `validate_skill_production.py` that requires Behavior Lock, token budget, quick_validate, forward scenario checks, reviewer gate, cleanup proof, and final report | highest quality gain; directly addresses user goal | medium; cross-skill integration needs careful rollout | high |
| B. Patch Reliability Gate | `edit-orchestration` refs/scripts | Plandex, ast-grep, OpenRewrite, Aider | Add `lint_apply_patch_payload.py` plus route rules: small hunks, exact raw anchors, add-file line prefix checks, max hunk size, generated diff review-before-apply path | reduces repeated patch failures; concrete tooling | medium; cannot fully parse runtime tool matching before application | high |
| C. Review/Execution Schema Unification | `reviewer`, `plan2do`, `spec2plan` validators | Superpowers, pre-commit | Normalize review verdict adapter: reviewer v2 `PASS|REVISE|BLOCK` maps to plan2do `PASS|FAIL/BLOCK`; require command-by-command verification receipts in execution final report | reduces false completion and duplicate review artifacts | medium; plan2do validator changes may break old artifacts | high |

## Recommendation
- Recommended action: implement Candidate A first, with C folded into its validator contract; then implement B.
- Target files:
  - `skill-tokenless/SKILL.md`
  - `skill-tokenless/references/validation.md`
  - `skill-tokenless/references/testing.md`
  - `skill-tokenless/references/skill-production-gate.md` new
  - `skill-tokenless/scripts/validate_skill_production.py` new
  - `.system/skill-creator/SKILL.md`
  - `reviewer/SKILL.md`
  - `reviewer/references/review-report-template.md`
  - `plan2do/SKILL.md`
  - `plan2do/references/execution-contract.md`
  - `plan2do/scripts/validate_execution.py`
  - `spec2plan/references/plan-contract.md`
  - `edit-orchestration/references/apply-patch.md`
  - `edit-orchestration/references/route-matrix.md`
  - `edit-orchestration/scripts/lint_apply_patch_payload.py` new
- Verification:
  - `python3 .system/skill-creator/scripts/quick_validate.py <changed-skill>`
  - `python3 skill-tokenless/scripts/validate_skill_production.py <skill-dir> --artifact <production-report.md>`
  - `python3 reviewer/scripts/validate_review_report.py <review.md>`
  - `python3 plan2do/scripts/validate_execution.py <workspace>`
  - `python3 spec2plan/scripts/validate_plan_contract.py <plan.md> --mode light|heavy`
  - self-tests for all new/changed scripts
- Reuse rationale: no direct Codex-native framework exists; borrow gate architecture, isolated review, pending diff review, hook-style deterministic checks, and structural rewrite tools as local, optional, low-dependency components.
- Execute now: no; this audit recommends a larger spec/plan before editing production skills.

## Proposed Production Gate Contract
- Gate name: Skill Production Gate.
- Scope: every new skill, material skill update, validator script update, skill metadata update, or skill workflow change.
- Default route:
  1. `skill-creator` drafts/updates skill.
  2. `skill-tokenless` performs Behavior Lock and token budget pass.
  3. Deterministic validators run: `quick_validate.py`, script self-tests, plan/execution/reviewer validators when applicable.
  4. Forward scenario checks run for at least one RED/GREEN or mock workflow path.
  5. `reviewer` gates the final artifact:
     - lite if docs-only, low-risk, small, and deterministic validators cover the change.
     - heavy subagent if new skill, validator script, production workflow, safety gate, plan/execution route, or prior failure.
  6. Reviewer subagent cleanup is recorded: `archive`, `kill`, `not launched`, or `unavailable with reason`.
  7. Production report is saved and validated.
- Completion requires:
  - behavior lock preserved or intentionally changed with source evidence;
  - token budget delta recorded;
  - validators passed or blocked with exact cause;
  - reviewer verdict accepted or disputed with evidence;
  - no missing cleanup for launched reviewer subagents;
  - final report maps requirements to evidence.

## Per-Skill Fix Direction
- `reviewer`:
  - Add stress fixture for stale/missing source paths, invalid confidence, invalid route, command evidence, and subagent cleanup statement.
  - Add adapter guidance for consumers that require `PASS|FAIL` rather than `PASS|REVISE|BLOCK`.
  - Add a "reviewer is not authority; coordinator must verify evidence" checklist to production gate.
- `edit-orchestration`:
  - Add patch payload lint script for generated reports and complex add/update patches.
  - Strengthen prevention: one logical change per patch, exact raw anchor check for risky hunks, max hunk size, explicit add-file blank-line prefix rule.
  - Route large Markdown/report creation through template artifact + reviewer gate instead of giant ad-hoc hunks when risk is high.
- `plan2do`:
  - Extend `validate_execution.py` to require command-by-command verification receipts or explicit blocker mapping to each task.
  - Accept/normalize reviewer v2 verdicts or require adapter artifact.
  - Fail if final report has review `PASS` but reviewer artifact has `REVISE` or `BLOCK`.
- `spec2plan`:
  - Make dependency fields canonical: use numeric lists only (`none`, `1`, `1,2`, not `Tasks 1-3`) or teach compiler ranges.
  - Add plan validator warnings for Markdown that compiles but is likely ambiguous.
  - Require a skill-production task template for skill work.
- `skill-tokenless`:
  - Reframe from token optimization into final production pass for skill creation/update.
  - Add `skill-production-gate.md` reference and production report schema.
  - Integrate `reviewer` as mandatory for new/material skill changes, with lite/heavy auto-routing.

## Stop
- This report is audit output only. Do not modify the target skills until a spec/plan is confirmed.
