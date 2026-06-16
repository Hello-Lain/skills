---
name: codex2codex
description: Use only when the user explicitly asks for /codex2codex task delegation, worker review, worker verification, or a /codex2codex wrapper around another skill or workflow. Orchestrates Codex worker sessions through the meight CLI with supervised start/wait loops, one-shot dispatch for trivial safe tasks, bidirectional QUESTION handling, nested skill handoff, independent review, and per-worker model or reasoning options.
---

# Codex2Codex

Use the `meight` harness to run Codex workers as teammates while the current Codex session stays the lead. Keep decomposition, integration, verification, user communication, and git ownership in the lead session.

## Core Rules

- Use this skill only for explicit `/codex2codex` requests; do not silently delegate ordinary tasks.
- Treat workers as collaborators: ask for implementation, review, verification, design alternatives, or consultative pushback.
- Never let workers commit or push. Review the working tree yourself before any git operation.
- Do not accept a worker's “done” as fact. Require lead verification, runtime evidence, or independent review.
- Use `--sandbox ro` for planning, review, audit, and verification. Use workspace write access only for the worker allowed to edit.
- Use separate git worktrees via `--cwd` when workers may touch overlapping files.
- Do not ask a worker to invoke `/codex2codex` recursively. The lead owns all worker spawning.

## Resolve the CLI

Before invoking workers, resolve the command once. Prefer `meight` from `PATH`; if it is not installed, run the bundled `meight.py` from this skill directory.

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/codex2codex"
# Or resolve from the current checkout instead of hard-coding a host path.
if command -v meight >/dev/null 2>&1 && meight --help >/dev/null 2>&1; then
  MEIGHT=(meight)
elif [ -x "$SKILL_DIR/.venv/bin/python" ] && "$SKILL_DIR/.venv/bin/python" -c 'import sys' >/dev/null 2>&1; then
  MEIGHT=("$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/meight.py")
else
  MEIGHT=(python3 "$SKILL_DIR/meight.py")
fi
```

If `python3 "$SKILL_DIR/meight.py"` fails because the Codex SDK is missing, run `"$SKILL_DIR/install.sh"` or add the installed shim directory to `PATH`.
`install.sh` is `uv`-first and validates `openai_codex`; do not validate with `import codex`.

Run `meight` commands with `MEIGHT_HOME` set to the target repo's `.meight` directory, or from the target repository root. Meight stores state under `MEIGHT_HOME` when set; otherwise it uses the git root of the shell working directory. `--cwd` controls the worker's workdir only.
For unstable or stale state, prefer explicit per-task `MEIGHT_HOME`, run `meight doctor`, then run `meight recover --dry-run` before any cleanup.

## Choose a Pattern

Pick the smallest role split that gives independent evidence:

| Pattern | Use For | Roles |
|---|---|---|
| Implement + audit | Default code or documentation changes | One editor, one read-only reviewer |
| Workflow runner + loopback auditor | `/codex2codex` wrapping another skill | One phase executor, one nested-skill compliance auditor |
| Dual proposal + synthesis | Ambiguous design, architecture, writing strategy, or pipeline choices | Two read-only designers, then lead synthesis |
| Partitioned execution + cross-review | Separable modules or sections | Non-overlapping editors, then cross-review |
| Verifier-only pair | Existing high-stakes changes | Runtime verifier plus adversarial static reviewer |
| Consult | Lead is unsure before editing | One read-only worker pressure-tests the approach |

If the split is unclear and stakes are high, start with a read-only consult worker instead of guessing.

## Supervised Workflow

Use `start` + `wait` for anything substantial so the lead can observe, steer, or answer questions.
`start`, `follow`, `reply`, `steer`, and `interrupt` auto-start the daemon when the socket is absent or stale. Prefer this auto-start path over manually backgrounding `meight daemon`, because some terminal/tool runners kill background children and leave stale sockets.

```bash
REPO="$HOME/path/to/target-repo"
export MEIGHT_HOME="$REPO/.meight"
mkdir -p "$MEIGHT_HOME"
cd "$REPO"

"${MEIGHT[@]}" start <name> --brief-file - --cwd "$REPO" \
  [--sandbox ws|ro|full] [--model MODEL] [--effort low|medium|high|xhigh] <<'EOF'
<brief>
EOF

"${MEIGHT[@]}" wait <name> --timeout <seconds>
# exit: 0=completed, 1=checkpoint timeout, 2=failed/interrupted,
#       3=QUESTION/needs input, 4=daemon unavailable
```

On exit `1`, inspect once and decide:

```bash
"${MEIGHT[@]}" status <name>
"${MEIGHT[@]}" steer <name> "correction if drifting"
"${MEIGHT[@]}" wait <name> --timeout <seconds>
```

On exit `0`, read `"${MEIGHT[@]}" result <name>` and verify before accepting. On exit `3`, read the question and reply on the same thread.
On exit `1`, treat it as a checkpoint, not a failure. If status age is suspicious, use `wait --stall-timeout <seconds>` or inspect with `doctor`.
On immediate daemon errors such as `ConnectionRefusedError`, `daemon socket not found`, or `daemon-dead`, run `doctor`, then `recover --dry-run`; if `doctor` reports `socket_live: False` and `lock_state: free`, run `recover --force` and retry `start` once. Do not use shell builtins through wrappers such as `rtk proxy command -v`; wrap them in `bash -lc`.

Validate completed worker results against the brief's output contract before treating them as usable. A worker can exit `completed` after only emitting a progress note; that is an invalid result, not a successful delegation. For structured outputs, use the bundled validator:

```bash
python "$SKILL_DIR/scripts/validate_result_contract.py" \
  "$MEIGHT_HOME/workers/<name>/result.md" \
  --min-chars 1000 \
  --reject-progress-only \
  --min-heading-count 2 \
  --must-contain "## 目标" \
  --must-contain "## 验证计划"
