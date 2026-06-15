# Plan

## Goal

Create a new Codex skill, preferably `openhand/`, that integrates with `danshardware/OpenHandsMCP` as an opt-in execution backend for complex planning, large-scale tasks, and high-effort workflows.

The skill should provide conservative adaptive delegation guidance, deterministic preflight checks, task-classification helpers, OpenHandsMCP setup instructions, backend task submission guidance, status polling, cleanup, recovery, and security controls.

## Non-Goals

- Do not rebuild OpenHandsMCP session, Docker, git, or container orchestration infrastructure.
- Do not claim parity with Claude Code dynamic workflows or any unverified Codex runtime hook capability.
- Do not enable fully automatic background delegation without user approval.
- Do not pass secrets to OpenHandsMCP by default.
- Do not modify existing user files such as `headroom/SKILL.md`, `headroom/scripts/setup-headroom-codex.sh`, `AGENTS.md`, or `caveman/`.
- Do not commit, deploy, or run operational backend tasks as part of implementation unless separately approved.

## Evidence Inspected

- `.plan-grill/openhands-skill/task-packet.md`
- `.plan-grill/openhands-skill/planner-summary.md`
- `.plan-grill/openhands-skill/review-findings.md`
- OpenHandsMCP GitHub metadata from the planning packet:
- Public Python repository.
- MIT license.
- Description: `MCP Server for running openhands`.
- Default branch: `main`.
- Repository metadata observed as updated `2026-06-14` and pushed `2025-06-30`.
- OpenHandsMCP repository contents from the planning packet:
- `README.md`
- `MCP_README.md`
- `pyproject.toml`
- `run_server.py`
- `src/openhands_mcp_server/server.py`
- `src/openhands_mcp_server/session_manager.py`
- tests
- OpenHandsMCP tool surface from inspected `server.py` summary:
- `start_session`
- `code`
- `git`
- `teardown`
- `coding_task_status`
- `cleanup_coding_tasks`
- Important evidence mismatch:
- README reportedly mentions `list_sessions`.
- Inspected `server.py` summary does not show a registered `list_sessions` tool.
- OpenHandsMCP behavior from inspected `session_manager.py` summary:
- Uses Docker SDK and GitPython.
- Clones repositories into session directories.
- Runs OpenHands containers.
- Allows multiple coding task containers per session.
- Defaults `OPENHANDS_MAX_TASKS` to `3`.
- Injects `OPENHANDS_SECRET_*`.
- Mounts workspace and Docker/Podman socket.
- Defaults model configuration toward local Ollama/devstral-style settings.
- Local repository status from task packet:
- Modified existing files: `headroom/SKILL.md`, `headroom/scripts/setup-headroom-codex.sh`.
- Untracked existing files: `AGENTS.md`, `caveman/`.
- These must be treated as user/existing changes and not touched.

## Current Context

The target repository is `~/.codex/skills`.

The desired skill should live in a new skill directory, with `openhand/` preferred because it matches the requested invocation style. The skill should be explicit-first: users invoke `$openhand` or `/openhand`, and adaptive delegation remains a guided workflow rather than a guaranteed automatic runtime behavior.

OpenHandsMCP appears suitable as the backend, but it has meaningful operational risk because it can launch containers, mount workspaces, mount Docker/Podman sockets, clone repositories, and inject secrets into cloned workspaces.

Network/proxy reliability is a known implementation risk. A previous clone attempt to `https://github.com/danshardware/OpenHandsMCP.git` timed out because Git config proxy pointed to `127.0.0.1:7890`, while GitHub API access via `curl` worked.

## Assumptions

- The skill name will be `openhand` unless the user chooses a different name.
- The first implementation should be explicit invocation only.
- Any adaptive behavior should be implemented as a classifier or decision guide that outputs rationale and asks before delegating.
- OpenHandsMCP will be installed or referenced as an external dependency rather than vendored wholesale.
- Backend use requires a disposable workspace or worktree, not the live skill repository directly.
- Secrets are opt-in per key and never enabled by default.
- OpenHandsMCP upstream details from the planning packet are accurate enough for planning, but must be revalidated before implementation.
- Codex MCP configuration location and lifecycle are TBD.
- The local environment may need Docker or Podman, image pulls, model endpoint configuration, disk space checks, and proxy fixes before backend smoke tests can run.

