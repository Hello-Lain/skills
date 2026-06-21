# Debug Skill Report Template

Use this stable structure for every skill audit. Keep raw logs, long diffs, and external pages out of the report; cite paths, commands, URLs, or short excerpts.

## Trace Mode Template

Use this compact artifact during or immediately after a task. It captures trajectory evidence without deep audit overhead.

```markdown
# Debug Skill Trace: <skill or chain>

- Mode: trace
- Skill(s):
- Task:
- Trigger:
- Loaded instructions:
- Decisions:
- Actions:
- Failures / friction:
- Recovery:
- Validators:
- Outcome:
- Optimization hints:
- Redaction: <none|applied>
- Human approval required before edits: yes
```

Trace mode does not recommend edits by itself. Convert to deep audit mode before making candidate recommendations.

## Deep Audit Template

```markdown
# Debug Skill Report: <skill>

## Verdict
- Impact: net-positive | net-negative | mixed | inconclusive
- Confidence: high | medium | low | blocked
- One-line reason:

## Evidence Used
- Skill files:
- Conversation / trace:
- Artifacts / diffs:
- Commands / validation:
- External reuse sources:
- Missing evidence:

## Execution Trace
1. Trigger:
2. Skill instructions loaded:
3. Decisions:
4. Actions:
5. Failures / friction:
6. Recovery:
7. Verification:
8. Result:

## Effectiveness
- Quality:
- Efficiency:
- Evidence use:
- Context handling:
- Tooling:
- Verification:
- User friction:
- Reuse discipline:

## Findings
- <severity>: <finding>. Evidence: <path/trace>. Impact: <task/user impact>.

## Reuse Search
- Defect:

| Source project/repo | Source link | Mature signal | Borrowed idea | Reusable component/CLI/schema | Adoption mode | Target skill change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | direct/adapted/pattern-only/rejected | | |

- Search boundary:
- No mature component found:
- Reuse-to-candidate mapping:

## Candidate Improvements
| Candidate | Target surface | Reuse source | Summary | Benefit | Risk / maintenance cost | Fitness / safety |
| --- | --- | --- | --- | --- | --- | --- |
| A | | | | | | |
| B | | | | | | |
| C | | | | | | |

## Promotion Gates
- Evidence sufficient:
- Real user-visible impact:
- Observable behavior improvement:
- Constraints pass:
- Rollback clear:
- Human approval before execution:

## Recommendation
- Recommended action:
- Target files:
- Verification:
- Reuse rationale:
- Execute now: no; requires explicit user approval.
```

Verdict rules:

- `net-positive`: evidence shows the skill improved real task quality or reduced risk more than it added overhead.
- `net-negative`: evidence shows the skill caused avoidable failure, wrong action, major overhead, or poor recommendation.
- `mixed`: useful in some steps but harmful or inefficient in others.
- `inconclusive`: evidence is insufficient, conflicting, or unavailable.
