# codex2codex SPEC

`codex2codex` is a harness that lets an orchestrator run multiple Codex
workers in parallel.

Core design goals:

- Observation is pull-based through compact disk digests to save tokens.
- Steering uses mid-turn input so active work is not discarded.
- Push-style waiting is reserved for completion or blocker boundaries through
  `wait` and background daemon execution.

This document is the implementation contract and verification record for
`meight.py`. It is not a usage tutorial.

## Stack

- Python 3.13 with a repository-local `.venv/`.
- Installer is `uv`-first and must handle pipless `uv venv`, then validate `pip check`, `uv pip check`, `import openai_codex`, and `meight.py --help`.
- `openai-codex==0.1.0b3` beta SDK. Keep the version pinned.
- SDK internals: the client spawns `codex app-server --listen stdio://` and
  talks JSON-RPC over stdio. One process multiplexes multiple threads through
  `MessageRouter`.
- The SDK inherits the user's Codex config, including model, reasoning effort,
  MCP servers, and authentication. This harness exposes only `high` and
  `xhigh` worker effort; worker turns may override model and effort per
  dispatch within that range.

### Verified SDK API Surface

```python
from openai_codex import Codex, Sandbox, ApprovalMode

codex = Codex()                       # supports context-manager use
th = codex.thread_start()             # th.id = "019e..."
h = th.turn(
    input,
    *,
    cwd=str,
    sandbox=Sandbox.workspace_write,
    model=None,
    effort="high|xhigh",
    approval_mode=None,
    output_schema=None,
    service_tier=None,
)                                      # -> TurnHandle
h.steer("text")
h.interrupt()
h.stream()                            # -> Iterator[Notification]
h.run()
codex.thread_resume(thread_id)        # exists; introspect signature in code if needed
```

- `Notification` objects expose `.method` as a string and `.payload` as a
  pydantic object. Use `.model_dump()` before reading payload fields.
- `Sandbox` values: `read_only`, `workspace_write`, `full_access`.
- `ApprovalMode` values: `deny_all`, `auto_review`. `None` inherits config.
- Observed event sequence:
  `turn/started -> item/started -> item/agentMessage/delta* -> item/completed -> thread/tokenUsage/updated -> turn/completed`.
- Other important events:
  `turn/diff/updated`, `turn/plan/updated`,
  `item/commandExecution/outputDelta`, `tool/requestUserInput`,
  `item/*/requestApproval`, `thread/status/changed`, `error`.

## Deliverables

- `meight.py`: single-file implementation using only the Python standard library
  plus `openai-codex`.
- `meight`: CLI shim for invoking `meight.py`.
- Supported invocation shape: `meight <cmd>`, `.venv/bin/python meight.py <cmd>`, or `python3 meight.py <cmd>` with auto-reexec into `.venv` when `openai_codex` is absent from the caller Python.

## State Directory

The `codex2codex` skill must create a fresh temporary `$MEIGHT_HOME` for every
top-level request and reuse it for all commands in that request. This prevents
old worker status, daemon sockets, and result files from affecting a new run.
After terminal results are read, the orchestrator should shut down the isolated
daemon and remove the temp directory.

At the CLI level, if `$MEIGHT_HOME` is set, use it. Otherwise use
`<repo root>/.meight/`, where `<repo root>` is resolved from the daemon
startup cwd through `git rev-parse --show-toplevel`; if that fails, use
`<cwd>/.meight/`.

```text
$MEIGHT_HOME/
  meight.sock          # Unix domain socket
  daemon.pid
  daemon.log         # daemon lifecycle log only; do not dump raw events
  workers/<name>/
    brief.md         # original dispatched prompt
    status.json      # digest; schema below
    events.log       # append-only meaningful event lines
    result.md        # final agent message at turn completion
```

The repository `.gitignore` should ignore `.meight/`, `.meight-runs/`, and
`.venv/` for manual/debug runs; default skill runs use temp state outside the
repo unless the lead chooses a repo-local temp path.

### status.json Schema

