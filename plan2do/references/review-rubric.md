# Plan2Do Review Rubric

Use this before final acceptance for non-trivial plan execution.

## Verdict Format

The review artifact must contain exactly one terminal verdict line:

```text
Verdict: PASS
```

or:

```text
Verdict: FAIL
```

## PASS Conditions

- Functional completeness: every required plan task is completed or explicitly blocked.
- Acceptance criteria: task artifacts show criteria were met.
- Verification: planned checks passed, or skipped checks have concrete blockers and next actions.
- Scope discipline: touched files stay within writable scope or scope changes are documented.
- Regression risk: changed behavior has smoke, fixture, compile, lint, or manual evidence.
- Architecture simplicity: no speculative abstraction, needless configurability, hidden global state, or over-engineering.
- Context hygiene: raw logs/diffs/transcripts are quarantined into artifacts; final context cites paths and outcomes.
- Documentation: skill docs or references changed when workflow behavior changed.

## FAIL Conditions

- Missing task artifact, review artifact, final report, or verification evidence.
- Known functional gap, failing command, unresolved blocker, or untracked approval need.
- Redundant architecture that makes the skill harder to use or maintain.
- Validator accepts incomplete work, unclear errors, or false success.
- Edits outside writable scope without explicit justification.

Use `Verdict: FAIL` if any FAIL condition applies. Write rework guidance before fixing.
