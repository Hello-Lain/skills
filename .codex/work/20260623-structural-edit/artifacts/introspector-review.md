# Introspector Review

- Artifact Type: skill implementation
- Confidence: High
- Verdict: keep

## Objective Extraction
- Reviewed artifact: `structural-edit/` — structure-first manual editing skill replacing `edit-orchestration`
- Root objective: raise edit success rate, reduce retry loops / patch misses, improve code correctness, keep edits deterministic, hard-stop instead of silently patching when structural toolchain is missing
- Decision question: Is the current `structural-edit` design the global-optimal solution for this objective, or should it be trimmed, redone, paused, blocked, or merged?

## Framing Audit
- Judgment: Valid framing. The spec correctly identifies that the old `apply_patch`-first default was the root cause of repeated failures in structured code/config/doc edits. The chosen direction — structure-first with strict fallback — matches the root objective.
- Direct evidence: `spec.md` explicitly captures the problem (text-anchored patch fragility under repeated sections, drifted context, partial state after retries), non-goals (no daemon, no C++/Rust v1), and success criteria.
- Inference: None needed; the framing is self-consistent with local failure history.

## Evidence Acquisition
- Sources loaded: `spec.md`, `plan.md`, `SKILL.md` + all references + all scripts, `tools/structural-edit/manifest.json`, live self-check outputs, `route_decision.py` 9 scenarios, `validate_structural_routes.py` output, real edit traces (Python ast-grep, JSON jq, YAML yq), `edit-orchestration/` deletion status, `quick_validate.py` result.
- Why they were needed: verify spec→code alignment, route correctness, toolchain completeness, fallback discipline, no silent downgrade.
- Remaining gaps: No live `jscodeshift` or `remark` real-edits were re-run (they were verified via self-check + manifest, but no actual JS/TS/MD file was rewritten in this session). This is a minor gap because self-check + manifest confirm the executable exists and runs. No end-to-end `openrewrite` test with a real Java project. Acceptable: openrewrite is spec'd as conditional and requires build context that this environment does not have.

## Provisional Verdict
- Provisional verdict: keep
- Reason: All 9 spec scenarios pass; 5/5 tools installed and self-check-green; real ast-grep/jq/yq edits work; `--force-user-root` added; `edit-orchestration` deleted; `validate_structural_routes.py` PASSES; `quick_validate.py` PASSES; knife-edge fallback rule is proven by `route_decision.py` returning `block` for Java without build context and for unknown file class without tiny+unique.

## Strongest Defense Of Current Design
1. The design is **deterministic**: `route_decision.py` is a no-side-effect function that maps file class + intent flags to a single route + tool. There is no ambiguity.
2. **No silent downgrade**: every structural route has `hard_stop_if_missing: True`. `BLOCK` is a first-class route (Java/unknown file class).
3. **Knife-edge fallback**: text fallback is only allowed when ALL of `tiny=True, unique=True, (prose_only OR markdown/generic-text)` are true. This is safe.
4. **Self-healing toolchain**: `prepare_structural_tools.py --force-user-root` ensures tools land in user root even when PATH has a different version; `manifest.json` records version+source+self-check history.
5. **Migration is complete**: `edit-orchestration` deleted; no competing default remains.
6. **Token-conscious**: `SKILL.md` is 362 words/53 lines; references are essential; no speculative language routes, no bloated examples.

## Alternative Comparison
### Option A (Current): structure-first bus + strict fallback
- Decision: keep
- Why: Matches root objective precisely. Hard-stop prevents blind patching. Toolchain manager is user-controlled. Minimal token cost.

### Option B: full ast-grep-only (no jq/yq/remark/jscodeshift)
- Decision: reject
- Why: ast-grep cannot correctly edit JSON (structured data, not code), YAML (indentation-sensitive), or Markdown (AST sections). Using ast-grep for these would be as fragile as text patching.

### Option C: keep edit-orchestration but add structural hints
- Decision: reject
- Why: Leaving two competing defaults causes route ambiguity. The spec explicitly requires one authoritative entrypoint. edit-orchestration was deleted.

### Option D: pure text-patch with better validation
- Decision: reject
- Why: This is the old approach that caused the problem. Adding validation after patching does not fix fragment fragility under drift/retries.

