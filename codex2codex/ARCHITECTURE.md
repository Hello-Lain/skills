# Architecture

For users: see [`README.md`](./README.md). This document is for people (or agents) modifying the harness: why it is shaped this way, where the sharp edges are.

## Design premise: the consumer is an agent

Every design decision optimizes for the orchestrating agent's economics, not human ergonomics:

1. **Observation is pull, completion is push.** Streaming worker events into the orchestrator's context would burn tokens linearly with worker runtime. Instead the daemon reduces the event stream to disk digests (`status.json`, `events.log`, `result.md`); the orchestrator polls only when it cares, and a blocking `wait`/`dispatch` (run as a background shell) delivers a push — the completion notification with the result attached, or a checkpoint wake-up when `wait --timeout` elapses while the worker keeps running. Supervised dispatch leans on that second case: a `wait --timeout` set near the expected duration is a sparse checkpoint, letting the orchestrator read one `status` and `steer` mid-run without ever streaming.
2. **Exit codes are the API.** `0` done, `2` failed/interrupted, `3` worker has a question, `4` daemon dead, `1` timeout. An agent branches on these without parsing prose.
3. **One call per intent (one-shot), or a supervised loop.** `dispatch` = (ensure daemon → start → wait → print result) and `reply` = (follow → wait → print last-turn result) are symmetric single background calls — one-shot driving costs the same tool calls as a native subagent, which suits trivial work. For substantial work the orchestrator instead uses `start` plus `wait`, so the door to `status`/`steer` stays open mid-run; how often it actually checks is its judgment, not a fixed cadence. Same pull/push primitives — just sampled when it matters instead of a single fire-and-forget.
4. **Two-way by protocol, not plumbing.** A preamble (auto-prepended to every brief) frames the worker as a teammate: never commit; and rather than guessing or silently complying, end with a `QUESTION:` paragraph — when blocked, or to flag a better approach, a wrong assumption, or a tradeoff before a direction locks in. The daemon promotes that to `needs_input` → exit 3 → the orchestrator answers or discusses with `reply` on the same thread. The same primitives run the other way: the orchestrator can dispatch a read-only `consult` brief to think a problem through with a worker, not just hand off work.

## Process topology

```
meight (CLI, ~/.local/bin)  ──── Unix socket, JSON-lines ────  per-repo daemon
                                                                │ openai-codex SDK (1 client)
   status/result/wait read disk directly                        ▼
   (work without the daemon)                              codex app-server (1 process)
                                                                │ N threads multiplexed
<repo>/.meight/workers/<name>/                          ▼
   brief.md · status.json · events.log · result.md   ◀── per-worker consumer thread
```

- **State home** = git root of the invoking cwd (`MEIGHT_HOME` overrides) → one independent daemon per repo.
- The SDK spawns `codex app-server --listen stdio://` and speaks JSON-RPC; per-turn notifications are routed by the SDK's internal MessageRouter, which is what allows N concurrent turns over one process.
- The daemon holds `Thread`/`TurnHandle` objects in a registry — this is what makes `steer`/`interrupt`/`follow` possible, and why `follow` does not survive a daemon restart (v1 scope; `thread_resume` exists in the SDK and is the natural extension).

## State machine

`starting → running → {completed | failed | interrupted | needs_input}`

- Transition priority: **preserve failed/interrupted > QUESTION promotion > completed**. A non-retryable `error` event marks the worker failed and a later `turn/completed(status=completed)` must not overwrite it.
- Unknown/missing terminal turn status maps to `failed`, never `completed` (the wait contract depends on it).
- `needs_input` carries a **source**: `"question"` (final-paragraph `QUESTION:` detected after a completed turn — a real, final state) vs `"tool"` (mid-turn tool/approval wait — transient). `classify_wait_state()` returns exit 3 **only for source=question**; a tool-wait that survives to stream-end is converted to `failed`. This distinction exists because an early review showed tool-waits masquerading as final states.
- Non-question terminal transitions clear `needs_input_detail`/`source` (stale-question bug, found in review).

## Runner Recovery

`run_wave.py` adds a bounded recovery layer above the daemon state machine:

