# Shared Artifact Contract

This contract defines the default save location, names, lineage metadata, and conflict handling for skill-produced planning artifacts.

## Topic Workspace

Save new artifacts under one topic workspace:

```text
.codex/work/<yyyyMMdd>-<topic-slug>/
```

`<yyyyMMdd>` is the local calendar date when the topic workspace is created. `<topic-slug>` is the stable topic name shared by all stages.

Canonical workspace layout:

```text
.codex/work/<yyyyMMdd>-<topic-slug>/
  manifest.yaml
  idea.md
  spec.md
  plan.md
  artifacts/
  subagents/
  revisions/
```

Create only the files and directories needed for the current stage, but preserve these names for all canonical artifacts and generated outputs.

## Slug Rules

- Derive `<topic-slug>` from the user-facing topic, not from the skill name.
- Use lowercase ASCII letters, digits, and hyphens only.
- Replace whitespace and punctuation with a single hyphen.
- Trim leading and trailing hyphens.
- Keep the slug stable across idea, spec, and plan stages unless the user explicitly renames the topic.
- If `.codex/work/<yyyyMMdd>-<topic-slug>/` already exists for a different topic, append `-v2` or another meaningful suffix.

## Manifest

Every topic workspace must include `manifest.yaml` once any canonical artifact is saved.

Required fields:

```yaml
version: 1
id: "work_<yyyyMMdd>_<topic_slug>"
slug: "<yyyyMMdd>-<topic-slug>"
title: "<human readable topic>"
created_at: "<ISO-8601 timestamp>"
updated_at: "<ISO-8601 timestamp>"
stage: "idea|spec|plan"
owner_skill: "idea-refine|interview-me|spec2plan"
canonical:
  idea: null
  spec: null
  plan: null
lineage:
  idea: null
  spec: null
  plan: null
source:
  created_by: "<skill name>"
  user_prompt_hash: null
locks:
  canonical_idea: null
  canonical_spec: null
  canonical_plan: null
history: []
```

Rules:

- `version` is `1` for this contract.
- `slug` includes the date prefix and topic slug.
- `stage` is the most mature confirmed artifact currently saved.
- `canonical` maps artifact types to canonical filenames. Use `null` for artifacts that do not exist yet.
- `lineage` links each artifact to its direct source path, or `null` when no source exists.
- `locks` records which canonical artifact paths are currently authoritative.
- `history` records stage changes, replacements, and revision writes.
- Update `updated_at` whenever any canonical artifact, revision, generated artifact, or subagent handoff changes.

## Canonical Artifacts

Canonical artifact names are fixed:

- `idea.md` for refined idea output.
- `spec.md` for confirmed requirements/spec output.
- `plan.md` for implementation plan output.

Generated supporting files go under:

- `artifacts/` for task outputs, review notes, validation logs, and worker reports.
- `subagents/` for subagent briefs, handoffs, and per-worker scratch artifacts.
- `revisions/` for non-canonical alternatives or superseded drafts.

## Lineage

Prefer reusing an existing topic workspace when moving from idea to spec to plan.

- If a spec is produced from `idea.md`, set `lineage.spec` to `idea.md`.
- If a plan is produced from `spec.md`, set `lineage.plan` to `spec.md`.
- If the source is outside the workspace, store the source path as given.
- If there is no source artifact, keep the lineage value `null`.

Do not duplicate a topic into a new workspace when a matching workspace path is provided or can be unambiguously inferred from the input artifact path.

## Information Preservation And Enrichment

The canonical artifact chain is:

```text
idea.md -> spec.md -> plan.md -> artifacts/*
```

Every downstream artifact must be a strict enrichment of its direct upstream input for all facts that still matter downstream.

Rules:

- Read the direct lineage source before drafting the downstream artifact.
- When the workspace already contains earlier canonical artifacts, inspect them too before dropping, reframing, or narrowing any user-confirmed fact.
- Carry forward every downstream-relevant fact from upstream artifacts: problem, target user, why now, success criteria, chosen direction, scope in/out, constraints, assumptions, risks, domain terms, acceptance checks, explicit decisions, and explicit `Not Doing` boundaries.
- Add stage-specific specificity rather than rewriting a shorter summary. `spec.md` should close questions and add requirement detail beyond `idea.md`; `plan.md` should add concrete files, symbols, commands, tasks, rollback, and validation detail beyond `spec.md`; execution artifacts should add actual commands, edits, outcomes, and verdicts beyond `plan.md`.
- If a downstream artifact omits, defers, or supersedes an upstream detail, record that explicitly with a reason such as `not needed for planning`, `superseded by confirmed user answer`, or `moved to open question`.
- Never silently narrow scope, loosen a constraint, remove a risk, or discard an assumption that still matters downstream.
- When upstream artifacts conflict, resolve the conflict explicitly in the downstream artifact instead of silently picking one version.

## Conflict Rules

No skill may silently overwrite a canonical artifact.

When the intended canonical file already exists:

- If the user explicitly asked to replace it, overwrite only that canonical file and update `manifest.yaml`.
- If the new content is a non-canonical alternative, save it under `revisions/<artifact>-<yyyyMMdd-HHmmss>.md`.
- If replacement intent is unclear, ask before overwriting.

Never overwrite `manifest.yaml` without preserving existing keys that are still valid for the workspace.

## Per-Skill Save Behavior

`idea-refine`:

- Creates or reuses `.codex/work/<yyyyMMdd>-<topic-slug>/`.
- Saves the canonical direction as `idea.md`.
- Sets `stage: idea`.
- Sets `canonical.idea: idea.md`.
- Sets `locks.canonical_idea: idea.md`.

`interview-me`:

- Reuses the input topic workspace when the interview starts from an existing workspace artifact.
- Saves the confirmed spec as `spec.md`.
- Sets `stage: spec`.
- Sets `canonical.spec: spec.md`.
- Sets `locks.canonical_spec: spec.md`.
- Sets `lineage.spec` to `idea.md` when the spec derives from the workspace idea.

`spec2plan`:

- Reuses the input topic workspace when the source spec is `.codex/work/<yyyyMMdd>-<topic-slug>/spec.md`.
- Saves the implementation plan as `plan.md`.
- Sets `stage: plan`.
- Sets `canonical.plan: plan.md`.
- Sets `locks.canonical_plan: plan.md`.
- Sets `lineage.plan` to `spec.md` when the plan derives from the workspace spec.
- Writes task output artifacts under `artifacts/`.
- Writes heavy-mode subagent briefs and handoffs under `subagents/`.

## Legacy Cleanup

The legacy generated artifact locations are not canonical for new work:

- ideas directories under `.codex/`
- specs directories under `.codex/`
- plans directories under `.codex/`

Do not create new artifacts in those directories by default. Existing legacy artifacts may be deleted instead of migrated when they are confirmed generated outputs and are no longer needed for an active handoff. Do not delete source skill files or the current handoff artifacts before replacement paths exist.
