SPEC2PLAN_ARTIFACT_V1
phase: reviewer
status: complete
artifact:
## Scenario Probes
- Add seeded false-PASS capsule: review artifact missing/FAIL but `run-capsule.json` claims PASS → `validate_execution_complete.py` must fail.
- Add raw-leak probe: capsule contains `events.log`, `result.md` turn transcript, or long worker body text → `validate_capsule.py` must fail.
- Add evidence-integrity probe: capsule references missing/empty artifact or hash mismatch → fail closed.
- Add dry-run misuse probe: `run_plan.py --dry-run` emits/records success capsule or executable-complete status → fail.
- Add legacy-state probe: old `execution-state.json` without capsule fields remains readable but new-run final acceptance requires capsule.
- Add failure-capsule probe: wave failure writes compact blocker/risk/evidence refs without raw transcript leakage.

## Code/doc contradictions
- `codex2codex/SKILL.md` says `scripts/run_plan.py --dry-run` is compile-only and never quality gate; planner correctly repeats this, but Task 12 still bundles dry-run with final gates. Fix wording so dry-run proves compile compatibility only.
- `codex2codex/SKILL.md` default artifacts live under `.codex/specs/<slug>/`; planner routes task artifacts under `.codex/work/.../artifacts/`. This may work as explicit output paths, but conflicts with codex2codex default/shared-state docs and plan-contract wording.
- Review workers must write only `review*.md`; Task 13 `Writable scope` includes product files plus `review.md`, creating an avoidable write-scope risk.
- `validate_execution_complete.py` currently has no capsule parameters and only validates execution-state, artifacts, review PASS, summaries, cleanup. Plan must specify exact integration path/API for capsule validation.
- Current `execution_state.py` stores plan/wave receipts only; planner assumes capsule hash/status fields but does not define version/migration semantics beyond “legacy readable.”

## Repo-unanswerable user questions
- Default hard capsule budget: 4k, 6k, or 8k tokens.
- Failure detail policy: compact expanded failure detail by default vs evidence links only.
- Complex-mode trigger: explicit CLI flag first vs automatic multi-wave/high-risk/review-FAIL heuristic.
- Artifact location policy: canonical capsule only in generated `.codex/specs/<slug>/` vs mirrored into `.codex/work/<topic>/artifacts/`.
- Gatekeeper role: use existing `review` role for MVP or introduce explicit `gatekeeper`.

## Blocking issues
- Task 13 review writable scope is unsafe/invalid for codex2codex review semantics; product files must be read-only scope, writable scope only `.codex/work/.../review.md`.
- Token-reduction validation is too proxy-level: chars/token estimate + raw-leak regex does not prove lead-context reduction or missed-defect rate. Needs measurable acceptance fixture/baseline.
- Quality gate validation lacks exact validator contract: capsule schema, hash algorithm, evidence claim types, and invocation from `validate_wave.py`/`validate_execution_complete.py` are underspecified.
- Same-wave Wave 5 risk: Task 8 changes `run_plan.py`; Task 9 changes `validate_execution_complete.py`/`validate_wave.py`. Both depend on shared capsule state/API from Task 7 and could diverge without a locked schema artifact.
- Blackboard MVP may be over-scoped: direction says opt-in complex mode “not default MVP,” but plan includes full blackboard implementation in early Wave 2, increasing blast radius before capsule path is proven.

## Recommended fixes
- Split a schema-contract task before coding: define `run-capsule.json` fields, schema version, hash algorithm, evidence claim types, budget policy, legacy behavior, CLI contracts.
- Move blackboard to optional later wave or explicit stretch task unless orchestrator confirms MVP scope expansion.
- Correct Task 13: `Writable scope: .codex/work/20260620-codex2codex-context-firewall/review.md`; product paths under read-only review scope/Files likely touched only.
- Add concrete token validation: compare pre/post lead-facing stdout/artifact bytes on at least one fixture run; set threshold and fail if capsule exceeds chosen budget or includes raw transcript markers.
- Add validator acceptance matrix to Task 3/9: PASS fixture, review FAIL, missing artifact, hash mismatch, dry-run, raw leak, legacy no-capsule, failed wave compact capsule.
- Add a Gate B schema freeze: Task 7-9 cannot start until `validate_capsule.py` fixtures pass and CLI/API contract is documented.
SPEC2PLAN_ARTIFACT_END
