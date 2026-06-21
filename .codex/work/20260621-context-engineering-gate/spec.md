# Spec: Context Engineering Gate

## Objective
Improve `/data/lcq/.codex/skills/context-engineering` so it remains a high-quality context governance skill while reducing token load and preventing unnecessary context artifacts. The primary outcome is a leaner, more executable skill that tells agents when to keep context governance internal, when to write a wave-level context pack, when to write task-level packs, and when to emit a Decision Packet.

## Users
- Primary: Codex main agent executing long or risky local tasks such as `spec2plan -> plan2do`.
- Secondary: Codex subagents that need consistent context governance without reading a long policy document.
- Reviewer: The user, who needs evidence that the skill improves quality without wasting context or artifacts.

## Problem
`context-engineering` is useful but currently heavy. Its `SKILL.md` is about 15k characters and loads as one large file. Recent execution of `plan-contract-fail-fast` generated five task-level context artifacts even though the skill says one wave-level pack is usually enough during plan execution. The skill has strong prose rules, but no deterministic gate that turns task risk, phase, and failure signals into a context action.

## Success Criteria
- `context-engineering/SKILL.md` is reduced below 10,000 characters while preserving core semantics.
- A lightweight `context-engineering/scripts/context_gate.py --self-test` passes without third-party dependencies.
- A replay fixture for the recent `plan-contract-fail-fast` scenario recommends one wave-level context pack by default, and task-level packs only when a task has risk, ambiguity, failure, or cross-cutting scope.
- `quick_validate.py /data/lcq/.codex/skills/context-engineering` passes.
- The skill keeps core semantics: `lite`, `full`, `escalate`, Source Hierarchy, Context Starvation Guard, Decision Packet, Context Capsule, and compaction safety.
- No LangGraph, Letta, AutoGen, CUE, Pydantic, or other heavy runtime dependency is required.

## Scope
### In
- Slim `context-engineering/SKILL.md` into a concise entrypoint with routing rules.
- Move detailed guidance into references such as `references/modes.md`, `references/artifact-policy.md`, and `references/replay.md`.
- Add `scripts/context_gate.py` with deterministic inputs and outputs.
- Add self-tests for the gate.
- Add a replay example based on `plan-contract-fail-fast` showing expected artifact decisions.
- Update `agents/openai.yaml` only if the final behavior or description changes enough to make metadata stale.

### Out
- Do not implement a real `/compact` actuator.
- Do not change `plan2do`, `spec2plan`, or other skills.
- Do not introduce LangGraph, Letta, AutoGen, SWE-agent, or similar runtimes as dependencies.
- Do not make context artifacts mandatory for every task.
- Do not delete existing work artifacts from previous executions.

## Requirements
### Functional
- `SKILL.md` must state the core rule, mode choice, artifact decision rule, escalation triggers, and reference routing.
- `context_gate.py` must accept enough information to decide one of these actions: `internal`, `wave-pack`, `task-pack`, `decision-packet`, `capsule`, or `compact-request`.
- `context_gate.py --self-test` must cover:
  - routine reversible task -> `internal` or `wave-pack`;
  - normal multi-task plan execution -> `wave-pack`;
  - failed command or patch miss -> `task-pack` or `escalate`;
  - destructive/security/API/schema action -> `decision-packet`;
  - high context pressure with phase boundary -> `capsule` then `compact-request`.
- The replay reference must explain why the recent `plan-contract-fail-fast` execution should not need five task-level packs by default.
- Reference files must preserve full details removed from `SKILL.md`.
- External project inspiration must be documented as pattern-only reuse:
  - LangGraph for state/checkpoint lifecycle;
  - Letta for working vs archival memory separation;
  - SWE-agent for trajectory/replay separation;
  - AutoGen for agent state/message abstraction.

### Non-Functional
- No third-party Python packages are required.
- The gate output must be simple enough for future agents to follow without reading every reference file.
- The implementation must favor quality over token savings when a risky decision is pending.
- The skill must remain compatible with existing Codex skill loading rules.

## Constraints
- Keep edits inside `/data/lcq/.codex/skills/context-engineering` and the topic workspace unless a validator requires metadata updates.
- Preserve the existing skill name `context-engineering`.
- Preserve the existing principle that summaries are continuity hints, not evidence.
- Preserve the existing rule that compaction is not assumed to be callable from inside the current session.
- Use plain Python stdlib for scripts.

## Assumptions To Validate
- [ ] Reducing `SKILL.md` below 10k characters is possible without losing core behavior - validate by checking character count and reviewing references.
- [ ] A deterministic gate can cover common context decisions without overfitting - validate with `--self-test` and replay fixture.
- [ ] `agents/openai.yaml` may not need changes - validate after SKILL.md rewrite.

## Risks
- Over-compressing `SKILL.md` could remove important safety semantics - mitigate by moving detail to references and adding routing instructions.
- `context_gate.py` could become a brittle policy engine - mitigate by keeping it advisory and small.
- Replay fixture could overfit to one recent task - mitigate by adding at least one routine task and one high-risk task self-test.
- Splitting references could make agents miss important details - mitigate by direct reference routing in `SKILL.md`.

## Acceptance Checks
- `python3 /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/context-engineering`
- `python3 /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py --self-test`
- `python3 -m py_compile /data/lcq/.codex/skills/context-engineering/scripts/context_gate.py`
- A character-count command confirms `context-engineering/SKILL.md` is below 10,000 characters.
- Manual review confirms references preserve Source Hierarchy, Context Starvation Guard, Decision Packet, Context Capsule, compaction safety, anti-pollution rules, and conflict handling.
- Replay check confirms the `plan-contract-fail-fast` scenario maps to one wave-level context pack unless a task has failure/risk triggers.

## Open Questions
- Should `context_gate.py` output JSON only, text only, or both?
- Should replay fixtures live in `references/replay.md` only, or should they also be machine-readable test data under `assets/` or `fixtures/`?
