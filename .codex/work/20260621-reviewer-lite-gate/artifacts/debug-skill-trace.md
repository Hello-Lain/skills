# Debug Skill Trace: Reviewer Lite Gate Integration

## Trace Pass 1
- Trigger: user requested `spec2plan` + `plan2do` + `reviewer`, with `debug-skill` tracking skill trajectory and optimization points.
- Skills loaded: `spec2plan`, `plan2do`, `reviewer`, `debug-skill`, `skill-tokenless`, `context-engineering`, `edit-orchestration`.
- Decisions: use light spec2plan because the spec is clear and execution is primary-agent; require production gate and final reviewer gate because the change is a material workflow update.
- Actions: wrote validated `plan.md`, compiled `execution/tasks.json`, added shared `reviewer` integration guide, patched four consumer skill hooks, and recorded task artifacts.
- Failures / friction: `rtk proxy cat` compressed long skill files, so the workflow needed targeted `sed` reads to rehydrate missing lines.
- Recovery: re-read truncated sections with precise line ranges before planning and editing.
- Verification: plan validator, execution compiler, quick_validate for five skills, debug-skill self-test, skill-tokenless self-test, grep gates, and `git diff --check` passed before draft production report.
- Result: net-positive so far; skill chain increased gate coverage but added context load cost.

## Optimization Candidates
| Candidate | Target surface | Evidence | Benefit | Risk | Fitness |
| --- | --- | --- | --- | --- | --- |
| A | `reviewer` | Consumer skills need only one stable hook. | Reduces duplicated review rules. | Integration guide may grow too broad. | High |
| B | `spec2plan` | Material skill plans need production-gate boilerplate. | A reusable plan snippet could reduce validator churn. | Too much template text may bloat plans. | Medium |
| C | `debug-skill` | Continuous trace is useful but external reuse search is costly mid-execution. | Add a lightweight in-run trace mode plus final deep audit mode. | Could under-search if misused. | Medium |

## Open Follow-Up
- Final reviewer gate returned `PASS`; no rework findings.
- External reuse sources checked for pattern fit: `https://github.com/obra/superpowers`, `https://github.com/plandex-ai/plandex`, `https://github.com/Aider-AI/aider`, `https://github.com/pre-commit/pre-commit`, `https://github.com/NousResearch/hermes-agent-self-evolution`.
- Final optimization point: `debug-skill` could benefit from an explicit lightweight in-run trace mode, then a deeper post-run audit mode for source search and candidate scoring.