## Proposed Approach

Build a conservative `openhand` Codex skill that wraps OpenHandsMCP through documentation, deterministic scripts, and safe operating procedures.

The implementation should have three layers:

- Skill guidance layer: `openhand/SKILL.md` defines when to use OpenHandsMCP, when not to use it, required approvals, safety gates, and cleanup obligations.
- Deterministic helper layer: scripts for preflight checks, task classification, MCP tool-surface verification, status polling, and cleanup verification.
- Reference/config layer: references documenting OpenHandsMCP setup, required environment variables, safe secret policy, task lifecycle, rollback, and troubleshooting.

The skill must avoid unsupported claims. It can say it provides an opt-in adaptive delegation workflow inspired by dynamic multi-agent workflows, but it must not claim equivalent automatic triggering, hook behavior, or feature parity.

## Step-by-Step Plan

1. Revalidate upstream OpenHandsMCP before implementation. Fetch or inspect the current upstream repository, record commit SHA, confirm license, confirm package name and entrypoint, confirm registered MCP tools from source rather than README, document whether `list_sessions` exists, and abort or revise if the observed tool surface differs materially from this plan.

2. Discover local Codex skill and MCP configuration conventions. Inspect nearby existing skills only as needed, identify whether local skills use `SKILL.md`, `agents/`, `scripts/`, `references/`, or marketplace metadata, and identify Codex MCP config path and format. If config path is unknown, produce a non-mutating example and mark live setup as TBD.

3. Create the new skill skeleton. Add `openhand/SKILL.md`, `openhand/scripts/`, and `openhand/references/`. Add `openhand/agents/openai.yaml` only if existing local skill conventions support it.

4. Define explicit invocation behavior. Document `$openhand` or `/openhand` as the safe first entrypoint, include positive and negative trigger examples, and require a user confirmation gate before starting any OpenHandsMCP-backed task.

5. Implement a dry-run task classifier. Output decision, rationale, risk level, required approvals, and proposed backend task prompt. Do not launch OpenHandsMCP from classifier mode. Include thresholds for complexity, file count, expected runtime, risk, and reversibility. Default to “do not delegate” when classification is uncertain.

6. Implement preflight checks. Verify Docker or Podman availability, socket access, disk space, network/proxy settings, model endpoint configuration, relevant `LLM_*` overrides, OpenHandsMCP package install or source checkout, repository allowlist, disposable workspace path, and that secrets are disabled unless explicitly requested.

7. Add OpenHandsMCP setup guidance. Document install options after upstream revalidation, include pinned commit or version guidance, include MCP server command example only after confirming the correct entrypoint, include a tool-surface smoke test before any coding task, and mark unverified Codex-specific config paths as TBD.

8. Add safe task lifecycle guidance. Start sessions only in disposable clones/worktrees, submit proposal-only tasks by default, poll status through `coding_task_status`, inspect generated diffs, run tests inside the session when practical, require Codex/human review before applying changes to the live workspace, and apply changes manually or through controlled patch flow only after approval.

9. Add secrets policy. Do not forward secrets by default. Require explicit per-key opt-in. Redact secret names and values in logs where appropriate. Treat `OPENHANDS_SECRET_*`, API keys, tokens, Docker auth, cookies, and repository credentials as sensitive. Document that OpenHandsMCP may write secrets to `.openhands_secrets` inside a cloned workspace. Exclude secret files from archives. Validate no secret files appear in diffs before applying delegated changes.

10. Add cleanup and rollback procedures. Call `cleanup_coding_tasks` before `teardown`, verify no OpenHands containers remain, verify disposable workspace cleanup or archive location, verify no generated changes were applied to the live workspace unless approved, and provide manual recovery instructions with destructive commands requiring explicit approval.

11. Validate the skill without backend execution first. Check metadata and trigger wording, run static checks for helper scripts, run dry-run classifier examples, verify references do not contain secrets or unsupported claims, and confirm no existing user-modified files were touched.

