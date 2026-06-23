# Fallback Policy

Strict text fallback exists for tiny, unique, low-risk edits. It is not a silent escape hatch.

## Text Fallback Allowed

All of these must be true:

- edit is tiny;
- target is uniquely anchored;
- change is low-risk and local;
- change is prose-like or formatting-preserving;
- a structural route would add more complexity than safety.

## Text Fallback Forbidden

Return `BLOCK` instead of patching when:

- a generator-owned route should apply;
- Python/JS/TS semantic rewrite should use AST or codemod tooling;
- JSON/YAML field or path operation should use `jq`/`yq`;
- Markdown section/list/frontmatter rewrite should use `remark`;
- Java migration would require `openrewrite`;
- the file class is in the mandatory-structural set and only fragile patching remains.

## Required BLOCK Response

Include:

- selected route
- missing or failing tool
- self-check or install command
- tool root path
- exact reason the edit cannot continue safely
