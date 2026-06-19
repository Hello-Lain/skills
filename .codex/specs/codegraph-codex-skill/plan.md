# CodeGraph Codex 集成与专用 Skill 计划

Mode: light
Risk level: Medium
Confidence: High

## Goal

把 `https://github.com/colbymchenry/codegraph` 配置进本机 Codex，并新增一个专用 skill，使后续 agent 在阅读大型/陌生代码库时优先使用 CodeGraph 的索引、符号、调用链、影响面、受影响测试能力，减少盲目 `rg`/全文件读取。

## Non-Goals

- 不在本计划阶段修改 `/data/lcq/.codex/config.toml`。
- 不在本计划阶段创建真实 `skills/codegraph-project-reader/`。
- 不替换现有 `lean_ctx`、`headroom`、`serena` MCP；CodeGraph 作为补充。
- 不把任意项目源码上传外部服务；CodeGraph 本地索引为默认前提。

## Evidence Inspected

- User request: 配置 `https://github.com/colbymchenry/codegraph` 到 Codex，设置专门 skill，提高 agent 阅读项目代码效率，用 `spec2plan` 产计划。
- URL inspected: `https://github.com/colbymchenry/codegraph`
- Local CLI probe: `npx --yes @colbymchenry/codegraph version` -> `1.0.1`
- Local CLI probe: `npx --yes @colbymchenry/codegraph install --print-config codex`
- Local CLI probe: `npx --yes @colbymchenry/codegraph --help`
- Local CLI probe: `npx --yes @colbymchenry/codegraph explore --help`
- Local CLI probe: `npx --yes @colbymchenry/codegraph node --help`
- Local CLI probe: `npx --yes @colbymchenry/codegraph affected --help`
- Local config: `/data/lcq/.codex/config.toml` has MCP servers `lean_ctx`, `headroom`, disabled `serena`; no `codegraph`.
- Local status: `/data/lcq/.codex/skills` already has unrelated modified/untracked files; preserve them.
- Skill rules inspected: `/data/lcq/.codex/skills/spec2plan/SKILL.md`
- Plan contract inspected: `/data/lcq/.codex/skills/spec2plan/references/plan-contract.md`
- Skill creation rules inspected: `/data/lcq/.codex/skills/.system/skill-creator/SKILL.md`
- Skill metadata rules inspected: `/data/lcq/.codex/skills/.system/skill-creator/references/openai_yaml.md`
- Skill compression rules inspected: `/data/lcq/.codex/skills/skill-tokenless/SKILL.md`
- Patch/editing rules inspected: `/data/lcq/.codex/skills/apply-patch/SKILL.md`
- Git hygiene rules inspected: `/data/lcq/.codex/skills/git-workflow-and-versioning/SKILL.md`

## Spec Summary

Need an implementation plan that:

- Installs or makes available the CodeGraph CLI command used by MCP.
- Adds CodeGraph as a Codex MCP stdio server.
- Creates a dedicated Codex skill that teaches future agents when and how to use CodeGraph.
- Biases the agent toward symbol/call graph/impact exploration before broad file reads.
- Validates CLI, config, skill schema, and at least one smoke workflow.

## Domain Language Check

- `CodeGraph`: the external project/package `@colbymchenry/codegraph`.
- `Codex config`: `/data/lcq/.codex/config.toml`.
- `Codex home`: `/data/lcq/.codex`.
- `MCP server`: CodeGraph launched by Codex via stdio using `codegraph serve --mcp`.
- `skill`: folder under `/data/lcq/.codex/skills/<skill-name>/` with `SKILL.md` and optional `agents/`, `references/`, `scripts/`.
- `agent reading efficiency`: fewer full-file reads, earlier symbol map, targeted source snippets, dependency/impact/test selection.

No term conflict found. `CodeGraph` is distinct from existing `lean_ctx` graph tools; plan treats them as complementary.

## Current Context

