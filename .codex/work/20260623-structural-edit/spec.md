# Structural Edit Skill Spec

## Summary

Create a new `structural-edit` skill that becomes the default entrypoint for file editing in this Codex environment. The skill must replace text-patch-first behavior with a structure-first editing bus:

1. prefer project-owned generators/formatters when they own the output;
2. otherwise prefer parser/AST/LSP/codemod-based edits for supported file types;
3. use strict parser-aware tools for structured text formats;
4. allow a tightly constrained text-patch fallback only when the file type or edit shape does not justify heavy structural tooling;
5. hard-stop with `BLOCK` when the selected structural route should apply but the required toolchain is missing or unhealthy.

This is not a small additive helper. It is a replacement-grade editing skill plus a migration plan for `edit-orchestration`.

## Problem

The current editing workflow is not globally optimal.

- `edit-orchestration` still treats `apply_patch` as the default fast path.
- Text-anchored patching is fragile under repeated sections, long prose, drifted context, multi-file edits, and partial state after previous retries.
- Existing helper-tool support is advisory and route-specific, but the architecture still starts from patching rather than from structure.
- Silent or easy fallback to text patching keeps the system operational while preserving the root failure mode.

The user goal is not “make patches slightly better.” The goal is:

- raise edit success rate;
- reduce retry loops and patch misses;
- improve correctness for code/config/docs edits;
- keep edits auditable and deterministic;
- force the system to stop rather than continue unsafely when its required editing substrate is unavailable.

## Non-Goals

- v1 does **not** need first-class support for `C/C++`, `Rust`, or niche languages.
- v1 does **not** need zero external dependencies.
- v1 does **not** need to remove all text editing forever.
- v1 does **not** need a fully autonomous external coding agent.
- v1 does **not** need background daemons, remote services, or persistent review memory.

## Confirmed Success Criteria

The skill is successful only if all of the following are true:

1. `structural-edit` becomes the default editing entrypoint for manual file edits in this Codex skill set.
2. Supported file classes must prefer structure-aware routes before any text-patch route:
   - `Python`
   - `TypeScript / JavaScript`
   - `JSON`
   - `YAML`
   - `Markdown`
3. `Java` is conditionally supported when a valid OpenRewrite-capable project/build environment exists.
4. If a selected structure-aware route requires a toolchain that is missing or fails self-check, the skill must return `BLOCK` and must not silently downgrade to fragile patching.
5. `edit-orchestration` no longer remains the authoritative default. It is either:
   - replaced by `structural-edit`, or
   - reduced to a compatibility shell that delegates to `structural-edit`.
6. The new skill includes formal installation, self-check, version recording, migration, compatibility, rollback, and validation contracts.
7. The final design is demonstrably better than the old patch-first design on curated representative scenarios.

## Introspector Verdict Incorporated

The original “replace everything, never use text patching” direction is **not** the global optimum.

The accepted architecture is a **merge path**:

- structure-aware editing becomes the primary and default bus;
- text patching remains only as a **strictly constrained fallback layer**;
- fallback must never trigger silently when a selected structure-aware route is expected but unavailable.

This avoids preserving the current weakness while also avoiding over-engineering tiny or prose-only edits into heavyweight tool paths.

## File-Type Coverage And Required Primary Routes

### 1. Python

Primary route:

- `ast-grep` structural search/rewrite

Secondary route:

- constrained `apply_patch` only for tiny unique edits that do not justify structural rewrite

Rationale:

- multi-language coverage;
- AST-based matching and rewriting;
- better fit than regex/text for function/class/import/decorator edits.

### 2. TypeScript / JavaScript

Primary route:

- `jscodeshift` for semantic/codemod-style transforms

Secondary route:

- `ast-grep` for simpler structural rewrites where a full JS codemod is unnecessary

Fallback:

- constrained `apply_patch` only for tiny unique edits or prose-like non-code fragments

Rationale:

- `jscodeshift` is a mature codemod toolkit for JS/TS;
- `ast-grep` remains useful for lighter pattern-driven transforms and cross-language consistency.

### 3. JSON

Primary route:

- `jq`

Fallback:

- no text-patch fallback when the intended edit is a structured field/value transformation that `jq` should handle
- constrained `apply_patch` allowed only for tiny unique formatting-preserving edits where structural transformation is not the intended operation

Rationale:

- JSON is structured data, not prose;
- parser-aware transformation should be the default.

### 4. YAML

Primary route:

- `yq`

Fallback:

- no text-patch fallback when the intended edit is a structured key/path/value operation that `yq` should handle
- constrained `apply_patch` only for rare non-semantic micro-edits after explicit route reasoning

Rationale:

