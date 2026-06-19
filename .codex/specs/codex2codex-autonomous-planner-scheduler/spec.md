# Spec: Autonomous Planner/Scheduler Contract for codex2codex

## Objective

Build an automatic planner/scheduler contract for `codex2codex` so lead Codex can take a natural-language or semi-structured `plan.md`, generate a safe executable worker DAG, compile it into valid `tasks.md`/manifest artifacts, launch appropriate `meight` workers, run review/fix loops, and keep final integration/approval with the lead.

The goal is not free-form swarm autonomy. The goal is controlled, machine-verifiable multi-agent execution with higher work quality, lower error probability, and minimal lead-context pollution.

## Users

Primary user: lead Codex.

Lead Codex needs to:

- Convert `plan.md` into executable worker waves without manually writing `tasks.md`.
- Decide worker roles, scopes, concurrency, review structure, and fix loops automatically.
- Keep raw worker transcripts/logs out of the main context.
- Receive only compact artifacts, verdicts, blockers, and final integration summaries.
- Preserve final authority over git, user communication, and acceptance.

Secondary user: human operator.

The human operator needs:

- A predictable, auditable workflow.
- Artifacts that explain what workers did.
- Safety boundaries that prevent runaway agent behavior.
- A final summary from lead Codex, not from arbitrary workers.

## Problem

Current `codex2codex` can execute structured `tasks.md` waves, validate manifests, start workers, collect artifacts, and trigger review/fix behavior. Its weakness is upstream planning.

Today, it cannot reliably infer from a raw or semi-structured `plan.md`:

- How many workers are needed.
- Which specialized roles should exist.
- Which files each worker may read/write.
- Which tasks can run in parallel.
- Which reviews are needed.
- Which validation commands should be required.
- How to adapt after review failure or worker uncertainty.

This makes `codex2codex` an effective static wave runner, but not yet an autonomous planner/scheduler.

## Success Criteria

- Given a `plan.md`, the system generates a valid `.codex/specs/<slug>/tasks.md` without requiring the user to manually define every task.
- The generated task graph contains worker roles, dependencies, file scopes, verification commands, output artifacts, and review gates.
- The scheduler compiles the task graph into one or more waves where same-wave write scopes do not conflict.
- The system can launch multiple workers when scopes are file-disjoint and can conservatively serialize when conflict or uncertainty exists.
- The system can create task-specific specialized roles, but each specialized role is bound to a base archetype and a machine-checkable capability envelope.
- Review workers return explicit `PASS` or `FAIL`.
- Any scoped `FAIL` creates a bounded fix wave and reruns the affected review.
- Lead Codex receives only compact summaries/artifacts, not raw worker logs or transcripts.
- Workers cannot recursively spawn workers, commit/push git changes, speak to the user, or edit outside approved scope.
- If the planner is uncertain about scope, verification, or safety, it must choose conservative serialization, ask a `QUESTION`, or fail validation before worker launch.
- Final acceptance remains with lead Codex.

## Scope

### In

- A planner/scheduler contract for converting `plan.md` into executable task DAGs.
- A machine-checkable role schema with base archetypes and dynamic specializations.
- Automatic generation of `tasks.md` and manifest files.
- Automatic wave construction based on dependencies and write-scope conflict detection.
- Automatic worker brief generation from task metadata.
- Automatic worker launch through existing `meight` primitives.
- Automatic review wave generation.
- Automatic bounded fix-wave generation after review `FAIL`.
- Context-isolation rules that prevent raw worker output from entering the lead context.
- Validation gates before launch, after worker result, after review, and before final summary.
- Conservative fallback behavior when planning confidence is low.

### Out

- Infinite or recursive agent spawning.
- Worker-created sub-workers.
- Automatic `git commit`, `git push`, branch publication, or PR creation.
- Worker communication with the human user.
- Worker authority to expand its own write scope.
- Cross-repo orchestration.
- Automatic multi-worktree management in v1.
- Production-grade distributed task database.
- Streaming raw worker transcripts into lead Codex context.
- Replacing `meight`; this spec extends orchestration above the existing execution backend.

## Requirements

### Functional