- `codegraph` is not currently on PATH (`which codegraph` returned no path).
- `npx --yes @colbymchenry/codegraph` works and reports version `1.0.1`.
- `codegraph install --print-config codex` recommends:

```toml
[mcp_servers.codegraph]
command = "codegraph"
args = ["serve", "--mcp"]
```

- Current Codex MCP config already includes:
  - `[mcp_servers.lean_ctx]`
  - `[mcp_servers.headroom]`
  - `[mcp_servers.serena]` with `enabled = false`
- Current working tree has unrelated dirty files; implementation must avoid reverting or staging them.
- Current Codex session will likely need restart/new session to expose newly added MCP tools.

## Assumptions

- Default install mode: global npm package, so `command = "codegraph"` works reliably for Codex MCP.
- Fallback install mode: if global npm install is undesirable/fails, configure MCP with `command = "npx"` and args equivalent to `--yes @colbymchenry/codegraph serve --mcp`.
- Skill name: `codegraph-project-reader`.
- Implementation root: `/data/lcq/.codex`.
- Skill path: `/data/lcq/.codex/skills/codegraph-project-reader`.
- Plan artifact path: `/data/lcq/.codex/skills/.codex/specs/codegraph-codex-skill/plan.md`.
- No secrets need to be read or written.

## User Inputs Needed

None for the default path.

Optional preference before execution:

- Use global install: `npm install -g @colbymchenry/codegraph`
- Or use no-global fallback: MCP launches CodeGraph through `npx --yes @colbymchenry/codegraph`

## Proposed Approach

1. Preserve state: inspect dirty tree and copy the current Codex config before editing.
2. Install/verify CodeGraph CLI.
3. Add `[mcp_servers.codegraph]` to `/data/lcq/.codex/config.toml`.
4. Create `codegraph-project-reader` via `skill-creator` initializer with `references` and `scripts`.
5. Implement a lean `SKILL.md` that enforces CodeGraph-first project-reading heuristics:
   - For unknown repo areas, run `codegraph status` then `sync`/`init` as needed.
   - Use `explore` for task-area discovery.
   - Use `node` for focused source + caller/callee context.
   - Use `callers`, `callees`, `impact` for edit blast radius.
   - Use `affected` for changed-file test targeting.
   - Fall back to `rg`, `rtk read`, `ctx_*`, or normal file reads when CodeGraph is unavailable or stale.
6. Add reference recipes for common tasks and MCP/CLI fallback behavior.
7. Add a small script to ensure a project has a fresh CodeGraph index.
8. Run skill validation, CLI smoke checks, and diff inspection.

## Scenario Probes

- New unfamiliar repo: agent runs `codegraph init <repo>` or `sync`, then `explore "auth flow"` before opening broad files.
- Bug fix in known symbol: agent runs `node <symbol>`, `callers <symbol>`, `impact <symbol>`, then reads only relevant files.
- Refactor risk check: agent runs `impact <symbol>` plus `affected <changed-files> --json`.
- MCP unavailable: skill instructs CLI fallback via `codegraph ...`; if CLI unavailable, fallback to `rg`/`ctx_*` and report degraded mode.
- Stale index: skill checks `status`/`sync` before trusting results.

## Dependency Graph

```text
Task 1 state/config audit
  -> Task 2 install CodeGraph CLI
    -> Task 3 add Codex MCP config
      -> Task 6 integration smoke

Task 1 state/config audit
  -> Task 4 scaffold skill
    -> Task 5 implement skill resources
      -> Task 7 skill validation/tokenless pass
        -> Task 8 final review

Task 3 + Task 5
  -> Task 6 integration smoke
```

## Task Breakdown

### Task 1: State and config audit

- Description: Capture dirty tree, current Codex MCP config, existing skill namespace, and expected rollback files before edits.
- Worker role: devops
- Wave: 1
- Acceptance criteria:
  - Existing unrelated changes identified.
  - No unrelated file is modified.
  - Config backup path selected.
