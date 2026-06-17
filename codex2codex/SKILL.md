---
name: codex2codex
description: "Use only for explicit /codex2codex requests, worker delegation, worker review/verification/arbitration, or Decision Council analysis. Coordinate Codex workers through meight with supervised start/wait loops, pushback, and lead-side verification. Do not use for ordinary tasks."
---

# Codex2Codex

Lead owns decomposition, arbitration, integration, verification, user communication, and git. Workers own bounded reasoning, execution, or review.

## Use
- Use only when the user explicitly asks for `/codex2codex`.
- Prefer the smallest fit: Consult-first, Implement + audit, Lead implementation + fresh review, Dual proposal + synthesis, Partitioned execution + cross-review, Verifier-only pair, Workflow runner + loopback auditor, Arbiter, Decision Council.
- If the task is trivial, short, or low-risk, stay in the lead session.

## Workflow
- Resolve `meight` once: `meight` -> `codex2codex/.venv/bin/python meight.py` -> `python3 meight.py` (auto-reexecs into the skill `.venv` when `openai_codex` is absent).
- Start each `/codex2codex` request with a fresh state dir: `RUN_HOME=$(mktemp -d "${TMPDIR:-/tmp}/meight-${PWD##*/}-XXXXXX")`. Record it.
- Prefix every meight command in that request with the same `MEIGHT_HOME="$RUN_HOME"`; do not reuse `$REPO/.meight` unless explicitly debugging/resuming.
- Use `--cwd` for worker workdir; `MEIGHT_HOME` is only harness state, not the worker repo.
- After terminal results are read and no worker is active: `MEIGHT_HOME="$RUN_HOME" meight shutdown || true`, then `rm -rf -- "$RUN_HOME"`.
- For stale state or SDK issues: `MEIGHT_HOME="$RUN_HOME" meight doctor`; require `openai_codex_import: True`; then `MEIGHT_HOME="$RUN_HOME" meight recover --dry-run`, and `recover --force` only if safe.
- Use `start` + `wait` for substantive work; use `dispatch` only for trivial short low-risk tasks.
- Exit `1` is a checkpoint; exit `3` means `QUESTION:`.
- Workers never commit, push, or recurse into `/codex2codex`.

## Brief
Keep briefs compact: `Role, Goal, Scope, Constraints, Challenge contract, Verification, Output contract, Report, Handoff Capsule`.
Council adds: `Decision question, Objective function, Hard constraints, Known options, Unknowns, Failure modes, Reversibility, Evidence required, Decision record output`.

## Contracts
- Ask workers to end with `QUESTION:` when blocked, when a better path exists, or when direction could change.
- Progress-only worker output is invalid; verify the artifact before accepting it.
- For substantive or structured outputs, validate result files with `validate_result_contract.py` when practical. New results must include `## Handoff Capsule`; use `--allow-missing-handoff` only for old artifacts.
- For structured worker results, use role headings:
  - Proposer: `## 提案`, `## 理由`, `## 证据`, `## 风险`, `## 替代方案考虑`
  - Red-Team Reviewer: `## 审查对象`, `## 假设挑战`, `## 遗漏风险`, `## 反证`, `## 替代方案`
  - Constraint Auditor: `## 约束清单`, `## 合规状态`, `## 违规分析（如有）`, `## 影响评估`
  - Rollback Planner: `## 可逆性评估`, `## 回滚步骤`, `## 恢复时间预期`, `## 不可逆风险`
  - ADR Synthesizer: `## 上下文`, `## 决策问题`, `## 选项评估`, `## 约束合规性`, `## 关键分歧`, `## 决策`, `## 理由`, `## 后果`, `## 后续行动`
- Every substantive `result.md` ends with:
  - `## Handoff Capsule`
  - `Goal`, `Current state`, `Authoritative artifacts`, `Decisions`, `Verification`, `Remaining risks`, `Next action`, `Suggested skills`, `Redactions / omitted raw data`
- After each result, read the artifact, check the contract, and use at most one targeted `reply`/`follow` if something is missing.
- `NO-GO` means fix and re-review.
- Load nested skills in the lead session first and preserve all user-confirmation gates.
- Summarize final roles, disagreements, changed artifacts, evidence, risks, and any user decision needed.

## Decision Council
Use only for consequential choices. Default workers: Proposer, Red-Team Reviewer, Constraint Auditor; add Rollback Planner or ADR Synthesizer only when risk justifies it. Evidence beats votes. Limit each worker to one `reply` or `follow` turn. Show the final ADR or decision summary to the user before consequential changes.

## Command Notes
- `status`: plan, changed files, tokens, recent tail.
- `doctor`: daemon health.
- `recover --dry-run`: stale cleanup candidates.
- `steer`: mid-run correction.
- `interrupt`: cancel unsafe runs.
- Worker artifacts: `$RUN_HOME/workers/<name>/{brief.md,status.json,events.log,result.md}` during the current request only.
- Re-run the pinned `openai-codex` SDK suite when upgrading the SDK.

## Nested Skill Handoff
Pass only the nested skill, path, current phase, do-not-advance gate, challenge contract, and output contract.
