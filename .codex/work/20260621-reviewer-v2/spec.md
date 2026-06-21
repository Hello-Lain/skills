# Spec: reviewer v2

## Objective

Upgrade the local `reviewer` skill so Codex agents can run reliable artifact quality gates without wasting tokens, polluting the main context, leaking reviewer subagents, or accepting malformed review reports.

The v2 must keep `reviewer` as one skill with internal `lite` and `heavy` review routes. It should use a low-cost preflight to choose the route, validate review report shape deterministically, clean up reviewer subagents after use, and fix the runtime defects found by `debug-skill`.

## Users

- Primary: main Codex agents that call `reviewer` before accepting specs, plans, code changes, research ideas, or execution results.
- Secondary: workflow skills such as `plan2do`, `debug-skill`, `spec2plan`, and future pipeline skills that use `reviewer` as an advisory quality gate.
- Tertiary: users who explicitly ask for review but expect low overhead for small or low-risk artifacts.

## Problem

The first `reviewer` implementation improved quality, but real use exposed avoidable cost and reliability defects:

- Review report schema is ambiguous: the template asks for exactly one top-level `Verdict:` line while also using `Verdict:` under alignment and quality sections.
- Current reviews can overuse subagents for small or low-risk artifacts, wasting tokens, time, and reviewer-agent slots.
- Reviewer subagents can remain alive after producing the review, increasing the chance of hitting subagent limits.
- Source evidence can cite paths that do not exist unless the coordinator checks source existence.
- Behavioral validation used fixtures, which are useful smoke tests but weaker than realistic forward-tests.
- `plan2do` validation feedback for verification evidence is easy to misread: a `## Verification` heading did not satisfy `validate_execution.py`; a `*verification*.md` artifact did.

## Success Criteria

- `reviewer` documents and uses a preflight complexity gate that chooses `lite` or `heavy` before loading broad context or launching a reviewer subagent.
- `lite` review completes inline by default and produces a bounded, short report for low-risk artifacts.
- `heavy` review uses an isolated reviewer subagent by default for non-trivial or risky artifacts.
- A `mandatory-isolation` option allows even lite reviews to run in a subagent when the user or workflow requires context isolation.
- Every reviewer subagent has an explicit lifecycle: dispatch, collect synthesized report, archive or kill the subagent, then keep only the report in the main context.
- A deterministic review report validator rejects malformed reports, including reports with missing top-level verdict, invalid verdict values, invalid route, unsupported severity, missing evidence for major/critical findings, or ambiguous top-level/sub-verdict parsing.
- The current `reviewer` self-review report, dry-review evidence, and intentionally malformed reports are covered by validator tests.
- `reviewer` checks that cited source paths exist or labels unavailable sources clearly before treating them as evidence.
- `plan2do` validation messaging or documentation clearly explains what counts as verification evidence without changing execution semantics.
- Final verification includes realistic forward-tests for at least one lite review and one heavy/subagent review, plus existing fixture-style checks.

## Scope

### In

- Update `reviewer/SKILL.md` with route preflight, lite/heavy semantics, escalation rules, mandatory isolation, subagent cleanup, source-existence checks, and validator usage.
- Update `reviewer/references/review-report-template.md` to remove verdict ambiguity and define distinct labels for top-level verdict and alignment/quality sub-verdicts.
- Update `reviewer/references/subagent-dispatch.md` with lifecycle cleanup requirements and packet minimization.
- Add a small validator script, likely `reviewer/scripts/validate_review_report.py`, for deterministic report validation.
- Add validator fixtures or tests for valid lite reports, valid heavy reports, missing top-level verdict, multiple top-level verdicts, malformed sub-verdicts, missing evidence, invalid severity, and invalid route.
- Add reviewer forward-test artifacts that exercise:
  - a low-risk lite review that stays inline;
  - a high-risk heavy review that uses a subagent and then archives or kills it;
  - a mandatory-isolation lite review path if subagent tooling is available.
- Clarify `plan2do` validation evidence docs or error text so future agents understand that either a `*verification*.md` artifact or a line matching the validator's `Verification` pattern is required.

### Out

- Do not create a separate `reviewer-lite` skill.
- Do not force all upstream skills to call `reviewer`.
- Do not change `plan2do` execution semantics or task status semantics.
- Do not build a GitHub PR bot, daemon, scheduler, or external service.
- Do not vendor third-party review frameworks.
- Do not require subagents for every lite review unless `mandatory-isolation` is explicitly requested.

## Requirements

### Functional

- `reviewer` must start each review with a cheap preflight using only the user goal, artifact type/size, explicit risk hints, and available source list.
- Preflight must classify route as `lite`, `heavy`, or `blocked` with a one-line reason.
- Lite route must be allowed only when all are true:
  - artifact is small, local, and low-risk;
  - source-of-truth is obvious or explicitly supplied;
  - no code behavior, security, privacy, data migration, research novelty, multi-file impact, plan execution, or final acceptance risk is material;
  - user did not request adversarial review or mandatory isolation.
