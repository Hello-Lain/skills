# Reviewer Dry-Review Fixtures

These fixtures exercise `reviewer` behavior. They are not product requirements.

## Fixture A: `idea-refine` Output

Artifact:
- Direction: Build a lab notebook assistant that turns raw experiment notes into reproducible ML experiment cards.
- Target user: PhD students running multimodal model experiments.
- Why now: local LLMs can summarize logs and configs cheaply.
- Core mechanism: parse notes, configs, and metrics; produce a card with hypothesis, setup, result, failure mode, and next run.
- Differentiator: focuses on reproducibility artifacts rather than generic note taking.
- MVP: CLI command over one experiment folder.
- Risks: messy notes, missing config files, hallucinated summaries.
- Not Doing: no team collaboration, no hosted SaaS, no automatic paper writing.

## Fixture B: Code Diff

```diff
diff --git a/auth.py b/auth.py
@@
-def is_expired(expiry, now):
-    return expiry < now
+def is_expired(expiry, now):
+    return expiry <= now
```

Context:
- Tokens expiring exactly at `now` must be rejected.
- Existing tests cover before and after `now`, but not equality.

## Fixture C: Research Idea

Artifact:
- Claim: A retrieval-augmented caption verifier can reduce hallucination in MLLM chart understanding.
- User/field: researchers evaluating chart question answering.
- Method: retrieve visually similar chart examples and ask a verifier model to check generated answers.
- Novelty claim: no one has combined retrieval and verifier models for chart QA.
- Dataset: use public chart QA datasets.
- Evaluation: accuracy and hallucination rate.
- Baselines: closed-book MLLM and RAG captioning.
- MVP: test on 200 examples.

## Fixture D: Plan Excerpt For Adversarial Review

Plan:
- Goal: add a new CLI command `sync-data`.
- Step 1: edit `cli.py`.
- Step 2: run `python tests.py`.
- Step 3: update README.
- Rollback: revert the files.
- Handoff: tell user it works.