12. Run backend smoke test only after explicit approval. Use a disposable test repository/worktree with no secrets, verify MCP tool listing, start a session, submit a minimal proposal-only task, poll status, clean up coding tasks, teardown session, and verify no containers, workspaces, or secrets remain.

## Files / Components Likely Affected

- `openhand/SKILL.md`
- `openhand/scripts/classify-task.sh` or equivalent deterministic classifier helper
- `openhand/scripts/preflight.sh`
- `openhand/scripts/check-openhands-mcp-tools.sh`
- `openhand/scripts/cleanup-openhands.sh`
- `openhand/references/openhands-mcp-setup.md`
- `openhand/references/delegation-policy.md`
- `openhand/references/security-and-secrets.md`
- `openhand/references/task-lifecycle.md`
- `openhand/agents/openai.yaml`, optional and TBD pending local convention check
- Codex MCP config example, path TBD
- Optional marketplace metadata, TBD pending local plugin/skill convention check

The following files must not be touched unless the user separately asks:

- `headroom/SKILL.md`
- `headroom/scripts/setup-headroom-codex.sh`
- `AGENTS.md`
- `caveman/`

## Owners / Responsibilities

- Execution owner: TBD.
- Review owner: TBD.
- Validation owner: TBD.
- Rollback owner: TBD.
- Security/secrets reviewer: TBD.
- Upstream OpenHandsMCP owner: Known: `danshardware/OpenHandsMCP`, based on the repository identified in the task packet.
- Codex skill implementation owner: Inferred: the local Codex agent or user executing this plan, based on the repository path and user request. Final owner remains TBD until assigned by the user.

## Validation Plan

- Confirm upstream OpenHandsMCP commit SHA, license, package entrypoint, and registered MCP tools before coding.
- Confirm `list_sessions` status from source and avoid relying on it unless verified.
- Confirm local Codex skill conventions before adding optional folders or metadata.
- Run static checks on all new scripts.
- Run dry-run classifier scenarios:
- Small single-file edit should not delegate.
- Large multi-file refactor should recommend user-approved delegation.
- Secrets-heavy task should refuse or require explicit opt-in.
- Production/destructive task should refuse automatic delegation.
- Verify `SKILL.md` uses explicit-first language and does not claim automatic runtime hooks.
- Verify references contain no secret values.
- Verify generated files are ASCII unless existing conventions require otherwise.
- Verify no unrelated existing files changed.
- Backend smoke test, after approval only:
- Tool-surface listing succeeds.
- Minimal no-secret disposable task runs.
- Status polling works.
- Cleanup removes coding task containers.
- Teardown removes the session.
- No OpenHands containers remain.
- No `.openhands_secrets` file or secret material appears in diffs or archives.

## Rollout Plan

- Phase 1: Documentation-only skill skeleton. Add `openhand/SKILL.md` and references. No backend execution. No Codex MCP config mutation.
- Phase 2: Dry-run helpers. Add classifier and preflight scripts. Validate locally without launching OpenHandsMCP tasks.
- Phase 3: MCP setup verification. Add non-mutating config example, confirm local Codex MCP config path, and run tool-surface check only after explicit approval.
- Phase 4: Disposable backend smoke test. Use no secrets, use a disposable repository/worktree, run one harmless task, and verify cleanup.
- Phase 5: Controlled real use. Delegate only after user approval, default to proposal-only changes, and review diffs/tests before applying anything to the live workspace.

## Monitoring / Observability

- Log preflight results without secret values.
- Record OpenHandsMCP commit/version used.
- Record MCP tool surface observed during smoke test.
- Track session ID or equivalent handle if exposed by OpenHandsMCP.
- Track coding task status through `coding_task_status`.
- Track cleanup calls and results.
- Verify running containers before and after backend use.
- Verify workspace/archive paths before and after backend use.
- Verify generated diffs before applying changes.
- Monitor for silent failures:
- Task completed but no diff produced.
- Container still running after teardown.
- Cleanup missed secondary coding task containers.
- Secrets file created in cloned workspace.
- Model endpoint silently falling back to an unintended backend.
- Proxy or network failures causing partial setup.

## Rollback / Recovery Plan