```json
{
  "name": "worker-a",
  "thread_id": "...",
  "turn_id": "...",
  "state": "starting|running|needs_input|completed|failed|interrupted",
  "started_at": "ISO8601 KST",
  "updated_at": "ISO8601 KST",
  "cwd": "...",
  "sandbox": "workspace-write",
  "model": null,
  "effort": "high",
  "current_item": "commandExecution: pnpm typecheck:be (12s)",
  "current_item_started_at": null,
  "plan": ["[done] step1", "[active] step2"],
  "files_changed": ["src/x.ts"],
  "tokens": {"input": 0, "cached": 0, "output": 0},
  "last_message_tail": "last 500 chars of the agent message",
  "last_event_at": null,
  "last_event": null,
  "stalled": false,
  "stalled_reason": null,
  "needs_input_detail": null,
  "needs_input_source": null,
  "turns": 1
}
```

- Write `status.json` atomically with a temporary file followed by `os.replace`.
- Update status at event granularity, but throttle high-volume delta updates to
  once every two seconds.
- `needs_input_source` is the public source of truth for `needs_input`:
  `"question"` means a final `QUESTION:` blocker and makes `wait` exit `3`;
  `"tool"` means an SDK tool or approval wait and is treated as active until
  stream-end cleanup.
- `events.log` line format:
  `2026-06-12T20:01:02+09:00 [item/completed] commandExecution: pnpm typecheck:be -> exit 0`.
- Do not write delta events to `events.log`.
- Truncate each event line to at most 300 characters.

## CLI Contract

The command table must match the `python3 meight.py --help` subcommand list exactly.

| Command | Behavior |
|---|---|
| `daemon` | Run the foreground daemon. The orchestrator starts it in the background. If a live daemon already exists, return exit `1`. |
| `ping` | Check daemon health over `meight.sock` and print `pong` with the daemon pid. |
| `doctor [--json]` | Passive health report. It must not mutate state. Report `MEIGHT_HOME`, socket, pid, lock state, heartbeat age, SDK import health, Codex CLI presence, redacted proxy/env presence, worker counts, stale workers, and corrupt status files. |
| `recover [--dry-run] [--force]` | Dry-run-first stale daemon artifact cleanup. Default behavior is dry-run. `--force` must refuse live socket or held lock, snapshot recoverable metadata, then remove stale daemon artifacts only. |
| `start <name> (--brief-file F\|- \| --brief TEXT) [--cwd DIR] [--sandbox ws\|workspace_write\|workspace-write\|ro\|read_only\|read-only\|full\|full_access\|full-access] [--model M] [--effort high\|xhigh] [--fast \| --no-fast] [--no-preamble]` | Start a new worker with `thread_start` plus one turn. Defaults: `sandbox=ws`, `effort=high`, `cwd=current directory`, `model` inherited from config. `--model` and `--effort` customize the worker model and reasoning effort. `--fast`/`--no-fast` toggles the codex Fast (priority) service tier for this worker; omitted = inherit `~/.codex/config.toml`. Reject duplicate active worker names. `--brief-file -` reads the brief from stdin. |
| `dispatch <name> (--brief-file F\|- \| --brief TEXT) [--cwd DIR] [--sandbox ws\|workspace_write\|workspace-write\|ro\|read_only\|read-only\|full\|full_access\|full-access] [--model M] [--effort high\|xhigh] [--fast \| --no-fast] [--no-preamble] [--timeout SEC] [--stall-timeout SEC]` | One-shot command: auto-start daemon if needed, `start`, `wait`, then print `result.md`. Default timeout is `1800` seconds. Exit code matches `wait`. Stall timeout is a passive checkpoint and never interrupts. |
| `follow <name> (--brief-file F\|- \| --brief TEXT) [--no-preamble]` | Start a new turn on the same thread for a terminal worker or a worker waiting on a final `QUESTION:`. Reset status, increment `turns`, and append to `result.md` and `events.log` with a separator. |
| `reply <name> (--brief-file F\|- \| --brief TEXT) [--no-preamble] [--timeout SEC] [--stall-timeout SEC]` | One-shot answer path for `QUESTION:` blockers: `follow`, `wait`, then print only the latest turn result. Default timeout is `1800` seconds. Stall timeout is a passive checkpoint and never interrupts. |
| `steer <name> TEXT` | Inject mid-turn text into a running turn. Return an error unless the worker is currently running. |
| `interrupt <name>` | Interrupt the active turn. |
| `status [name] [--json]` | Does not require the daemon. Read `status.json` directly. With no name, print a one-line table for all workers: name, state, elapsed, files count, tokens, and current item. With a name, print details. `--json` prints JSON. |
| `list [--json]` | Alias for `status` with no worker name. |
| `result <name>` | Print `result.md`. |
| `wait <name> [--timeout SEC] [--stall-timeout SEC]` | Poll `status.json` once per second. Terminal states return `completed=0`, `failed=2`, `interrupted=2`. Final `QUESTION:` returns `3`. Daemon death returns `4`. Timeout or stall checkpoint returns `1`. Print one final status summary line to stdout. Stall checkpoint never interrupts. |
| `shutdown [--force]` | Refuse shutdown while active workers exist. With `--force`, interrupt all active workers and then shut down. |