```

Use `--reject-progress-only` for progress/status filtering. Do not use `--must-not-contain` for phrases such as "I will inspect" or "正在检查"; real artifacts may quote those phrases while explaining the gate. Reserve `--must-not-contain` for secrets, unsafe actions, or task-specific forbidden content.

If validation fails, send one targeted `follow` asking for the exact missing artifact and wait again. If the second result is still invalid, mark the worker as failed/blocked and do not silently replace it with lead-only work.

## One-Shot Dispatch

Use `dispatch` only for trivial, short, low-risk work where supervision is not useful.

```bash
REPO="$HOME/path/to/target-repo"
export MEIGHT_HOME="$REPO/.meight"
cd "$REPO"

"${MEIGHT[@]}" dispatch <name> --brief-file - --cwd "$REPO" \
  [--sandbox ws|ro|full] [--model MODEL] [--effort low|medium|high|xhigh] [--timeout 1800] <<'EOF'
<brief>
EOF
```

`dispatch` auto-starts the daemon, starts the worker, waits, and prints the result.

## Health And Recovery

- `meight doctor` is read-only. Use it before starting workers in a repo with old `.meight` state.
- `meight recover --dry-run` reports stale daemon artifacts without mutation.
- `meight recover --force` snapshots recoverable metadata then removes stale daemon artifacts; do not use it when `doctor` reports a live socket or held lock.
- `wait --stall-timeout SEC` returns a checkpoint when a running worker has not updated status for `SEC`; it never interrupts automatically.
- Prefer foreground daemon plus explicit `MEIGHT_HOME` while debugging daemon issues. Use manual foreground `meight daemon` only for diagnosis, not normal supervised workflow.

## Brief Template

Write briefs with concrete scope and evidence requirements. Include file pointers whenever possible.

```text
Role: <executor | auditor | verifier | designer | consult>
Goal: <success criteria and why it matters>
Scope: <allowed files, directories, or read-only targets>
Existing patterns: <file:line references or docs to follow>
Constraints: <domain rules, nested skill gates, sandbox limits>
Verification: <commands, checks, or evidence to collect>
Output contract: <exact artifact, verdict, or report shape>
Report: <changed files, evidence, risks, questions>
```

Role-specific additions:

- Executor: state allowed edits, required checks, and final report format.
- Auditor: include the original request, changed files/artifacts, severity scale, and `GO`/`NO-GO` verdict.
- Verifier: provide exact commands or observations to collect; forbid unrelated edits.
- Designer: ask for assumptions, tradeoffs, comparison criteria, and no implementation unless requested.
- Consult: show the lead's current thinking and ask what is missing or better.

## Nested Skill Handoff

When `/codex2codex` wraps another skill, load the nested skill in the lead session first. Workers do not inherit loaded skill context automatically, so pass the relevant rules explicitly.

```text
Nested skill: <skill-name>
Skill path: <~/ or ~/.codex relative path to SKILL.md>
Required rules: <short bullets copied or summarized by lead>
Current phase: <bounded phase only>
Do not advance past: <confirmation/checkpoint>
Output contract: <exact artifact/report expected>
```

Preserve all user-confirmation gates from the nested skill. Workers may prepare phase outputs, but the lead asks the user before advancing through required checkpoints.

## Questions and Follow-Ups

Treat worker exit `3` as a collaboration point. A `QUESTION:` may mean blocked, but it may also flag a better approach, wrong assumption, or decision that changes direction.

```bash
"${MEIGHT[@]}" reply <name> --brief "answer or decision" [--timeout 1800]
"${MEIGHT[@]}" follow <name> --brief "additional instruction"
```

Use at most two `reply` or `follow` turns per thread; then start a fresh worker with an updated brief.

## Verification Contract

- Worker edits require lead review plus targeted tests or checks when available.
- Lead edits require fresh worker review for non-trivial changes.
- `NO-GO` means fix and re-review, not stop.
- `completed` is not sufficient. Check `result.md` against the output contract; progress-only, too-short, or missing-section outputs are invalid.
- Push back on worker findings only with concrete code or runtime evidence.
- Summarize final worker roles, changed artifacts, verification evidence, unresolved risks, and any user decision needed.

## Command Notes

- `"${MEIGHT[@]}" status` shows all workers; `"${MEIGHT[@]}" status <name>` shows current item, plan, changed files, tokens, and recent message tail.
- `"${MEIGHT[@]}" doctor` reports daemon/socket/pid/heartbeat/worker health without mutation.
- `"${MEIGHT[@]}" recover --dry-run` shows stale daemon cleanup candidates.
- `"${MEIGHT[@]}" steer <name> "text"` injects a mid-turn correction when a worker is drifting.
- `"${MEIGHT[@]}" interrupt <name>` cancels a wrong or unsafe run.
- Worker artifacts live in `<repo>/.meight/workers/<name>/{brief.md,status.json,events.log,result.md}`.
- Restart the daemon after editing `meight.py`; a live daemon keeps running old code.
- Re-run the `SPEC.md` verification suite when upgrading the pinned `openai-codex` SDK.