- For skill file changes: revert only the new `openhand/` files created by this plan. Do not revert unrelated user-modified files. If marketplace or config metadata is added later, remove only entries introduced for `openhand`.
- For MCP/backend setup: stop new task submission immediately, run `cleanup_coding_tasks` first, run `teardown` after task cleanup, verify no OpenHands containers remain, remove or archive disposable workspaces after checking for secrets, remove non-mutating config examples if they caused confusion, and remove live MCP config only if this plan added it and the user approves.
- For delegated code changes: do not apply backend-generated changes automatically. If changes were applied, revert using a reviewed patch or VCS operation scoped only to those changes. Never run broad destructive git commands against the live workspace without explicit user approval.
- For secrets exposure: stop backend containers, remove secret files from disposable workspaces and archives, inspect diffs/logs for leaked secret values, rotate affected secrets if exposure is confirmed, record the incident, and prevent reuse of the same unsafe flow.

## Abort Criteria

Abort implementation or backend execution if any of the following occur:

- Upstream OpenHandsMCP cannot be revalidated.
- The observed OpenHandsMCP tool surface differs materially from the plan and no safe adaptation is obvious.
- Codex MCP config path or lifecycle remains unknown and live config mutation would be required.
- Docker/Podman socket access is unavailable or too risky for the environment.
- The task requires secrets but explicit per-key approval is not available.
- Proxy/network failures prevent reliable upstream install or image pulls.
- Model endpoint or image configuration is unknown.
- Disposable workspace creation fails.
- Tool-surface smoke test fails.
- Cleanup cannot verify that task containers were removed.
- Secret files appear in diffs, archives, or logs.
- The implementation would require modifying unrelated existing user files.
- The user does not approve backend execution.

## Risks

- High: Docker/Podman socket mounting can expose broad host control.
- High: Workspace mounts are write-capable and could modify files outside the intended scope if misconfigured.
- High: `OPENHANDS_SECRET_*` injection may write sensitive material to `.openhands_secrets` in a cloned workspace.
- High: OpenHandsMCP README and actual server tool surface may diverge.
- High: Multi-container task cleanup may require `cleanup_coding_tasks` before `teardown`.
- Medium: Codex MCP configuration path and lifecycle are currently TBD.
- Medium: Backend defaults may not work with the local model endpoint, image availability, proxy, or disk limits.
- Medium: Delegated changes could be low quality or unsafe if applied without review.
- Medium: Network/proxy issues may cause partial installs or stale upstream evidence.
- Low: Skill naming could be inconsistent if `openhand`, `openhands`, and `/openhand` are mixed.
- Low: Users may overestimate the automatic nature of the workflow if wording is not conservative.

## Open Questions

- TBD: Should the skill directory be named `openhand/`, `openhands/`, or another name?
- TBD: What is the correct local Codex MCP config path and supported config format?
- TBD: Should the implementation include `agents/openai.yaml`, and what local convention governs it?
- TBD: Should OpenHandsMCP be installed from a pinned commit, a package release, or a local checkout?
- TBD: Which model endpoint should OpenHandsMCP use in this environment?
- TBD: Is Docker or Podman preferred locally?
- TBD: What repository allowlist should backend sessions be allowed to access?
- TBD: Who approves backend execution?
- TBD: Who reviews security/secrets handling?
- TBD: Who owns rollback if a backend task modifies files unexpectedly?
- Unknown: Whether upstream OpenHandsMCP currently exposes additional tools beyond those listed in the planning packet.
- Unknown: Whether the current environment can pull required Docker images reliably.
- Unknown: Whether local proxy settings need to be changed before implementation.
- Unknown: Whether Codex supports any runtime hook mechanism suitable for automatic invocation in this local setup.

## Execution Decision

- Recommendation: Needs answers
- Risk Level: High
- Confidence: Medium
- Reason: The plan has a safe implementation path for an explicit, opt-in skill, but backend execution involves Docker/socket access, secrets handling, disposable workspaces, upstream API drift, and unresolved Codex MCP configuration details. Implementation can begin with documentation and dry-run helpers after user approval, but live OpenHandsMCP task execution should wait until the TBD items and preflight checks are resolved.
