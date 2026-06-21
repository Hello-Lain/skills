# Review: reviewer v2 validator/report schema

- Artifact Type: code+template review
- Confidence: High
- Review Mode: heavy
- Review Route: subagent
- Verdict: REVISE

## Review Basis
- Goal: compact heavy forward-test of reviewer v2 validator/report schema.
- Artifact: `/data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py` and `/data/lcq/.codex/skills/reviewer/references/review-report-template.md`
- Sources: `/data/lcq/.codex/skills/.codex/work/20260621-reviewer-v2/spec.md`, `/data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py`, `/data/lcq/.codex/skills/reviewer/references/review-report-template.md`, `/data/lcq/.codex/skills/reviewer/SKILL.md`
- Constraints: read-only; no file/git/config edits; no subagents spawned by the reviewer; inspected only supplied sources.
- Validators: `python3 reviewer/scripts/validate_review_report.py --self-test` passed; `python3 -m py_compile reviewer/scripts/validate_review_report.py` passed.
- Cleanup: archive (agent `590aa8b2-0abd-4023-a879-26fd87f77e39`)

## Rubric
- Required v2 sections: validator must require actual section headings and required header fields from the template.
- Top-level verdict ambiguity: template and validator must distinguish the single top-level verdict from alignment/quality results.
- Severity/evidence checks: validator must reject unsupported severities, missing major/critical evidence, and PASS with major/critical findings.
- Local path citation checks: validator must reject missing local source/evidence paths unless that specific path is clearly marked missing or unavailable.
- Lite/heavy route semantics: skill/template must document lite, heavy, mandatory-isolation, fallback, transcript, and cleanup behavior clearly enough for agents to execute.

## Mode Decision
- Route: heavy
- Reason: requested heavy isolated review of code plus schema behavior with validator edge cases.
- Packet: supplied goal, constraints, focus areas, four source files, and two allowed commands.
- Raw transcript handling: omitted

## Alignment Result
- Result: REVISE
- Reason: The implementation covered the core v2 shape and passed its self-test, but local-path validation and required-section validation had material false-pass/false-fail cases against the spec at review time.

## Quality Result
- Result: REVISE
- Reason: The schema was concise and route semantics were mostly clear, but the validator needed tighter parsing before it was reliable as a deterministic gate.

## Findings
- [major] Command evidence with a path can be falsely rejected as a missing local path
  Evidence: `/data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py` `_extract_local_paths`; `/data/lcq/.codex/skills/reviewer/references/review-report-template.md` Findings rule says evidence may be a command.
  Criterion: Local path citation checks must reject missing local paths, not valid command evidence.
  Impact: A valid finding such as an evidence command containing `reviewer/scripts/validate_review_report.py --self-test` can be parsed as one nonexistent path including the command prefix/arguments, causing a false validation failure.
  Fix Type: patch current artifact
  Revision: In backtick extraction, distinguish command strings from standalone paths, or tokenize command evidence and validate only path-like tokens that are actually cited as paths.

- [major] Missing-path exemptions apply to the whole Sources/Evidence block instead of the specific missing path
  Evidence: `/data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py` `validate_report` uses `allow_missing` for the entire block when any marker like `missing` or `unavailable` appears.
  Criterion: Missing local source paths must be rejected unless they are explicitly marked missing or unavailable.
  Impact: One missing/unavailable marker can suppress existence checks for every path in that source or evidence block, allowing unrelated nonexistent paths to pass.
  Fix Type: patch current artifact
  Revision: Apply missing/unavailable allowance per extracted path or per line, and require the marker to describe the same cited path.

- [major] Required section validation can be satisfied by non-heading text
  Evidence: `/data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py` `for section in REQUIRED_SECTIONS: if section not in text`; `/data/lcq/.codex/skills/reviewer/references/review-report-template.md` requires concrete v2 section order.
  Criterion: Required v2 sections must be present as report sections.
  Impact: A malformed report can include `## Rubric` or another required label inside prose or a code block and satisfy the required-section check without having the actual heading.
  Fix Type: patch current artifact
  Revision: Check required sections against parsed lines with exact heading matches, preferably preserving order.

- [minor] Header enum validation is looser than the template contract
  Evidence: `/data/lcq/.codex/skills/reviewer/scripts/validate_review_report.py` accepts lowercase verdicts via `re.IGNORECASE` and only checks that Confidence exists; `/data/lcq/.codex/skills/reviewer/references/review-report-template.md` specifies `PASS|REVISE|BLOCK` and `Low|Medium|High`.
  Criterion: Deterministic schema validation should reject malformed report values.
  Impact: Reports outside the documented schema can pass, reducing the validator's usefulness as a strict forward-test.
  Fix Type: patch current artifact
  Revision: Enforce exact verdict casing and validate Confidence against `Low`, `Medium`, or `High`.

## Recheck Plan
- Run `python3 reviewer/scripts/validate_review_report.py --self-test`.
- Run `python3 -m py_compile reviewer/scripts/validate_review_report.py`.
- Add or manually exercise negative cases for command evidence with path arguments, missing marker scoped to only one path, required heading text inside prose/code, lowercase verdict, and invalid Confidence.

## Residual Risks
- The supplied packet did not include `reviewer/references/subagent-dispatch.md` or plan2do files, so cleanup and plan2do documentation implementation were judged only from the spec and `reviewer/SKILL.md`, not from those omitted artifacts.
