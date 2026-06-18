# codex2codex

> **A two-way harness for Codex x Codex.** Not just dispatch-and-wait: Codex workers raise questions and flag better ideas mid-run, the Codex orchestrator consults them when it's stuck, and both sides review each other's work - a real collaboration loop, not one model bossing the other around. Built on the official `openai-codex` Python SDK. CLI: `meight`.

Most Codex↔Codex bridges are built for *a human watching a terminal* — tmux panes to attach to, dashboards to click. Meight is built for the agents themselves: a Codex orchestrator and Codex workers collaborating directly, with no human in the loop. In practice that means:

- **Both directions, same thread.** Codex isn't just an executor — a worker ends a turn with a `QUESTION:` to flag a better path or a shaky assumption (not only when it's blocked), and the orchestrator answers or adjusts the direction with it. Real back-and-forth, not fire-a-task-collect-a-result.
- **Consult, don't just delegate.** Stuck on a design? The orchestrator dispatches a read-only worker to think a problem through *with* it — the sibling of code review, applied to the thinking instead of the artifact.
- **Independent Codex checks the work.** Worker Codex implements -> orchestrator Codex verifies; orchestrator Codex implements -> a fresh worker Codex reviews. Fresh-thread review catches what same-thread self-review misses.
- **Supervised, on your terms.** The `start`+`wait` split lets the orchestrator pull `status` and `steer` mid-run — how often, and whether at all, is its judgment, not a fixed cadence. Progress lives in small disk files, so watching costs ~0 context.
- **One-shot when it fits.** `meight dispatch` still gives fire-and-forget for trivial, short, low-risk tasks.

```
   Codex orchestrator   ⇄   Codex worker(s)
   (what & why)               (how)
        │                          ▲
        ├──  start + brief  ───────┘
        │
        │◀──  QUESTION:  better idea · wrong assumption · blocked · done
        │──▶  answer · steer · consult · review
        │            (either side can open the next turn, same thread)
        │
        ▼   orchestrator pulls disk digests on demand — ~0 context, never streamed
   per-repo daemon ── official openai-codex SDK ── codex app-server (1 process, N threads)
        status.json · events.log · result.md
```

## Why two Codex instances, working together

Meight pairs a lead Codex session with one or more worker Codex sessions. The lead keeps direction, integration, user communication, and git; workers handle bounded implementation, review, runtime checks, and design consults. Both sides are configurable: choose the lead model/reasoning in the Codex session that loads this skill, and choose each worker's model/reasoning with `--model` and `--effort`.

The `codex2codex` skill is intentionally explicit-trigger only: use `/codex2codex ...` when you want the lead Codex to orchestrate workers. It can also wrap another skill or workflow, for example `/codex2codex complete the /mllm-structure-style workflow`. In that case the lead reads the nested skill, passes its key rules and checkpoint boundaries into worker briefs, assigns adaptive roles such as workflow runner + loopback auditor or dual proposal + synthesis, and keeps final user-facing confirmation in the lead session.

## Why this exists

As of June 2026, every public Codex↔Codex project we could find drives Codex through its **CLI** — spawning `codex exec` subprocesses or typing into tmux. Tools built that way share the same limits: to redirect a running worker you have to kill it (and lose its work), to see progress you have to pipe everything into the orchestrator's context, and a stuck worker has no way to ask for help.

OpenAI's official **`openai-codex` Python SDK** (released May 2026) removed those limits: it talks to `codex app-server` directly and exposes steering, interrupting, and streaming as real APIs, with a single Codex process running many workers at once. **Meight is — to our knowledge — the first public harness built on it.** Side by side:

| | tmux/exec bridges | MCP wrappers | **Meight** |
|---|---|---|---|
| Parallel workers | 1 process per worker | blocking tool calls | N threads, 1 codex process |
| Mid-turn steering | attach & type (human) or kill+resume (loses work) | ✗ | **`meight steer` — programmatic, no work lost** |
| Progress observation | scrape stdout / stream into context | ✗ | **disk digest, pull on demand (~0 tokens)** |
| Two-way conversation | ✗ (guesses or stalls) | ✗ | **worker raises `QUESTION:` (blocked *or* better idea) → exit 3 → `meight reply`; orchestrator can `consult` back** |
| Result delivery | scrape | tool return | **exit-code contract + result on stdout** |
| Session continuity | fragile | threadId | **same-thread `follow`/`reply` turns** |

