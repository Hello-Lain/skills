# Task 4: Route Examples

- Status: complete
- File changed:
  - `edit-orchestration/references/examples.md`
- Covered routes:
  - `fast path`
  - `patch recovery path`
  - `structural rewrite path`
  - `agent-edit path`
  - `review-before-apply path`
  - `generated-output path`

## Verification

- `grep -R "fast path\\|patch recovery path\\|structural rewrite path\\|agent-edit path\\|review-before-apply path\\|generated-output path" -n edit-orchestration` found all route names.
- `grep -R "selected route" -n edit-orchestration` found stop behavior in `SKILL.md` and `examples.md`.