- Preflight runs `meight doctor --json` before implementation waves to catch missing CLI/SDK/role-skill readiness as `TOOL_INFRA`; exhausted preflight exits as `INFRA_FAILED`.
- Active `starting`/`running` workers that hit a checkpoint with stale progress are steered once with a scoped recovery brief; if they remain unhealthy, the runner interrupts before reusing the same worker name.
- `PRE_FIRST_ITEM_STALL` has priority over generic stale-worker handling. It means the worker reached `turn/started` but no item ever started in that turn, no token usage exists, and no current item arrived before the active wait became stale. This is classified as an infrastructure/app-server stream failure, not a task quality failure.
- Recovery for `PRE_FIRST_ITEM_STALL` rotates the daemon/app-server into a fresh `MEIGHT_HOME`, runs a nonce smoke worker to prove the new stream path, then retries the original worker once. Smoke failure or a second pre-first-item stall exhausts as infra recovery failure; the runner must not keep retrying.
- Terminal recoverable workers are followed on the same thread before restart. Same-name restarts and fresh replacement starts are bounded by `--same-worker-restarts` and `--fresh-worker-restarts` (`0..3`, default `1` each).
- Replacement worker success is copied back to the original manifest worker directory so `validate_wave.py` validates the manifest contract rather than an ad hoc worker name.
- `PATCH_BODY` is a runner-owned fallback, not lead fallback. Implementation workers may emit a complete `apply_patch` patch or unified diff when direct editing failed; the runner extracts paths, rejects absolute/traversal/out-of-scope paths, applies the patch, then requires real changed files.

Recovery classification is deliberately small and terminal outcomes are stable:

| Category | Examples | Exhausted outcome |
|---|---|---|
| `TRANSIENT_API` | provider timeout, 5xx, unavailable provider, no active credentials, app-server/socket disconnect | `INFRA_FAILED` |
| `TOOL_INFRA` | tool backend, approval backend, `apply_patch`, MCP/tool-call, meight daemon/socket failure | `INFRA_FAILED` |
| `PATCH_CONTEXT` | stale hunk, target changed, patch context mismatch, failed expected lines | `CONTRACT_FAILED` |
| `CONTRACT_FAIL` | missing artifact, blocked artifact, missing review verdict, missing expected diff | `CONTRACT_FAILED` |
| `TASK_BLOCKER` | real `QUESTION:`, ambiguous requirement, design conflict, writable-scope conflict, repo-unanswerable decision | `TASK_BLOCKED` |

Validator gates stay authoritative after recovery. A worker can recover from infrastructure failure, but cannot pass with a blocked artifact, missing output artifact, missing implementation file change, missing verification evidence, or review output without `Verdict: PASS|FAIL`. Lead fallback is prohibited unless the orchestrator explicitly requests it; otherwise failed recovery must surface as `INFRA_FAILED`, `CONTRACT_FAILED`, or `TASK_BLOCKED`.

Recovery cleanup and reporting are part of the contract: every rotated `MEIGHT_HOME` must be shut down and removed unless debugging/resume was explicitly requested, completed or blocked sidecar workers must not be left alive, and artifacts may include only redacted summaries of stall class, nonce smoke result, retry count, cleanup status, and paths. Raw worker transcripts, raw event streams, credentials, and private logs must not be copied into lead context or artifacts.

## Concurrency design

Three locks, one direction — **adding any reverse acquisition is a deadlock**:

| Lock | Protects | Order |
|---|---|---|
| `reg_lock` | worker registry (copy, then release) | outermost, never held into worker calls |
| `ctl_lock` (per worker) | all `TurnHandle` control calls: steer / interrupt / force-shutdown | acquired before… |
| `w.lock` (per worker) | status dict + digest writes | …innermost. Consumer threads take only this |

