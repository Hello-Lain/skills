# Review Report Template

Use this v2 section order for final reviewer output. The labels `Review Mode`, `Review Route`, and top-level `Verdict` are machine-validated.

```markdown
# Review: <artifact name>

- Artifact Type: <type>
- Confidence: <Low|Medium|High>
- Review Mode: <lite|heavy|blocked>
- Review Route: <inline|subagent|multi-subagent|blocked>
- Verdict: <PASS|REVISE|BLOCK>

## Review Basis
- Goal: <source goal>
- Artifact: <path or description>
- Sources: <paths/contracts/commands inspected>
- Constraints: <binding constraints>
- Validators: <commands run or not run with reason>
- Cleanup: <archive|kill|not launched|unavailable with reason>

## Rubric
- <criterion>: <pass condition>

## Mode Decision
- Route: <lite|heavy|blocked>
- Reason: <why this route was chosen>
- Packet: <what was sent or used>
- Raw transcript handling: <omitted|artifact path|not applicable>

## Alignment Result
- Result: <PASS|REVISE|BLOCK>
- Reason: <one or two lines>

## Quality Result
- Result: <PASS|REVISE|BLOCK>
- Reason: <one or two lines>

## Findings
- [<severity>] <title>
  Evidence: <path, section, command, or missing evidence>
  Criterion: <rubric/source rule violated>
  Impact: <why it matters>
  Fix Type: <patch current artifact|revise upstream artifact|rerun upstream skill|ask user|stop>
  Revision: <concrete instruction>

## Recheck Plan
- <what to inspect or run after revision>

## Residual Risks
- <remaining uncertainty or "None known">
```

Rules:

- Include exactly one top-level `Verdict:` line.
- Use `PASS`, `REVISE`, or `BLOCK` for top-level verdict and result values.
- Do not use `Verdict:` under `Alignment Result` or `Quality Result`; use `Result:`.
- Validate saved reports with `python3 reviewer/scripts/validate_review_report.py <report.md>`.
- List critical and major findings before minor findings.
- Omit `nit` findings unless the user asks for polish.
- If there are no findings, write `Findings: None`.
- If validators are skipped, state the exact blocker or why a manual review is sufficient.
- If local source paths are cited as evidence, they must exist or be explicitly marked missing/unavailable.