- Verification: `git -C /data/lcq/.codex/skills status --short`; `grep -n "mcp_servers" /data/lcq/.codex/config.toml`
- Dependencies: None
- Files likely touched: None
- Writable scope: `.codex/specs/codegraph-codex-skill/artifacts/task-1-audit.md`
- Output artifact: `.codex/specs/codegraph-codex-skill/artifacts/task-1-audit.md`
- Estimated scope: XS

### Task 2: Install CodeGraph CLI

- Description: Make `codegraph` available on PATH or decide no-global `npx` fallback.
- Worker role: devops
- Wave: 2
- Acceptance criteria:
  - `codegraph version` works, or fallback command is documented.
  - Installed version is recorded.
  - No project files are modified.
- Verification: `codegraph version` or `npx --yes @colbymchenry/codegraph version`
- Dependencies: Task 1
- Files likely touched: Global npm prefix outside repo, if global install selected
- Writable scope: `.codex/specs/codegraph-codex-skill/artifacts/task-2-install.md`
- Output artifact: `.codex/specs/codegraph-codex-skill/artifacts/task-2-install.md`
- Estimated scope: S

### Task 3: Add Codex MCP config

- Description: Add CodeGraph MCP server block to `/data/lcq/.codex/config.toml`.
- Worker role: devops
- Wave: 3
- Acceptance criteria:
  - Config contains exactly one `[mcp_servers.codegraph]` block.
  - Command resolves to the selected install mode.
  - Existing MCP blocks remain unchanged.
- Verification: `grep -n "\\[mcp_servers.codegraph\\]" /data/lcq/.codex/config.toml`; `codegraph serve --help`
- Dependencies: Task 2
- Files likely touched: `/data/lcq/.codex/config.toml`
- Writable scope: `config.toml`
- Output artifact: `.codex/specs/codegraph-codex-skill/artifacts/task-3-mcp-config.md`
- Estimated scope: XS

### Task 4: Scaffold `codegraph-project-reader` skill

- Description: Use `init_skill.py` to create the skill folder with `references` and `scripts`, plus `agents/openai.yaml`.
- Worker role: coding
- Wave: 2
- Acceptance criteria:
  - Skill folder exists at `/data/lcq/.codex/skills/codegraph-project-reader`.
  - `SKILL.md` frontmatter has valid name/description.
  - `agents/openai.yaml` exists and mentions `$codegraph-project-reader`.