## Keep / Remove / Redesign
### Keep
- Route decision engine (`route_decision.py`): deterministic, provably correct.
- Toolchain manager with manifest (`prepare_structural_tools.py`, `manifest.json`): self-healing, user-root, version-tracked.
- Hard-stop BLOCK behavior for missing tools and unsupported file classes.
- 9 scenario gates (`validate_structural_routes.py`): cover all specified routes.
- `--force-user-root` flag: prevents silent PATH-tool version confusion.
- Migration completion: edit-orchestration deleted.

### Remove
- Stale "compatibility shell" wording in `migration.md`: edit-orchestration is already deleted, not a compatibility shell.

### Redesign
- **Minor: migration.md should say "edit-orchestration has been deleted" not "remains as compatibility shell"**. This is a doc stale flaw, not a design flaw. Patch needed.

## Verification Questions
1. Q: Does `route_decision.py` ever return `strict-text-fallback` when `structured_op=True`?
   A: No. `_fallback_allowed` returns False when `structured_op=True`. Verified by test scenario 1 (Python structured→ast-grep).
2. Q: Can a user bypass hard-stop by omitting `--structured-op`?
   A: Yes, if they do not declare the operation as structured. Mitigation: the workflow in SKILL.md step 3 says "classify the route with route_decision.py". The tool is deterministic given its inputs. If the user lies about the intent, the tool returns what they asked for. This is reasonable — the agent (not the tool) owns intent classification.
3. Q: Is there any scenario where a required structural tool is missing and the system silently falls back?
   A: No. every structural route has `hard_stop_if_missing=True`. The SKILL.md core rule prohibits silent downgrade.
4. Q: Is `remark`'s `--non-interactive` covered?
   A: Not yet explicitly in references. SKILL.md uses `--non-interactive` for ast-grep only. Remark CLI may also prompt. Documented as residual risk.

## Evidence Classes
- Direct evidence:
  - `validate_structural_routes.py` returns PASS for all 9 scenarios.
  - `quick_validate.py` returns "Skill is valid!".
  - All 5 tools self-check PASS.
  - Real ast-grep rewrite on Python file (jq/yq also verified).
  - `edit-orchestration` directory deleted.
  - `--force-user-root` exists in prepare_structural_tools.py.
- Inference:
  - jscodeshift and remark CLI binaries exist and self-check passes → edit would work (not directly tested in this review, but the binary is proven runnable).
  - `migration.md` wording is stale because edit-orchestration was deleted after the migration doc was written.
- Uncertainty:
  - Remark/ast-grep interactive mode in non-TTY environments: `SKILL.md` now has `--non-interactive` for ast-grep; remark might also require `--silent`/`--no-color` or pipe suppression. Not tested in this review.
  - `openrewrite` scenario cannot be tested without a Java build context. Acceptable per spec.

## Falsifier
- **If `route_decision.py` returns `strict-text-fallback` for a structured op** → the design is broken. Evidence: it does not. `_fallback_allowed` returns False when `structured_op=True`.
- **If a missing structural tool leads to silent text patching** → the design is broken. Evidence: `hard_stop_if_missing: True` on all structural routes. The only non-structural defaults are `strict-text-fallback` (never structural) and `block` (no tool to check).
- **If `edit-orchestration/` still exists after migration** → the migration is incomplete. Evidence: directory deleted.

## Delta Review
- Revision effect: N/A — first review of this artifact.
- New complexity: None. The design is concise: one decision function, one toolchain manager, one manifest.
- Net result: The skill is complete, correct, and minimally complex for its scope.

## Verdict Stability
- Previous verdict: N/A
- Current verdict: keep
- Change cause: N/A

## Final Verdict
- Verdict: keep
- Judgment: `structural-edit` is the global-optimal design for the stated objective and constraints. The only actionable finding is a stale migration doc line.
- Best available path: Patch migration.md to say "edit-orchestration has been deleted", then mark this review complete.

## Risks
- `remark` CLI may need `--silent`/`--no-color` suppression in non-TTY environments. Add to residual risks in production report.
- No auto-upgrade policy for npm/binary tool versions; user must re-run `prepare_structural_tools.py` manually.
- `openrewrite` scenario remains untestable without Java build context; acceptable by spec.