- The system must accept a `plan.md` as input.
- The system must produce a planner output artifact before launching workers.
- The planner output must include a task DAG with task IDs, dependencies, roles, scopes, verification, artifact paths, and review requirements.
- The system must generate or update `.codex/specs/<slug>/tasks.md`.
- The system must generate a per-wave manifest.
- The scheduler must reject same-wave write-scope overlaps unless explicit worktree isolation is available and enabled.
- The scheduler must prefer parallel execution only when file scopes are disjoint and validation commands do not conflict.
- The scheduler must serialize tasks when write scopes overlap, dependencies are ambiguous, or risk is elevated.
- The planner may create specialized roles dynamically.
- Every specialized role must inherit from a base archetype.
- Every role must declare a capability envelope.
- Every worker brief must include role, instance name, spec path, wave, file scope, task, verification, output artifact, concurrency assumptions, and restrictions.
- Every worker must write or return a structured artifact.
- Implementation artifacts must include changed files, verification performed, risks, and blockers.
- Review artifacts must include scope, findings, verification, and `Verdict: PASS|FAIL`.
- On review `FAIL`, the system must generate a fix wave scoped only to the failed findings.
- After a fix wave, the system must rerun the affected review.
- The number of fix cycles must be bounded.
- The lead must receive a compact final summary containing waves, workers, artifacts, verdicts, verification, blockers, and cleanup status.
- Raw event logs, full transcripts, secrets, and unrelated worker output must not be included in the lead final summary.

### Non-Functional

- Safety is higher priority than autonomy.
- Deterministic validation gates must reject invalid planner output before worker launch.
- The system must be auditable through durable artifacts under `.codex/specs/<slug>/`.
- The system must keep lead context small by summarizing worker outputs and reading only required artifacts.
- The system must fail closed: invalid scope, missing verification, missing artifact, unresolved blocker, or missing review verdict must prevent success.
- The system must prefer conservative scheduling when confidence is low.
- The workflow must remain usable by Codex without human terminal babysitting.
- The workflow must not require manual task splitting for ordinary `plan.md` inputs.

## Role Model

### Base Archetypes

The system should define a small set of base archetypes. Example archetypes:

- `planner`: converts input plan into task DAG and scheduling metadata.
- `coding`: implements scoped product/code changes.
- `review`: independently reviews scoped changes and returns `PASS` or `FAIL`.
- `devops`: handles build, CI, environment, scripts, and operational validation.
- `sa`: performs architecture, risk, or design review.

These are not the only roles workers may have. They are capability bases.

### Dynamic Specialized Roles

The planner may create task-specific roles when useful.

Examples:

- `django-auth-migration-coder`
- `pytest-regression-writer`
- `ci-cache-debugger`
- `security-boundary-reviewer`
- `api-contract-auditor`
- `docs-runbook-updater`

A specialized role is valid only if it declares:

- `base_archetype`
- `purpose`
- `allowed_read`
- `allowed_write`
- `forbidden_actions`
- `verification`
- `artifact_path`
- `review_required`
- `max_followups`
- `context_budget`
- `risk_level`

Specialized roles must not expand their own authority at runtime.

## Capability Envelope

Every worker must be bound by a capability envelope.

Minimum fields:

```yaml
role_id: django-auth-migration-coder
base_archetype: coding
purpose: Implement the scoped auth migration.
allowed_read:
  - src/auth/**
  - tests/auth/**
allowed_write:
  - src/auth/**
  - tests/auth/**
forbidden_actions:
  - git commit
  - git push
  - spawn workers
  - edit files outside allowed_write
  - contact user
verification:
  - pytest tests/auth
artifact_path: .codex/specs/auth-migration/artifacts/django-auth-migration-coder.md
review_required: true
max_followups: 2
context_budget: minimal
risk_level: medium
```

The scheduler must reject any worker without a valid capability envelope.

## Planner Output Contract

The planner must emit machine-checkable output before execution.

Recommended shape:

```json
{
  "spec_slug": "autonomous-planner-scheduler",
  "source_plan": "plan.md",
  "confidence": "medium",
  "tasks": [
    {
      "id": "task-001",
      "title": "Generate scheduler role schema",
      "base_archetype": "coding",
      "specialized_role": "scheduler-contract-impl",
      "purpose": "Implement role schema validation.",
      "depends_on": [],
      "allowed_read": [
        "codex2codex/scripts/**",
        "codex2codex/SKILL.md"
      ],
      "allowed_write": [
        "codex2codex/scripts/orchestrate_plan.py",
        "codex2codex/schemas/role.schema.json"
      ],
      "verification": [
        "python -m pytest codex2codex/tests"
      ],
      "artifact_path": ".codex/specs/autonomous-planner-scheduler/artifacts/task-001.md",
      "review_required": true,
      "risk_level": "medium"
    }
  ],
  "review_strategy": {
    "required": true,
    "mode": "scoped",
    "verdict_required": true
  },
  "scheduling_policy": {
    "parallelize_when": "write_scopes_disjoint",
    "serialize_when": "scope_overlap_or_uncertainty",
    "max_fix_cycles": 2
  }
}
```

## Scheduler Rules

- Build waves from dependency order and write-scope compatibility.
- Tasks with overlapping `allowed_write` must not run in the same wave.
- Tasks with unknown or broad write scopes must run alone.
- High-risk tasks may require review before downstream dependent waves.
- Review tasks must run after implementation tasks they review.
- Fix tasks must only target failed review findings.
- Rerun only affected review scopes after fix unless global integration risk is detected.
- If the scheduler cannot prove a wave is safe, it must not parallelize it.