- Verification: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/codegraph-project-reader`
- Dependencies: Task 1
- Files likely touched:
  - `/data/lcq/.codex/skills/codegraph-project-reader/SKILL.md`
  - `/data/lcq/.codex/skills/codegraph-project-reader/agents/openai.yaml`
  - `/data/lcq/.codex/skills/codegraph-project-reader/references/`
  - `/data/lcq/.codex/skills/codegraph-project-reader/scripts/`
- Writable scope: `skills/codegraph-project-reader/**`
- Output artifact: `.codex/specs/codegraph-codex-skill/artifacts/task-4-scaffold.md`
- Estimated scope: S

### Task 5: Implement CodeGraph reading workflow resources

- Description: Replace placeholders with a concise skill entrypoint, detailed recipe reference, integration reference, and an `ensure-codegraph-index.sh` helper script.
- Worker role: coding
- Wave: 3
- Acceptance criteria:
  - `SKILL.md` stays lean and routes detail to references.
  - Skill requires status/init/sync before trusting CodeGraph in a repo.
  - Skill defines MCP-first and CLI fallback behavior.
  - Skill defines when to use `explore`, `node`, `callers`, `callees`, `impact`, `affected`, `files`.
  - Script is executable or has exact invocation docs.
- Verification:
  - `grep -R "explore\\|node\\|impact\\|affected\\|fallback" /data/lcq/.codex/skills/codegraph-project-reader`
  - `bash /data/lcq/.codex/skills/codegraph-project-reader/scripts/ensure-codegraph-index.sh --help`
- Dependencies: Task 4
- Files likely touched:
  - `/data/lcq/.codex/skills/codegraph-project-reader/SKILL.md`
  - `/data/lcq/.codex/skills/codegraph-project-reader/references/query-recipes.md`
  - `/data/lcq/.codex/skills/codegraph-project-reader/references/codex-integration.md`
  - `/data/lcq/.codex/skills/codegraph-project-reader/scripts/ensure-codegraph-index.sh`
- Writable scope: `skills/codegraph-project-reader/**`
- Output artifact: `.codex/specs/codegraph-codex-skill/artifacts/task-5-resources.md`
- Estimated scope: M

### Task 6: Integration smoke checks

- Description: Validate CLI/MCP-facing commands against a small local repo path and record restart requirement.
- Worker role: devops
- Wave: 4
- Acceptance criteria:
  - `codegraph status -p <path>` or fallback command produces expected status.
  - `codegraph files -p <path>` works after init/index if needed.
  - `codegraph explore -p <path> "<query>" --max-files 3` works or degradation is documented.
  - Codex restart/new session requirement is stated.
- Verification:
  - `codegraph status -p /data/lcq/.codex/skills`
  - `codegraph explore -p /data/lcq/.codex/skills "skill validation workflow" --max-files 3`
- Dependencies: Task 3, Task 5
- Files likely touched: `.codegraph/` under smoke target if indexing `/data/lcq/.codex/skills`
- Writable scope: `.codegraph/**`
- Output artifact: `.codex/specs/codegraph-codex-skill/artifacts/task-6-smoke.md`
- Estimated scope: S

### Task 7: Skill tokenless and validation pass

- Description: Apply `skill-tokenless` review, validate skill schema, inspect counts/diff, preserve gates.
- Worker role: review
- Wave: 5
- Acceptance criteria:
  - `quick_validate.py` passes.
  - `SKILL.md` is concise; long detail lives in one-level references.
  - Required gates remain: stale index check, fallback path, no blind broad reads, no secret handling.
  - Diff has no unrelated changes.
- Verification:
  - `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/codegraph-project-reader`
  - `wc -l /data/lcq/.codex/skills/codegraph-project-reader/SKILL.md /data/lcq/.codex/skills/codegraph-project-reader/agents/openai.yaml`
  - `grep -R "status\\|sync\\|fallback\\|secrets" /data/lcq/.codex/skills/codegraph-project-reader`
- Dependencies: Task 5
- Files likely touched: `/data/lcq/.codex/skills/codegraph-project-reader/**`
- Writable scope: `skills/codegraph-project-reader/**`
- Output artifact: `.codex/specs/codegraph-codex-skill/artifacts/task-7-validation.md`
- Estimated scope: S

### Task 8: Final review and handoff

- Description: Review final diff, summarize commands, rollback, and how to use the new skill.
- Worker role: review
- Wave: 6
- Acceptance criteria:
  - Final response includes changed files, validation status, restart note, and rollback commands.
  - No unrelated dirty files are reverted or included.
  - User knows how to invoke `$codegraph-project-reader`.
- Verification: `git -C /data/lcq/.codex/skills diff --stat`; targeted `git diff` for touched skill files; `grep -n "\\[mcp_servers.codegraph\\]" /data/lcq/.codex/config.toml`
- Dependencies: Task 6, Task 7
- Files likely touched: None
- Writable scope: `.codex/specs/codegraph-codex-skill/artifacts/task-8-review.md`
- Output artifact: `.codex/specs/codegraph-codex-skill/artifacts/task-8-review.md`
- Estimated scope: S

## Step-by-Step Plan

1. Run audit commands and save `.codex/specs/codegraph-codex-skill/artifacts/task-1-audit.md`.
2. Install CodeGraph globally:

```bash
npm install -g @colbymchenry/codegraph
codegraph version
```

3. If global install fails, use fallback config:

```toml
[mcp_servers.codegraph]
command = "npx"
args = ["--yes", "@colbymchenry/codegraph", "serve", "--mcp"]
```

4. Otherwise add recommended config:

```toml
[mcp_servers.codegraph]
command = "codegraph"
args = ["serve", "--mcp"]
```

5. Scaffold skill:

```bash
python /data/lcq/.codex/skills/.system/skill-creator/scripts/init_skill.py codegraph-project-reader --path /data/lcq/.codex/skills --resources scripts,references --interface display_name="CodeGraph Project Reader" --interface short_description="Use CodeGraph to read codebases faster." --interface default_prompt="Use $codegraph-project-reader to map this codebase with CodeGraph before broad file reads."
```

6. Replace placeholders with final skill content.
7. Add references:
   - `references/query-recipes.md`
   - `references/codex-integration.md`
8. Add helper:
   - `scripts/ensure-codegraph-index.sh`
9. Run validation:

```bash
python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/codegraph-project-reader
bash /data/lcq/.codex/skills/codegraph-project-reader/scripts/ensure-codegraph-index.sh --help
```

10. Run smoke:

```bash
codegraph status -p /data/lcq/.codex/skills
codegraph explore -p /data/lcq/.codex/skills "skill validation workflow" --max-files 3
```

11. Start a new Codex session to load the `codegraph` MCP server.

## Parallelization

- Wave 1: Task 1 only. It establishes state and avoids dirty-tree collisions.
- Wave 2: Task 2 and Task 4 can run in parallel. CLI install touches global npm; skill scaffold touches only `skills/codegraph-project-reader/**`.
- Wave 3: Task 3 and Task 5 can run in parallel after their dependencies. Config and skill resources are disjoint.
- Wave 4: Task 6 waits for both config and skill resources.
- Wave 5: Task 7 waits for skill resources.
- Wave 6: Task 8 waits for smoke and validation.

No same-wave implementation tasks share writable paths.

## Files / Components Likely Affected

- `/data/lcq/.codex/config.toml`
- `/data/lcq/.codex/skills/codegraph-project-reader/SKILL.md`
- `/data/lcq/.codex/skills/codegraph-project-reader/agents/openai.yaml`
- `/data/lcq/.codex/skills/codegraph-project-reader/references/query-recipes.md`
- `/data/lcq/.codex/skills/codegraph-project-reader/references/codex-integration.md`
- `/data/lcq/.codex/skills/codegraph-project-reader/scripts/ensure-codegraph-index.sh`
- Optional smoke index: `/data/lcq/.codex/skills/.codegraph/**`
- Plan artifacts: `/data/lcq/.codex/skills/.codex/specs/codegraph-codex-skill/**`

## Owners / Responsibilities

- Main agent: execute config edits, skill creation, validation, smoke checks, final handoff.
- Review role: inspect skill clarity, token efficiency, and diff isolation.
- User: only needed if they prefer no global npm install.

## Validation Plan

- Config validation:
  - `grep -n "\\[mcp_servers.codegraph\\]" /data/lcq/.codex/config.toml`
  - `codegraph serve --help`
- CLI validation:
  - `codegraph version`
  - `codegraph status -p /data/lcq/.codex/skills`
- Skill validation:
  - `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/codegraph-project-reader`
  - `bash /data/lcq/.codex/skills/codegraph-project-reader/scripts/ensure-codegraph-index.sh --help`
- Smoke validation:
  - `codegraph explore -p /data/lcq/.codex/skills "skill validation workflow" --max-files 3`
  - If current Codex cannot see MCP tools immediately, start a new Codex session and verify tool exposure there.
- Diff validation:
  - `git -C /data/lcq/.codex/skills status --short`
  - `git -C /data/lcq/.codex/skills diff -- /data/lcq/.codex/skills/codegraph-project-reader`

## Rollout Plan

1. Local-only rollout in `/data/lcq/.codex`.
2. New skill becomes auto-discoverable in future Codex sessions.
3. New MCP server becomes available after Codex restart/new session.
4. First real repo use should run `codegraph init <repo>` or `codegraph sync <repo>`.
5. If smoke indexing `/data/lcq/.codex/skills` creates unwanted `.codegraph/`, remove it after validation unless user wants it retained.

## Monitoring / Observability

- Use `codegraph status -p <repo>` to detect stale/missing index.
- Use `codegraph daemon`/`daemons` if background daemon issues appear.
- Use Codex startup logs if MCP server fails to launch.
- Skill should require agents to report degraded mode when CodeGraph is missing/stale.
- Compare future sessions by reduced broad `read` usage and more targeted `explore`/`node`/`impact` usage.

## Documentation / ADR Updates

ADR: Not needed.

Rationale: local tool/skill integration, reversible config addition, no durable project architecture decision.

Docs to create/update:

- `skills/codegraph-project-reader/SKILL.md`
- `skills/codegraph-project-reader/references/query-recipes.md`
- `skills/codegraph-project-reader/references/codex-integration.md`
- Optional final artifact `.codex/specs/codegraph-codex-skill/artifacts/task-8-review.md`

## Rollback / Recovery Plan

- Remove the CodeGraph MCP block from `/data/lcq/.codex/config.toml`.
- Remove `/data/lcq/.codex/skills/codegraph-project-reader/`.
- If globally installed and no longer wanted:

```bash
npm uninstall -g @colbymchenry/codegraph
```

- If smoke index is unwanted:

```bash
rm -rf /data/lcq/.codex/skills/.codegraph
```

- Do not revert unrelated dirty files in `/data/lcq/.codex/skills`.

## Abort Criteria

- `codegraph` package cannot run via either global install or `npx`.
- `config.toml` contains unexpected structure that would make safe insertion ambiguous.
- Skill validation fails after one repair attempt.
- Smoke indexing writes unexpected large/unwanted artifacts outside `.codegraph/`.
- Any step requires secrets, auth tokens, or irreversible external system changes.

## Risks

- New MCP server may not be visible until Codex restarts.
- Global npm install changes user environment outside the repo.
- `npx` fallback adds startup latency and network dependency.
- CodeGraph index may become stale if agents skip `sync`.
- Existing `lean_ctx` tools overlap conceptually; skill must define routing to avoid duplicated context work.
- Current worktree is dirty; implementation must avoid unrelated changes.

## Open Questions

- Should implementation use global npm install or no-global `npx` MCP launch? Default plan uses global install because upstream Codex snippet expects `command = "codegraph"`.
- Should the smoke `.codegraph/` index for `/data/lcq/.codex/skills` be retained for future skill-dev work or deleted after validation?

## Execution Decision

Plan only. Implementation not executed in this `spec2plan` pass.

Ready to execute after user confirms or asks to proceed.

## Execution Handoff

- Goal: Configure CodeGraph for Codex and add `codegraph-project-reader` skill to improve codebase-reading efficiency.
- Current state: Plan generated; no real config/skill implementation performed. CodeGraph works via `npx`; `codegraph` is not on PATH. Existing `/data/lcq/.codex/config.toml` has no CodeGraph MCP block. Worktree has unrelated dirty files.
- Authoritative artifacts: `/data/lcq/.codex/skills/.codex/specs/codegraph-codex-skill/plan.md`; source project `https://github.com/colbymchenry/codegraph`; local Codex config `/data/lcq/.codex/config.toml`.
- Decisions: Use light spec2plan; default install path is global npm plus upstream Codex MCP snippet; fallback is `npx` MCP launch.
- Verification: Plan still needs `validate_plan_contract.py`; implementation verification listed in `Validation Plan`.
- Remaining risks: Codex restart required for MCP visibility; global npm install preference not confirmed; dirty tree must be preserved.
- Next action: Validate this plan, then implement Tasks 1-8 if user says proceed.
- Suggested skills: `git-workflow-and-versioning`, `apply-patch`, `skill-creator`, `skill-tokenless`, `debugging-and-error-recovery` if CLI/MCP smoke fails.
- Redactions / omitted raw data: No secrets inspected; raw web/docs not copied beyond short config snippet and CLI help facts.
