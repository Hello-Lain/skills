# Spec: Edit Orchestration Skill

## Objective
Build a replacement for the current `apply_patch` skill for Codex users working in `/data/lcq/.codex/skills` and child workspaces. The new skill should maximize edit correctness while preserving efficiency by routing each file-editing task through a unified safety protocol, using a fast `apply_patch` path for small edits and mature external tools for complex edits.

## Users
- Primary: Codex agents editing code, configuration, docs, and skill files in the user's Codex skill ecosystem.
- Secondary: The user, who needs fewer failed patches, fewer unintended edits, and less manual tool setup.

## Problem
The current `apply_patch` skill is a narrow manual patch discipline. It helps with precise edits, but it does not choose better edit mechanisms, prepare mature helper tools, enforce a full review/test gate, or distinguish simple edits from structural rewrites. Complex edits can fail due to brittle context matching, repeated patterns, AST-sensitive changes, or stale worktree state.

## Success Criteria
- Small edits remain efficient: single-file low-risk edits follow a fast path with no heavyweight tool startup unless needed.
- Edit failures decrease: failed patch attempts route into explicit recovery or stop states instead of repeated stale retries.
- Unintended edits decrease: every change path includes intent capture, dirty-state awareness where relevant, diff inspection, and verification before final response.
- Complex edits improve: multi-file, repeated, migration, or syntax-aware edits can use mature tools instead of hand-built broad patches.
- Tooling is self-prepared: the skill can install or bootstrap required helper CLIs in user-level locations without asking the user to preconfigure them.
- Tool self-checks are mandatory: if the selected route requires a helper tool and install/self-test fails, the skill stops instead of silently downgrading to a weaker route.

## Scope
### In
- Trigger for all manual file-editing tasks.
- Internal route selection by edit risk and shape:
  - Fast path: small, unique-context, low-risk edits with `apply_patch`.
  - Patch recovery path: failed hunk, stale context, whitespace/line-ending ambiguity, duplicate anchors.
  - Agent-edit path: use Aider-style edit formats, repo-map/context, lint/test retry concepts for complex natural-language changes.
  - Review-before-apply path: use Plandex-style isolation, pending diff review, and apply gate concepts for larger multi-file work.
  - Structural rewrite path: use AST or codemod tools such as `ast-grep`, `jscodeshift`, or OpenRewrite when the task is repeated, syntax-aware, or migration-like.
  - Generated-output path: let project-owned generators/formatters/package managers write their owned files, then inspect diff.
- User-level tool preparation:
  - Network install is allowed.
  - Versions must be pinned or otherwise recorded.
  - Installation must target user/cache/project-controlled locations such as `$CODEX_HOME/tools`, `~/.local/bin`, or project `.codex/tools`.
  - No `sudo` or system package manager mutation.
- Preflight checks:
  - Understand requested behavior and target files.
  - Inspect existing patterns before editing.
  - Check dirty worktree state when repo state matters.
  - Preserve unrelated user changes.
- Post-edit gates:
  - Inspect diff against stated intent.
  - Run focused verification when relevant.
  - Run broader checks when cheap.
  - Report exact verification commands and gaps.

### Out
- Building a full replacement coding agent or IDE from scratch.
- Global/system-level installation, `sudo`, or mutation of OS package manager state.
- Silent downgrade when a selected helper route fails self-check.
- Ignoring dirty worktree conflicts.
- Treating formatter, lockfile, or generated-file churn as automatically acceptable without diff review.
- Rewriting unrelated files to make a patch apply.

## Requirements
### Functional
- The skill must classify each manual edit by risk and choose the lightest safe route.
- The skill must use `apply_patch` for low-risk surgical edits where it is clearly sufficient.
- The skill must prefer mature external components for complex edits rather than reimplementing their behavior in instructions.
- The skill must be able to prepare required helper tools automatically in user-level locations.
- The skill must pin or record tool versions and run a minimal self-check before relying on a prepared tool.
- The skill must stop and explain the failed route if the required helper tool cannot be prepared or self-checked.
- The skill must include an explicit recovery playbook for patch failures, including raw whitespace inspection and re-reading changed regions before retrying.
- The skill must require diff review before finalizing edits.
- The skill must require targeted verification for behavior-changing code edits.
- The skill must report when verification is skipped and why.

### Non-Functional
- Reliability first: avoid edits that can plausibly modify unintended regions.
- Efficiency second: do not launch/install heavy tools for trivial edits.
- Auditability: tool installs, selected routes, commands, and verification gaps must be explainable.
- Portability: user-level tool paths must work across common Linux workspace setups.
- Context economy: the skill body should keep only the core protocol; detailed tool recipes should live in references or scripts loaded only when needed.

## Constraints
- The skill replaces the current `apply_patch` role in the user's skill ecosystem.
- The skill operates inside `/data/lcq/.codex/skills` unless later installed elsewhere.
- Automatic setup may use network access, but only with user-level install targets.
- Do not require the user to manually configure helper tools before the skill can work.
- Do not use system-level package mutation or privileged commands.
- If selected route self-check fails, stop rather than falling back to a weaker hidden route.

## Assumptions To Validate
- [ ] `aider` can be installed and invoked from a user-level pinned tool path without interfering with existing Codex workflows - validate with a dry-run/self-check script during implementation.
- [ ] `ast-grep` is the best default structural rewrite helper for multi-language code in this workspace - validate by testing install and a no-op pattern command.
- [ ] `jscodeshift` and OpenRewrite should be optional route-specific helpers rather than always-installed defaults - validate against expected JS/Java migration use cases.
- [ ] A pure workflow skill plus optional setup scripts is acceptable in the Codex skill loader - validate with existing skill conventions and quick validation tooling.

## Risks
- Toolchain bloat - mitigate with lazy route-specific installs and references/scripts instead of loading everything by default.
- Network install flakiness - mitigate with pinned versions, cache paths, clear stop messages, and no silent downgrade.
- External tool behavior drift - mitigate with recorded versions and self-checks.
- Over-routing simple edits to heavy tools - mitigate with a fast path that keeps small edits on `apply_patch`.
- False confidence from generated/codemod changes - mitigate with mandatory diff review and focused verification.
- Dirty worktree collisions - mitigate with preflight status checks and stopping on conflicting user changes.

## Acceptance Checks
- Skill metadata triggers on manual file-edit tasks and supersedes the old `apply_patch` skill behavior.
- A low-risk single-file edit follows fast path: read target, apply patch, inspect diff, verify if needed.
- A repeated structural change routes to `ast-grep` or another structural tool and stops if that tool cannot self-check.
- A complex multi-file natural-language edit routes to an Aider/Plandex-inspired heavy path and requires review before apply.
- Tool preparation installs only under user/cache/project-controlled paths and records versions.
- No route uses `sudo` or mutates system package manager state.
- Patch failure recovery re-reads raw target text before retrying and never reuses stale context.
- Final response includes changed files, verification commands, outcomes, and known gaps.

## Open Questions
- Exact skill name: likely `edit-orchestration`, `safe-edit`, or `surgical-edit`.
- Which helper tools should be bundled as setup scripts in v1 versus documented as route-specific optional tools.
- Whether to keep the old `apply-patch` skill installed but narrower, or replace/rename it after validation.