- **Turn generation ids**: each `follow` bumps `worker.generation`; the consumer thread carries its generation and every event/stream-end/exception handler drops work from stale generations. This is the mechanism that makes follow safe against a previous turn's late events.
- **Daemon singleton**: `flock(LOCK_EX|LOCK_NB)` on `daemon.lock`, plus a live-socket ping probe before ever unlinking an existing socket. Two concurrent cold dispatches may both spawn — flock guarantees one survives.
- **Liveness**: never trust `pid_alive` alone (pid reuse); socket ping is the primary signal, with a 2-strike policy in `wait`.
- **Health checks are passive**: `doctor` reports socket/pid/lock/heartbeat/worker health and redacted env presence but never mutates state.
- **Recovery is dry-run-first**: `recover --dry-run` shows stale daemon artifacts; `recover --force` refuses live socket/held lock, snapshots metadata, then removes only stale daemon artifacts.
- **Stall handling is advisory**: status diagnostics and `wait --stall-timeout` can report stale progress, but they never interrupt automatically.
- `status.json` writes: temp name includes pid+thread-id, then `os.replace` (a fixed temp name lets concurrent writers steal each other's files).

## Orchestration policy

The routing we run in production with Codex as the orchestrator; adapt to taste.

| Work | Route |
|---|---|
| Bounded implementation with a clear spec; code review; browser/runtime checks | Codex worker via `meight` |
| Exploration fan-out; fresh-context verification; anything needing the orchestrator's own tooling | Fresh Codex worker or Codex subagent |
| High-stakes or irreversible paths | Either — but runtime evidence + explicit orchestrator sign-off regardless |

- **Independent review is mandatory**: worker Codex implements -> lead Codex verifies; lead Codex implements -> a fresh worker reviews (`--sandbox ro --effort xhigh`, re-review via `follow` on the same worker). Same-thread self-review is not accepted.
- Worker model/reasoning is per-dispatch: omit `--model` to inherit `~/.codex/config.toml`, and override effort only with `--effort high|xhigh`.
- Workers never commit; git belongs to the orchestrator (enforced by the preamble).
- Briefs must point at *existing patterns* relevant to the task — detail-oriented reviewers flag absent context as defects otherwise.
- `follow` at most ~2 times per thread, then reset with a fresh brief (long Codex sessions degrade).
- Role effort, prompt text, aliases, caps, sandbox, context profile, and preferred skills are local to this skill in `roles/*.yaml`; `scripts/roles.py` is only the loader.
- Wave profile defaults to `role`: `prepare_wave.py` resolves each worker's YAML `context_profile` and records the concrete `minimal|standard|full` value in `manifest.json`. Use static `doctor --json` for routine global-skill availability checks; live worker smoke tests are reserved for worker-execution debugging because they spend a full worker context.

## Hardening history

Built by a Codex orchestrator, adversarially reviewed by Codex across five rounds before v1 — 13 real defects found and fixed. Classes of bugs, as a checklist for future changes:

1. Daemon double-start via stale pid + socket unlink (→ flock + ping probe)
2. Follow racing a previous turn's stream thread (→ generation ids, consumer-finished gate)
3. SDK failure leaving zombie `starting` workers that block their name forever (→ mark-failed on turn-creation exception)
4. Concurrent control calls on a shared `TurnHandle`, including the force-shutdown path bypassing the lock (→ per-worker `ctl_lock` everywhere)
5. Same-name reuse unlinking files a live thread still writes (→ consumer-finished gate)
6. Fixed temp-file name corrupting `status.json` under concurrent writers (→ unique temp names)
7. Unknown turn status mapped to `completed`, violating the wait contract (→ completed-only mapping)
8. pid-reuse false-alive (→ ping-first liveness)
9. Tool-wait `needs_input` surfacing as exit 3 / masking failures; stale question detail after failure (→ `needs_input_source`, terminal-transition clears)
10. Enum-vs-string comparison silently broken by pydantic's default `model_dump()` (→ `mode="json"` everywhere)

State-machine changes should re-run the fake-event scenarios (tool-wait→stream-end, question persistence, failed-preservation, multi-line question, wait classification) plus the live checks in `SPEC.md`.

## Operational notes

- **Editing `meight.py` does not affect a running daemon** — restart it (`meight shutdown`, next dispatch auto-starts). Easy to forget.
- Prefer explicit per-task `MEIGHT_HOME` and foreground daemon while debugging health/recovery issues.
- `doctor` is safe to run repeatedly; use `recover --dry-run` before any state cleanup.
- Beta SDK (`openai-codex==0.1.0b3`, pinned): before bumping, re-introspect the API surface (`inspect.signature`), dump real event payloads (`MEIGHT_DEBUG=1` → per-worker `debug-events.log`), and re-run the verification suite.
- Approval requests arrive as SDK server-requests (auto-accepted by the SDK's default handler), not stream notifications — the `needs_input` tool path is defensive.
- Per-turn `cwd`/`sandbox`/`model`/`effort` come from the SDK's `Thread.turn()` — worktree isolation is just `--cwd`.

## Deliberate non-features (v1)

Custom approval handling; structured worker output via `output_schema` (SDK supports it — natural extension for machine-readable reports); automatic worktree creation; daemon supervision/auto-restart; `follow` across daemon restarts via `thread_resume`; multi-repo single daemon.
