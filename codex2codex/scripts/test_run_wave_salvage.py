#!/usr/bin/env python3
from __future__ import annotations

import unittest

import run_wave


class RunWaveSalvageTest(unittest.TestCase):
    def test_review_artifact_body_prefers_artifact_body_marker(self) -> None:
        result = """Blocked writing artifact: apply_patch failed.

ARTIFACT_BODY:
# Review

Verdict: PASS

## Findings

No blocking findings.

## Verification

- grep passed
"""

        artifact = run_wave._review_artifact_body("review-1", result)

        self.assertIn("Verdict: PASS", artifact)
        self.assertIn("## Findings", artifact)
        self.assertNotIn("Blocked writing artifact", artifact)
        self.assertNotIn("ARTIFACT_BODY:", artifact)

    def test_review_artifact_body_strips_fenced_marker_body(self) -> None:
        result = """Unable to write output artifact.

ARTIFACT_BODY:
```markdown
# Review

Verdict: PASS

## Findings

No blocking findings.

## Tests

- validate_wave passed
```
"""

        artifact = run_wave._review_artifact_body("review-1", result)

        self.assertIn("Verdict: PASS", artifact)
        self.assertIn("## Tests", artifact)
        self.assertNotIn("```", artifact)
        self.assertNotIn("Unable to write output artifact", artifact)

    def test_review_artifact_body_strips_legacy_fenced_wrapper(self) -> None:
        result = """Blocked writing artifact because tool approval failed.

Complete review body:

```markdown
# Review

Verdict: PASS

## Findings

No blocking findings.

## Verification

- validate_wave passed
```
"""

        artifact = run_wave._review_artifact_body("review-1", result)

        self.assertIn("Verdict: PASS", artifact)
        self.assertIn("## Verification", artifact)
        self.assertNotIn("Blocked writing artifact", artifact)
        self.assertNotIn("Complete review body", artifact)

    def test_implementation_artifact_body_prefers_marker(self) -> None:
        result = """Could not write artifact.

ARTIFACT_BODY:
# Implementation

## Summary

- Updated worker brief fallback.

## Verification

- unit tests passed

## Risks

- None
"""

        artifact = run_wave._implementation_artifact_body("coding-1", result)

        self.assertIn("## Summary", artifact)
        self.assertIn("## Verification", artifact)
        self.assertNotIn("Could not write artifact", artifact)
        self.assertNotIn("ARTIFACT_BODY:", artifact)


if __name__ == "__main__":
    unittest.main()