## Harness Preamble and QUESTION Protocol

By default, `start`, `dispatch`, `follow`, and `reply` prepend the harness
protocol preamble to the brief. `--no-preamble` disables this.

The preamble requires workers to leave changes in the working tree and to avoid
`git commit` or `git push`. It also frames the worker as a teammate: rather than
guessing or silently complying, a worker ends its final response with a paragraph
starting with `QUESTION:` — either when blocked on information only the
orchestrator can provide, or to raise a better approach, a wrong assumption, or a
decision that could shift direction.

When a completed turn's last paragraph starts with `QUESTION:`, the daemon
promotes the worker to:

```json
{
  "state": "needs_input",
  "needs_input_source": "question",
  "needs_input_detail": "QUESTION: ..."
}
```

`wait` returns exit `3` for this state. `follow` and `reply` are allowed to
continue from this state on the same Codex thread.

## Result Artifact Contract

When a `.codex/specs/<slug>/` directory exists, workers should update or reference the requested artifact instead of inventing a separate handoff format. Implementation results list changed files, verification, risks, and next action. Review results include scope, findings, tests or verification, and a hard verdict:

```md
## Cycle 1
Scope: <scope>

### Findings
- [path:line] Risk or bug, or `None`.

### Verification
- Command and result.

### Verdict
PASS|FAIL
```

`scripts/validate_result_contract.py` validates generic worker output by default. Pass `--require-review` for review artifacts or `--require-handoff` for legacy `## Handoff Capsule` artifacts.

## Plan-to-Wave Contract

`plan.md` is the high-level orchestration input; `tasks.md` and `manifest.json` are the executable IR. `scripts/plan_to_tasks.py` must parse `### Task N:` sections from a `spec2plan` plan and compile them into codex2codex task lines.

Each executable plan task should include:

- `Worker role`: `coding|test|review|consult|sa` or a clear alias. The role contract is local to this skill in `roles/*.yaml`; `scripts/roles.py` is the loader. `devops`, `ops`, `ci`, `deploy`, and `infra` are compatibility aliases to `coding`, not first-class roles.
- `Writable scope`: exact paths the worker may write. For review/consult, this is product read scope.
- `Verification`: command or check the worker must run/report.
- `Dependencies`: task numbers or `None`.
- `Wave`: optional explicit wave number.
- `Output artifact`: path for the worker report/review.

Generated worker briefs must include the selected role YAML path, role prompt,
preferred skills, resolved context profile, and the global skill policy from
`roles/_defaults.yaml`.
`doctor --json` must report global skill directory availability and
`missing_role_skills` for all skills referenced by role YAML.

`plan_to_tasks.py` assigns waves from dependencies, moves overlapping same-wave implementation scopes later, writes `.codex/specs/<slug>/tasks.md`, creates a minimal `spec.md` source pointer when absent, and can append a review wave. `scripts/run_plan.py` wraps `plan_to_tasks.py` plus `run_wave.py`; `--dry-run` previews workers before execution.

