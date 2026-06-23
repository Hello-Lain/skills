# Compatibility

## Repositories with no structural tools preinstalled

- Self-check the selected tool first.
- Prepare it in a user-controlled root when the route allows preparation.
- If the selected structural route still lacks a healthy toolchain, return `BLOCK`.

## Tiny edits

- Tiny unique prose-like edits may use strict text fallback.
- Tiny does not override structured-data or semantic-route requirements.

## Generated files

- Prefer the owning generator or formatter.
- Reject manual patching that fights generated output.

## Mixed-language repos

- Classify per target file.
- Keep one primary route per edit batch; split unrelated file classes when needed.

## Java without valid OpenRewrite context

- Treat as unsupported for semantic migration.
- Return `BLOCK`; do not fake support with manual patching.