- Heavy route must trigger when any high-risk condition exists, including code behavior changes, security/privacy/data risk, research novelty claims, spec/plan/execution acceptance, cross-file changes, unclear source authority, adversarial mode, failed prior review, or user request for isolated review.
- Mandatory isolation must override lite inline behavior and run the minimal lite review packet inside a subagent when tooling is available.
- If subagent tooling is unavailable, reviewer must state the fallback reason and choose inline lite/heavy according to risk; if isolation is mandatory and unavailable, return `BLOCK`.
- After a reviewer subagent returns, the coordinator must archive or kill that reviewer subagent when supported by available tools and record the cleanup result in the review basis or residual risks.
- Review output must distinguish:
  - top-level verdict: `PASS`, `REVISE`, `BLOCK`;
  - alignment sub-verdict;
  - quality sub-verdict.
- The report template must avoid using the exact same `Verdict:` label for sub-verdicts if the validator depends on top-level verdict parsing.
- The validator must support both lite and heavy reports.
- The validator must fail reports that cite non-existent local source paths as evidence without marking them unavailable or missing.
- The validator or coordinator must reject reports whose severity conflicts with the top-level verdict, such as `PASS` with major/critical findings.
- `reviewer` must keep raw subagent transcripts out of the main context unless the transcript itself is the requested artifact.
- `plan2do` validation docs or error message must explain verification evidence with concrete examples:
  - `artifacts/task5-verification.md`;
  - a final report line that begins with `Verification`.

### Non-Functional

- Lite review should normally fit in a short response and avoid broad file reads.
- Heavy review should keep the main context clean by passing only a compact packet to the subagent and returning only the synthesized report.
- Validator should be dependency-light and runnable with the local Python standard library.
- Changes should preserve current `reviewer` review-only safety semantics.
- Documentation should remain concise and use references for detailed validator/report rules.

## Constraints

- Workspace root is `/data/lcq/.codex/skills`.
- Manual file edits must use `apply_patch`.
- Existing `reviewer` v1 behavior should remain understandable; v2 extends it rather than replacing the whole skill.
- Existing `idea-refine`, `interview-me`, `spec2plan`, and `plan2do` workflows must not be globally modified to require reviewer.
- `plan2do` change is limited to validation-message or documentation clarity unless a later plan explicitly approves more.
- No destructive git operations or commits.

## Assumptions To Validate

- [ ] Inline lite review can catch low-risk artifact defects without materially polluting the main context. Validate with a small doc/metadata fixture and a real small artifact.
- [ ] Heavy subagent review plus immediate cleanup is supported by available subagent tooling. Validate by creating a reviewer subagent, collecting output, then archiving or killing it.
- [ ] A simple Python validator can reliably distinguish top-level verdict from alignment/quality sub-verdicts. Validate with positive and negative fixtures.
- [ ] Source-existence checks can be done without blocking external URL citations. Validate local path checks separately from URL/reference citations.
- [ ] Clarifying `plan2do` verification evidence does not change execution validator semantics. Validate existing `validate_execution.py` behavior before and after docs/message changes.

## Risks

- Lite route may under-review tasks that appear small but are semantically risky. Mitigation: conservative escalation triggers and `BLOCK` when source authority is unclear.
- Mandatory subagent isolation for lite reviews may reintroduce slot pressure. Mitigation: make it opt-in or workflow-required, not default.
- Cleanup tooling may differ across agent providers. Mitigation: document best-effort cleanup and record cleanup result; return residual risk when cleanup is unavailable.
- Validator could become too rigid and reject useful human-written reports. Mitigation: validate only structural invariants needed for safety and false-completion prevention.
- Changing report labels may break existing artifacts. Mitigation: keep validator compatibility mode or document that v2 reports use the new schema.

## Acceptance Checks

- `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/reviewer` passes.
- `python3 /data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py <valid-lite-report>` passes.
- `python3 /data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py <valid-heavy-report>` passes.
- The report validator fails intentionally malformed reports for missing top-level verdict, duplicate top-level verdict, invalid route, invalid severity, major finding without evidence, and `PASS` with major/critical finding.
- A lite review fixture is reviewed without launching a subagent unless mandatory isolation is requested.
- A heavy review fixture launches a reviewer subagent, writes a report, then archives or kills the subagent and records cleanup status.
- A mandatory-isolation lite fixture uses a subagent when tooling is available, or returns `BLOCK` with a fallback reason when unavailable.
- A local-path source citation to a missing file is rejected or labeled as missing evidence.
- `plan2do` validation docs or error text includes concrete examples of acceptable verification evidence.
- Existing `reviewer` dry-review evidence is either migrated to the v2 schema or explicitly retained as v1 historical evidence.

## Open Questions

- Should the review report validator accept v1 historical reports in compatibility mode, or only validate v2 reports?
- Should cleanup mean archive, kill, or whichever lifecycle action is supported by the current subagent tool?
- Should `mandatory-isolation` be a reviewer option name, a packet field, or both?