## Context Isolation

The system must protect lead Codex context.

Allowed into lead context:

- Planner summary.
- Generated tasks/waves summary.
- Worker artifact paths.
- Review verdicts.
- Critical findings.
- Verification command/result summaries.
- Blockers requiring lead decision.
- Final compact integration report.

Forbidden from lead context by default:

- Raw worker transcripts.
- Full event logs.
- Long terminal output.
- Secrets or credentials.
- Unrelated worker reasoning.
- Repeated intermediate progress chatter.

Raw data may remain on disk for debugging, but final summaries must reference paths and compressed findings, not paste transcripts.

## Failure Handling

The system must fail or pause when:

- Planner output is invalid.
- Required fields are missing.
- Write scopes conflict inside a wave.
- A worker edits outside approved scope.
- A worker omits its artifact.
- Verification is missing.
- Review verdict is missing.
- Review returns `FAIL`.
- Worker returns unresolved `QUESTION`.
- Worker attempts forbidden actions.
- Raw logs or secrets would be included in summary.
- Fix cycle limit is reached.

When failure is recoverable, the system should generate a bounded fix wave or ask lead Codex for a decision.

## Constraints

- Must build on existing `codex2codex` and `meight` execution model.
- Must preserve lead ownership of git and final acceptance.
- Must prioritize control and safety over maximum autonomy.
- Must support dynamic specialized roles without allowing unrestricted capabilities.
- Must keep worker execution auditable through `.codex/specs/<slug>/`.
- Must not require human-authored `tasks.md` for ordinary plan inputs.
- Must not let workers recursively spawn workers.

## Assumptions To Validate

- [ ] Existing `plan_to_tasks.py`, `prepare_wave.py`, and `run_wave.py` can be extended instead of replaced - validate by inspecting current script boundaries.
- [ ] `meight` result/status artifacts provide enough metadata to validate worker scope and artifacts - validate against current `status.json` and `result.md` behavior.
- [ ] File-scope conflict detection can be reliable enough with glob/path matching in v1 - validate with sample overlapping and disjoint scopes.
- [ ] Verification commands can be inferred from repo conventions often enough for v1 - validate on representative Python/TS/docs projects.
- [ ] Dynamic specialized role generation improves quality without increasing scope drift - validate with review outcomes across sample plans.

## Risks

- Planner creates plausible but unsafe scopes - mitigate with strict schema validation and conservative scheduling.
- Dynamic roles become unbounded swarm behavior - mitigate by requiring base archetype inheritance and capability envelopes.
- Worker artifacts are too verbose and pollute lead context - mitigate with artifact contracts and summary-only lead ingestion.
- Review misses cross-task integration bugs - mitigate with final integration review when multiple waves touch related modules.
- Auto-generated verification commands are wrong or insufficient - mitigate by requiring explicit verification field and allowing planner uncertainty to trigger `QUESTION`.
- Fix waves chase review failures indefinitely - mitigate with `max_fix_cycles`.
- Workers silently exceed scope - mitigate with git diff/path validation before accepting results.
- High autonomy hides important decisions from lead - mitigate by surfacing blockers, risky tradeoffs, and scope changes as lead decisions.

## Acceptance Checks

- Provide a sample `plan.md`; system generates valid `.codex/specs/<slug>/tasks.md`.
- Validate generated planner output against a schema.
- Validate generated manifest has no same-wave write-scope conflicts.
- Confirm every task has role, base archetype, allowed read/write scope, verification, artifact, dependencies, and review setting.
- Confirm dynamic specialized roles are accepted only when bound to a base archetype and capability envelope.
- Run a dry-run scheduler and inspect planned waves without launching workers.
- Run an execution on a small repo and confirm multiple workers launch only when write scopes are disjoint.
- Force a review `FAIL` and confirm a bounded fix wave is generated.
- Confirm affected review reruns after fix.
- Confirm missing artifact, missing verdict, or missing verification fails validation.
- Confirm final lead summary omits raw worker transcripts and event logs.
- Confirm workers do not commit, push, contact user, spawn workers, or edit outside approved scope.

## Open Questions

- Should `orchestrate_plan.py` be a new script, or should `run_plan.py` absorb planner/scheduler behavior?
- What schema format should be canonical: JSON Schema, YAML schema, or Markdown with embedded JSON blocks?
- Should v1 include repo inspection for verification inference, or require planner to emit verification with uncertainty handling?
- Should high-risk plans require an explicit `sa` review before implementation?
- Should the role registry live under `roles/`, `agents/`, or `.codex/specs/<slug>/roles.generated.yaml`?
- What is the default maximum worker count per wave?
- What is the default maximum fix cycle count?