- YAML config drift is a major source of patch instability;
- `yq` gives structured operations and JSON-compatible expression power.

### 5. Markdown

Primary route:

- `remark` / `unified` AST-based editing for heading/section/list/frontmatter-aware edits

Formatting route:

- `prettier` or project-owned formatter only when formatting ownership is explicit

Fallback:

- constrained `apply_patch` for tiny unique prose changes that are cheaper and equally safe as AST edits

Rationale:

- Markdown mixes prose and hierarchy;
- purely line-based section rewrites are fragile;
- formatter alone is not a semantic editor, so formatter must not be treated as the primary edit engine.

### 6. Java

Primary route:

- `OpenRewrite`, only when:
  - project build files exist; and
  - Maven/Gradle execution path is valid; and
  - recipe execution is feasible in the current repo

Fallback:

- no fake generic standalone Java rewrite path
- if Java structural route is required and unavailable, return `BLOCK`

Rationale:

- Java should use its mature migration ecosystem rather than generic patching.

## Tool Selection Decision

### Chosen Core Tools

#### `ast-grep`

Chosen as the general structural rewrite backbone because it is:

- mature;
- actively documented;
- polyglot;
- fast;
- suitable for search, lint, rewrite, and interactive codemod workflows.

#### `jscodeshift`

Chosen for JS/TS semantic codemods because it is:

- battle-tested;
- specialized for JS-family transforms;
- better than a generic tool for API migrations and AST-aware refactors.

#### `jq`

Chosen for JSON because it is:

- standard;
- lightweight;
- structure-aware;
- easy to distribute as a single binary.

#### `yq`

Chosen for YAML because it is:

- mature;
- jq-like;
- suitable for structured config mutation across YAML and adjacent formats.

#### `remark` / `unified`

Chosen for Markdown because it:

- treats Markdown as AST, not text blobs;
- supports heading/list/frontmatter aware transformation;
- is better aligned than regex or plain formatters for document-structure edits.

#### `OpenRewrite`

Chosen as conditional Java support because it is:

- purpose-built for recipe-driven JVM migrations;
- preferable to pretending Java can be safely handled by generic patching in migration-heavy scenarios.

### Explicitly Not Chosen As Primary Backbone

#### `Comby`

Useful and mature, but not selected as the primary core because:

- `ast-grep` gives stronger AST-native semantics for core supported languages;
- the v1 problem is not “get a better syntax-aware grep,” it is “make structure-first editing the default bus.”

Comby may be added later as a secondary auxiliary tool, but not as the v1 architectural center.

#### `Aider`

Not chosen as a primary editing route because this project needs:

- deterministic file transformations;
- explicit route semantics;
- auditable failure handling;
- minimal extra agent state.

Agent-edit helpers can remain optional, but must not define the primary architecture.

#### `Prettier`

Not a primary editor. It is a formatter-only route when formatting ownership is explicit.

## Required Architecture

`structural-edit` must implement the following route stack in order:

### Route 1: Generated Output Route

Use when a project-owned generator/formatter/package-manager/build tool owns the output.

Examples:

- lockfiles
- generated sources
- formatter-owned output
- scaffold-owned files

Behavior:

- run the owning tool;
- inspect diff;
- reject unrelated churn.

### Route 2: Structural Rewrite Route

Use when the file type is supported and the edit is semantic, repeated, cross-file, API-shaped, schema-shaped, or code-structure-sensitive.

Behavior:

- choose the file-type-specific structural tool;
- require tool self-check before use;
- install/prep only into user-controlled roots;
- return `BLOCK` if the selected toolchain is unavailable or unhealthy.

### Route 3: Parser-Aware Structured Data Route

Use for structured non-code formats such as:

- JSON
- YAML
- Markdown structure

Behavior:

- use `jq`, `yq`, `remark`/`unified`, or other approved parser-aware tools;
- treat these as first-class editing routes, not convenience extras.

### Route 4: Strict Text-Patch Fallback

Allowed only when all of the following are true:

- the edit is small;
- the target region is unique and stable;
- the edit is low-risk and reversible;
- the file is not one where the selected structured route should have applied;
- route reasoning explicitly records why text patching is acceptable.

This fallback must never be used merely because the proper structural tool is missing.

## Hard Stop Policy

The skill must stop with `BLOCK` when any of these occur:

1. The chosen supported-file route requires a structural tool that is missing.
2. Tool self-check fails after allowed preparation.
3. Version or health checks indicate the route cannot be trusted.
4. The selected structured route would normally apply, but only text patching remains available.
5. The file type is in the “must support structurally” set and the skill would otherwise silently downgrade.

The `BLOCK` response must include:

- selected route;
- missing or failing tool;
- install/self-check command;
- root path used for tool storage;
- exact reason execution cannot continue safely.

