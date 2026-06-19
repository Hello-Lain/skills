# Codex2Codex Tasks: plan

Source plan: `/data/lcq/.codex/skills/.spec2plan/deprecation-doc-cleanup/plan.md`

## Wave 1

- [x] [coding] Task 1: Expand skill entrypoint triggers and core rules | `deprecation-and-migration/SKILL.md` | Verify: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/deprecation-and-migration && rg -n "documentation|stale|duplicate|temporary|authoritative|merge" /data/lcq/.codex/skills/deprecation-and-migration/SKILL.md` Output: `.codex/specs/deprecation-doc-cleanup/artifacts/task-1-entrypoint.md`
- [x] [coding] Task 2: Add detailed documentation cleanup workflow | `deprecation-and-migration/references/upstream.md` | Verify: `rg -n "Documentation Lifecycle|authoritative|temporary|duplicate|delete gates|merge|archive" /data/lcq/.codex/skills/deprecation-and-migration/references/upstream.md` Output: `.codex/specs/deprecation-doc-cleanup/artifacts/task-2-reference.md`

## Wave 2

- [x] [coding] Task 3: Update skill UI metadata | `deprecation-and-migration/agents/openai.yaml` | Verify: `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/deprecation-and-migration && rg -n "doc|documentation|cleanup|deprecation|migration" /data/lcq/.codex/skills/deprecation-and-migration/agents/openai.yaml` Output: `.codex/specs/deprecation-doc-cleanup/artifacts/task-3-metadata.md`

## Wave 3

- [x] [review] Task 4: Review expanded skill behavior | `.codex/specs/deprecation-doc-cleanup/review.md` | Verify: `git -C /data/lcq/.codex/skills diff -- deprecation-and-migration/SKILL.md deprecation-and-migration/references/upstream.md deprecation-and-migration/agents/openai.yaml && python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/deprecation-and-migration` Output: `.codex/specs/deprecation-doc-cleanup/review.md`
