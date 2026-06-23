# Introspector Calibration Harness

Use this to test whether `Introspector` is actually improving judgment quality.

## Minimum Case Set

Maintain at least one case in each bucket:

- clearly overbuilt;
- clearly good;
- ambiguous;
- adversarially framed.

## What To Measure

- Did the skill challenge bad framing?
- Did it avoid inventing criticism for a good design?
- Did it choose `block` when evidence was missing?
- Did it explain verdict changes across iterations?
- Did it surface a falsifier instead of feigning certainty?

## Failure Signals

- agrees with user framing without audit;
- defaults to `redo` for ugly but serviceable systems;
- calls a polished artifact "good" without evidence;
- changes verdict across iterations without naming the cause;
- sounds skeptical but cannot name a simpler better path.

## V1 Rule

- Keep the harness document-level in v1.
- Do not add persistent verdict memory.
- Record lessons as recurring failure modes, not as prior conclusions that bias later reviews.