## Toolchain Management Requirements

The skill must own a formal local toolchain manager.

### Install Roots

Allowed roots must remain user-controlled, e.g.:

- `$CODEX_HOME/tools/structural-edit`
- `~/.codex/tools/structural-edit`
- project-local `.codex/tools/structural-edit`
- explicit `--root`

Forbidden:

- `sudo`
- system package manager mutation
- writes into `/usr`, `/usr/local`, `/bin`, `/etc`, `/var`, `/opt`

### Required Capabilities

The skill must provide scripts/contracts for:

- listing supported tools;
- preparing/installing selected tools;
- self-checking tool readiness;
- recording a manifest with version and command path;
- pinning package/binary versions where possible;
- reporting missing prerequisites clearly.

### Manifest

Maintain a tool manifest containing at least:

- tool id
- command path
- install method
- pinned package or binary source
- detected version
- updated timestamp
- last self-check result

### Version Policy

The skill must define:

- default install specs;
- optional pin env vars or config keys;
- upgrade rules;
- compatibility notes per tool.

## Skill Surface Requirements

`structural-edit` must include at least:

- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`

### `SKILL.md` responsibilities

It must:

- define trigger conditions;
- state default route order;
- define the hard-stop policy;
- distinguish structural routes from strict fallback;
- prohibit silent downgrade;
- state when to route to each reference file.

### `references/` responsibilities

At minimum include:

- route matrix
- tool selection and installation policy
- fallback policy
- migration plan from `edit-orchestration`
- compatibility matrix
- failure recovery
- validation scenarios

### `scripts/` responsibilities

At minimum include:

- prepare/install script
- self-check script
- manifest/report helper
- optional route-specific wrappers
- optional scenario validator

## Migration Requirements

The spec must explicitly cover migration from `edit-orchestration`.

### Required Migration Outcome

One of these must be implemented:

1. `edit-orchestration` is replaced in-place by the new architecture; or
2. `structural-edit` becomes the new primary skill and `edit-orchestration` becomes a compatibility wrapper that delegates to it.

### Migration Rules

- do not leave two competing default edit skills with ambiguous routing;
- preserve existing useful scripts or references only if they still fit the new architecture;
- remove or downgrade patch-first language in old docs;
- keep an explicit rollback path;
- update all references to the old default entrypoint.

## Compatibility Strategy

The skill must define compatibility behavior across:

- repositories with no structural tools preinstalled;
- repos that only need tiny edits;
- repos with generated files;
- repos with JS/TS codemod needs;
- repos with Python/config/doc changes;
- repos with Java but no valid OpenRewrite runtime;
- mixed-language repos.

Compatibility rule:

- “compatible” does **not** mean “continue by patching anyway.”
- It means “route correctly, or stop explicitly.”

## Validation And Acceptance

The skill must ship with explicit scenario gates.

Minimum required scenarios:

1. Python semantic edit → `ast-grep` chosen, not patch-first.
2. JS/TS migration edit → `jscodeshift` chosen.
3. JSON key/value update → `jq` chosen.
4. YAML path update → `yq` chosen.
5. Markdown section rewrite → `remark` chosen.
6. Tiny unique prose fix → strict text fallback allowed.
7. Required structural tool missing → `BLOCK`, not silent fallback.
8. Java migration request without valid OpenRewrite context → `BLOCK`.
9. Generated file mutation request → generated-output route chosen.
10. Old `edit-orchestration` invocation still reaches the new structural bus or a clearly deprecated compatibility layer.

Acceptance requires:

- deterministic self-check output;
- validated install roots;
- manifest recording;
- route-choice evidence for each scenario;
- explicit proof that missing required tools halt execution.

## Review Gate

Because this skill becomes decision-critical infrastructure, final acceptance must include:

- `reviewer` heavy gate by default;
- adversarial review focused on silent downgrade risk, route ambiguity, and fake “supported” claims;
- evidence that the chosen fallback policy does not reintroduce the old architecture under a new name.

## Implementation Guidance For Downstream Planning

When this spec is converted to a plan, the plan should likely sequence work as:

1. architecture and route contract;
2. toolchain manager and manifest;
3. core route scripts and references;
4. migration of `edit-orchestration`;
5. validation scenarios and heavy review gate.

The downstream implementation should remain surgical:

- reuse what is still good in `edit-orchestration`;
- replace patch-first defaults;
- avoid adding speculative tools beyond the confirmed v1 coverage.

## Final Direction

Build `structural-edit` as a **structure-first editing bus with a hard-stop toolchain gate and a strictly constrained text fallback**, then migrate or absorb `edit-orchestration` so the environment has one authoritative default editing path instead of competing ones.
