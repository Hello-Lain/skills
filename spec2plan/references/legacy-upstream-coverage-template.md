# Legacy `Upstream Coverage` Migration Template

Use this when an existing `plan.md` predates the `Upstream Coverage` requirement and must be upgraded without losing upstream context.

Goal:

- reconstruct the upstream artifact chain;
- preserve still-relevant facts;
- mark true omissions explicitly instead of inventing thin summaries.

## Inputs To Load First

- current `plan.md`
- linked `spec.md` when it exists
- linked `idea.md` when it exists
- `manifest.yaml` in the shared workspace when it exists
- any cited issue/PRD/ADR paths named in `Evidence Inspected` or `Execution Handoff`

If an upstream artifact cannot be found, say so directly in `Source artifacts` and `Open Questions`. Do not guess.

## Insert This Section After `## Spec Summary`

```markdown
## Upstream Coverage

- Source artifacts:
  - `.codex/work/<yyyyMMdd>-<topic-slug>/spec.md`
  - `.codex/work/<yyyyMMdd>-<topic-slug>/idea.md`
  - `manifest.yaml`
- Carried forward:
  - problem = <user pain or trigger preserved from upstream>
  - user = <primary user or operator preserved from upstream>
  - success criteria = <observable outcomes preserved from upstream>
  - scope boundaries = <in/out or not-doing decisions preserved from upstream>
  - constraints = <binding limits preserved from upstream>
  - assumptions / risks = <key uncertainties still relevant during execution>
- Added planning detail:
  - files / symbols = <new implementation evidence introduced by the plan>
  - commands / validation = <new executable checks introduced by the plan>
  - task decomposition = <new waves, dependencies, rollback, rollout, monitoring detail>
- Dropped / deferred upstream details:
  - None
```

## Migration Rules

- `Carried forward` must name facts, not headings.
- `Added planning detail` must contain planning/execution detail that did not already exist upstream.
- `Dropped / deferred upstream details` must be `None` or a concrete item plus reason:
  - `pricing strategy deferred because packaging does not affect implementation order`
  - `alternative direction B dropped because it was explicitly rejected in idea.md`
- If upstream artifacts disagree, record the conflict here and resolve it again in `Assumptions`, `Open Questions`, or `Execution Handoff`.
- If the plan is legacy and the upstream source was never saved, cite the best surviving artifact path instead of pretending a canonical file existed.

## Fast Upgrade Checklist

- [ ] Exact upstream paths cited
- [ ] Problem/user/success/scope/constraints preserved
- [ ] New planning detail made explicit
- [ ] No silent omission of risks or not-doing boundaries
- [ ] Any dropped/deferred detail has a reason
- [ ] `scripts/validate_plan_contract.py <plan.md> --mode light|heavy` passes after insertion