## Quick start

Requirements: [Codex CLI](https://developers.openai.com/codex) installed & authenticated, Python >= 3.10, and `uv`.

```bash
git clone <repo-url> codex2codex
cd codex2codex && ./install.sh   # uv-managed .venv + ~/.local/bin/meight
```

`install.sh` uses `uv`, allows prerelease resolution for the pinned beta SDK, ensures pip when `uv venv` creates a pipless environment, and validates `openai_codex` import plus `pip check`/`uv pip check`. In proxy/mirror environments, pass the environment explicitly, for example:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple \
HTTP_PROXY=http://127.0.0.1:7890 HTTPS_PROXY=http://127.0.0.1:7890 \
ALL_PROXY=socks5://127.0.0.1:7890 ./install.sh
```

If `meight` is not on `PATH`, invoke the bundled script directly from this directory. `python3 ./meight.py ...` auto-reexecs into `./.venv/bin/python` when `openai_codex` is only installed in the skill venv:

```bash
python3 ./meight.py --help
```

For substantial work, use supervised dispatch. The Codex skill uses a fresh `MEIGHT_HOME` per request so old workers never bleed into a new run. Bare CLI use without `MEIGHT_HOME` still falls back to per-repo `.meight/`.

```bash
RUN_HOME="$(mktemp -d "${TMPDIR:-/tmp}/meight-${PWD##*/}-XXXXXX")"
```

For codex-agent-team specs, generate worker briefs from `tasks.md` first:

```bash
python scripts/prepare_wave.py --spec-dir .codex/specs/<slug> --wave "Wave 1"
```

The generated manifest rejects overlapping write scopes. Review workers use workspace-write so they can create `review*.md`, but their product file scope remains read-only by instruction.

Run the wave end-to-end:

```bash
python scripts/run_wave.py --spec-dir .codex/specs/<slug> --wave "Wave 1"
```

On success this validates the wave, marks matching `tasks.md` items complete, and writes `review-summary.md` for review waves. Use `--manifest` to run a previously generated manifest.

Useful controls:

```bash
python scripts/run_wave.py --spec-dir .codex/specs/<slug> --wave "Wave 1" --dry-run
python scripts/run_wave.py --spec-dir .codex/specs/<slug> --wave "Wave 1" --profile full
python scripts/run_wave.py --spec-dir .codex/specs/<slug> --wave "Wave 1" --no-fix-wave
python scripts/run_wave.py --spec-dir .codex/specs/<slug> --wave "Wave 2: review" --auto-run-fix --max-fix-cycles 2
```

Default profile is `minimal`: generated briefs tell workers to read only the spec, task, listed files, and directly related tests. On review `FAIL`, `run_wave.py` appends the next `Wave N: fix review findings` task unless `--no-fix-wave` is set. With `--auto-run-fix`, it runs generated fix wave(s), then reruns the original review until PASS or `--max-fix-cycles` is reached.

Reuse that same path for every command in the request:

```bash
MEIGHT_HOME="$RUN_HOME" meight start impl-1 --brief-file - --cwd ~/my-repo <<'EOF'
Implement X in src/foo.py. Existing pattern: see src/bar.py:42.
Verify with: pytest tests/test_foo.py. Report changed files + test output.
EOF

MEIGHT_HOME="$RUN_HOME" meight wait impl-1 --timeout 300
# exit 0=completed · 2=failed/interrupted · 3=worker asked a question · 4=daemon dead · 1=checkpoint timeout
```

After reading terminal results, stop the isolated daemon and remove its temp state:

```bash
MEIGHT_HOME="$RUN_HOME" meight shutdown || true
rm -rf -- "$RUN_HOME"
```

When debugging or hardening daemon issues, keep the temp `MEIGHT_HOME` and run a foreground daemon.

On exit `1`, the worker is still running. Inspect once, then either wait again or steer:

```bash
MEIGHT_HOME="$RUN_HOME" meight status impl-1
MEIGHT_HOME="$RUN_HOME" meight steer impl-1 "Stop refactoring the helper — only fix the bug."
MEIGHT_HOME="$RUN_HOME" meight wait impl-1 --timeout 300
```

If status has not updated for too long, use a passive stall checkpoint:

```bash
MEIGHT_HOME="$RUN_HOME" meight wait impl-1 --timeout 300 --stall-timeout 600
```

On exit `0`, `2`, or `3`, `wait` prints a status summary. Read the full message from disk:

```bash
MEIGHT_HOME="$RUN_HOME" meight result impl-1
```

New worker reports should update or reference the relevant `.codex/specs/<slug>/` artifact when one exists. Implementation reports should list changed files, verification, risks, and next action. Review reports should include findings, tests/verification, and a hard verdict:

```md
## Cycle 1
Scope: parser

### Findings
- [path:line] Risk or bug, or `None`.

### Verification
- Command and result.

### Verdict
PASS
```

Validate generic result artifacts with `python scripts/validate_result_contract.py "$RUN_HOME/workers/<name>/result.md"`. Add `--require-review` for review outputs, or `--require-handoff` only for legacy Handoff Capsule results. Generated review summaries include each review worker's verdict, critical finding count, verification excerpt, and artifact path. After a generated wave, validate the whole wave before accepting completion:

```bash
python scripts/validate_wave.py --manifest .codex/specs/<slug>/generated/<wave>/manifest.json --meight-home "$RUN_HOME"
```

The worker asked a question (exit 3)? The question is also visible in `meight status impl-1` as `needs_input_detail`. Answer in one shot, same thread:

```bash
MEIGHT_HOME="$RUN_HOME" meight reply impl-1 --brief "Use config-a.json, and keep the legacy field."
```

You're the one who's stuck? Run the loop the other way — dispatch a read-only worker to think a problem through *with* you, then `follow` to refine the direction together:

```bash
MEIGHT_HOME="$RUN_HOME" meight start consult-1 --sandbox ro --brief "My plan is X but I'm unsure about Y. Read src/ and tell me what I'm missing — and a better approach if you see one."
MEIGHT_HOME="$RUN_HOME" meight wait consult-1 --timeout 300
MEIGHT_HOME="$RUN_HOME" meight follow consult-1 --brief "Good point on Y. If we go that way, how does Z hold up?"
```

For trivial, short, low-risk tasks, one-shot dispatch is still available:

```bash
MEIGHT_HOME="$RUN_HOME" meight dispatch tiny-1 --brief "Check whether README mentions LICENSE." --sandbox ro
```

## Using it from Codex

This is the intended consumer. For real work, run `wait --timeout` as the **background Bash call**. Codex wakes at the checkpoint, reads one `status`, and either waits again or sends a targeted `steer`:

```
Bash(command: "MEIGHT_HOME=\"$RUN_HOME\" meight start review-1 --sandbox ws --effort high --brief-file - <<'EOF' ... EOF")
Bash(command: "MEIGHT_HOME=\"$RUN_HOME\" meight wait review-1 --timeout 300",
     run_in_background: true)
-> ... Codex keeps working ...
→ <task-notification> exit 1 checkpoint timeout
→ MEIGHT_HOME="$RUN_HOME" meight status review-1
→ healthy: wait again · drifting: MEIGHT_HOME="$RUN_HOME" meight steer review-1 "..."
```

Use `--sandbox ro` for pure consult/review reports that do not write artifacts. Use `--sandbox ws` when the worker must create `review*.md`; restrict product files in the brief.

When the worker reaches a terminal state, the notification is `0` (completed), `2` (failed/interrupted), or `3` (worker question). Use `MEIGHT_HOME="$RUN_HOME" meight result review-1` for the full report. On `0`, verify the work before accepting it. On `3`, answer with `MEIGHT_HOME="$RUN_HOME" meight reply`.

Every brief is automatically prefixed with a harness preamble that (a) forbids `git commit`/`push` — git stays owned by the orchestrator — and (b) frames the worker as a teammate: rather than guessing or silently complying, end with a `QUESTION:` paragraph when blocked *or* to flag a better approach, a wrong assumption, or a decision that could shift direction. Disable with `--no-preamble`.

A drop-in orchestrator prompt (role split, routing table, dispatch protocol, independent-review rules) ships as [`CODEX.md`](./CODEX.md), but it is optional. The self-contained Codex **skill** lives at the repository root in [`SKILL.md`](./SKILL.md) and should trigger only when the user explicitly requests `/codex2codex`.

## What "easy for an agent" actually means

Small decisions everywhere assume the user is an LLM agent, not a person at a terminal:

- **Exit codes are the API.** `0` done, `2` failed, `3` question, `4` daemon gone. The agent branches on a number instead of reading prose and guessing whether things worked. Unknown outcomes map to *failed*, never to *completed* — exit 0 can be trusted.
- **Sparse checkpoints, not busy polling.** Set `wait --timeout` near the work's expected duration: finish in time and the orchestrator just gets the completion push; overrun and the timeout wakes it for one `status` look. A timeout returns exit `1` and leaves the worker running. No fixed interval, no obligation to check — `status` and `steer` stay available without tight polling loops that burn turns.
- **Names, not session IDs.** Workers are addressed as `review-1`, follow-ups included. No UUID bookkeeping to get wrong.
- **Results survive on disk.** `result.md` stays re-readable — if the agent's context gets compacted mid-session, nothing is lost.
- **Status is pre-digested.** Instead of raw logs, `status` returns what a decision needs: what the worker is doing now, which files changed, its last thought. Exactly enough to choose between wait, steer, and interrupt.
- **Policy can't be forgotten.** The no-commit rule and the QUESTION protocol are injected into every brief by the harness, not remembered by the agent.
- **Briefs go through stdin.** Long multi-line briefs avoid shell-quoting traps entirely.

## Command reference

| Command | What it does |
|---|---|
| `meight doctor [--json]` | Passive health report for state dir, socket, pid, heartbeat, SDK import, proxy presence, and workers. |
| `meight recover --dry-run \| --force` | Dry-run-first stale daemon artifact cleanup. `--force` snapshots metadata before removing stale artifacts. |
| `meight start <name> [opts]` | Start a worker and return immediately with the thread id. Supervised workflow entry point. |
| `meight wait <name> --timeout SEC [--stall-timeout SEC]` | Checkpoint wait: return on terminal state, QUESTION, daemon death, timeout, or passive stall checkpoint. Timeout leaves the worker running. |
| `meight dispatch <name> [opts]` | One-shot: auto-start daemon → start worker → wait → print result. Use for trivial, short, low-risk work. |
| `meight reply <name> --brief ...` | One-shot answer to a worker question: follow + wait + print last-turn result |
| `meight status [name]` | Pull digest (table or detail). Reads disk — works without the daemon |
| `meight steer <name> "text"` | Inject instruction into the running turn (no work lost) |
| `meight interrupt <name>` | Cancel the running turn (idempotent) |
| `meight follow <name> --brief ...` | Low-level: new turn on the same thread (context preserved) |
| `meight result / list / daemon / ping / shutdown` | Low-level support commands |

Options: `--cwd` (worker workdir - use separate git worktrees for overlapping file scopes), `--sandbox ws|ro|full` (default `ws` = workspace-write; reviews run `ro`), `--model MODEL` (worker model; omit to inherit `~/.codex/config.toml`), `--effort low|medium|high|xhigh` (worker reasoning effort; default `medium`), `--fast`/`--no-fast` (per-worker toggle for Codex Fast/priority tier; omit to inherit config), `--timeout`.

Worker state lives in `$MEIGHT_HOME/workers/<name>/`: `brief.md`, `status.json` (state machine + tokens + files changed + last activity), `events.log` (one line per meaningful event), `result.md` (final message per turn). Without `MEIGHT_HOME`, the CLI uses `<repo>/.meight/`; add `.meight/` to your global gitignore.

## Good to know

- Meight inherits your `~/.codex/config.toml` as-is (model, reasoning effort, MCP servers, auth). If `codex` works in your terminal, `meight` works. Per-worker overrides (`--model`, `--effort`, `--fast`/`--no-fast`) take precedence for that worker.
- `doctor` is read-only. Use `recover --dry-run` before `recover --force`; do not force recovery while a live socket or held lock is reported.
- `openai-codex` is pinned (`0.1.0b3`, beta). When bumping, re-run the verification suite in [`SPEC.md`](./SPEC.md).
- Design details — the concurrency model, state machine, and orchestration policy — live in [`ARCHITECTURE.md`](./ARCHITECTURE.md).

## License

MIT
