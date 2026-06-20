Salvaged-From-Worker: coding-1

## Changed Files

- `codex2codex/SKILL.md`
  - Added `PRE_FIRST_ITEM_STALL` guidance: infra/app-server stream failure, not task quality failure.
  - Documented fresh `MEIGHT_HOME`, nonce smoke worker, retry-once limit, infra failure, cleanup, redacted recovery artifact rules.
- `codex2codex/ARCHITECTURE.md`
  - Added runner recovery contract: stall priority, fresh home rotation, nonce smoke, one retry, cleanup, no raw transcript/event leakage.

## Verification

- Ran: `rg "PRE_FIRST_ITEM_STALL|nonce smoke|MEIGHT_HOME" codex2codex/SKILL.md codex2codex/ARCHITECTURE.md`
- Result: pass; 10 matches across both scoped docs.

## Judgment Calls

- Docs-only; no tests added.
- Operator commands in `SKILL.md`; rationale/contract in `ARCHITECTURE.md`.

## Residual Risks

- None identified.