For codex2codex waves, `scripts/prepare_wave.py` parses `tasks.md`, rejects same-wave write-scope overlap, resolves `--profile role|minimal|standard|full` to each worker's concrete `context_profile`, and writes generated briefs plus `manifest.json`. `scripts/run_wave.py` can take either `--manifest` or `--spec-dir/--wave`; it supports `--dry-run`, `--profile role|minimal|standard|full`, `--no-fix-wave`, `--auto-run-fix`, and `--max-fix-cycles`. It executes the manifest with `meight`, waits for workers, salvages complete PASS/FAIL review bodies from `result.md` when artifact writes are blocked, runs `validate_wave.py`, updates `tasks.md` and enriched `review-summary.md`, creates `Wave N: fix review findings` on review `FAIL`, optionally runs the fix wave(s) and reruns the original review until PASS or cycle limit, shuts down each isolated daemon, and returns nonzero on worker failure, blocked result, missing artifact, invalid review artifact, or review `FAIL`. A worker `completed` state is not sufficient if the expected artifact is missing or invalid.

## Daemon Internals

- One synchronous `Codex` client per daemon.
- One Python `threading.Thread` per worker to consume the SDK stream and write
  digests.
- Socket protocol: one JSON request line and one JSON response line.
  Example: `{"cmd":"start",...}` -> `{"ok":true}` or
  `{"ok":false,"error":"..."}`.
- Socket-dispatched commands: `start`, `follow`, `steer`, `interrupt`,
  `shutdown`, `ping`.
- Worker registry: `name -> {thread, handle, state}`.
- `steer` and `interrupt` operate through the stored `TurnHandle`.
- `needs_input` handling:
  - `tool/requestUserInput` or `item/*/requestApproval` records a summarized
    payload in `needs_input_detail` with `needs_input_source="tool"`.
  - A final `QUESTION:` paragraph records the question in `needs_input_detail`
    with `needs_input_source="question"`.
  - Automatic approval or tool-response handling is out of scope.
- `error` notifications or stream exceptions set the worker state to `failed`
  and write the reason to `events.log`.
- `SIGTERM` and `SIGINT` attempt to interrupt all handles, close the Codex
  client, and clean up pid/socket files.
- Agent-message deltas are accumulated in memory and finalized on
  `item/completed`.
- `result.md` is written at `turn/completed` with the last agent message.

## Beta SDK Defenses

- Always read payload fields through `model_dump()` followed by `dict.get()`
  chains. Missing fields must not crash a worker.
- Unknown events are ignored except for optional debug logging.
- SDK exceptions, including `CodexRpcError`, fail only the affected worker. The
  daemon must stay alive.
- Unknown or missing terminal turn statuses must not be silently mapped to
  `completed`; classify them as `failed` unless an interrupt was requested.

## Verification Suite

Run these checks after implementation and attach the evidence.

1. Run `doctor` against a stopped state and confirm it reports no live daemon but does report stale artifacts when present.
2. Run `recover --dry-run` against stale artifacts and confirm it reports what would be removed without mutating state.
3. Start `daemon` in the background, then confirm `ping` returns ok and `doctor` reports heartbeat / live socket health.
4. Run:
   `mkdir -p "$HOME/tmp/fleet-test" && start t1 --brief "create $HOME/tmp/fleet-test/hello.txt with content 'hi', then reply DONE" --cwd "$HOME/tmp/fleet-test" --sandbox ws`
   Then `wait t1` must exit `0`; the file must exist; `status.json`,
   `events.log`, and `result.md` must agree.
5. Steering test:
   `start t2 --brief "Count from 1 to 50 slowly, one number per line, pausing to think between each"`
   While running, send `steer t2 "Stop counting, just reply STEERED"` and
   confirm the result reflects the steer.
6. Interrupt test: interrupt a long-running task and confirm
   `state=interrupted`.
7. Stall checkpoint test: run a slow worker with `wait --stall-timeout SEC` and confirm it returns `1` without interrupting the worker.
8. Parallelism test: run two workers concurrently and confirm their
   `status.json` files update independently.
9. Follow-up test: send a follow-up instruction to completed `t1` and confirm
   the new turn uses the same `thread_id`.

## Scope-Outs

- Automatic responses to approval requests or SDK tool input requests.
- `output_schema` support.
- Automatic worktree creation. The orchestrator controls worktrees through
  `cwd`.
- Automatic daemon restart beyond the `dispatch` one-shot daemon start.
- Automatic interrupt on stall. Stall handling is passive checkpointing only.
- Multi-repository coordination inside one daemon.
