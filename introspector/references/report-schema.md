# Introspector Report Schema

Use this shape for every final output artifact.

```markdown
# Introspector Review

- Artifact Type:
- Confidence: Low|Medium|High
- Verdict: keep|trim|merge|redo|pause|change-direction|block

## Objective Extraction
- Reviewed artifact:
- Root objective:
- Decision question:

## Framing Audit
- Judgment:
- Direct evidence:
- Inference:

## Evidence Acquisition
- Sources loaded:
- Why they were needed:
- Remaining gaps:

## Provisional Verdict
- Provisional verdict:
- Reason:

## Strongest Defense Of Current Design
- 

## Alternative Comparison
### Option A
- Decision:
- Why:

### Option B
- Decision:
- Why:

### Option C
- Decision:
- Why:

## Keep / Remove / Redesign
### Keep
- 

### Remove
- 

### Redesign
- 

## Verification Questions
- 

## Evidence Classes
- Direct evidence:
  - 
- Inference:
  - 
- Uncertainty:
  - 

## Falsifier
- 

## Delta Review
- Revision effect:
- New complexity:
- Net result:

## Verdict Stability
- Previous verdict:
- Current verdict:
- Change cause:

## Final Verdict
- Verdict:
- Judgment:
- Best available path:

## Risks
- 
```

Rules:

- Include exactly one top-level verdict line.
- Use `block` when the report cannot justify a stable optimization claim.
- Keep `Delta Review` and `Verdict Stability` even when the answer is "not applicable"; state why.
- Never present inference as direct evidence.
