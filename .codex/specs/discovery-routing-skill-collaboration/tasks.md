# Codex2Codex Tasks: plan

Source plan: `/data/lcq/.codex/skills/.codex/plans/discovery-routing-skill-collaboration/plan.md`

## Wave 1

- [x] [coding] Task 1: Create shared Discovery Routing references | `idea-refine/references/discovery-routing.md`, `interview-me/references/discovery-routing.md`, `spec2plan/references/discovery-routing.md` | Verify: `rtk diff idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md spec2plan/references/discovery-routing.md` Output: `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-1-routing-reference.md`

## Wave 2

- [x] [coding] Task 2: Update idea-refine handoff instructions | `idea-refine/SKILL.md` | Verify: `rtk grep -n "Discovery Routing\\|interview-me\\|spec2plan" idea-refine/SKILL.md` Output: `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-2-idea-refine.md`
- [x] [coding] Task 3: Update interview-me handoff instructions | `interview-me/SKILL.md` | Verify: `rtk grep -n "Discovery Routing\\|idea-refine\\|spec2plan" interview-me/SKILL.md` Output: `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-3-interview-me.md`
- [x] [coding] Task 4: Update spec2plan collaboration gate | `spec2plan/SKILL.md` | Verify: `rtk grep -n "Discovery Routing\\|idea-refine\\|interview-me" spec2plan/SKILL.md` Output: `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-4-spec2plan.md`

## Wave 3

- [x] [devops] Task 5: Validate edited skill docs | `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-5-validation.md` | Verify: `rtk python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py idea-refine && rtk python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py interview-me && rtk python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py spec2plan && rtk git diff -- idea-refine/SKILL.md interview-me/SKILL.md spec2plan/SKILL.md idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md spec2plan/references/discovery-routing.md` Output: `.codex/specs/discovery-routing-skill-collaboration/artifacts/task-5-validation.md`

## Wave 4

- [x] [review] Task 6: Review collaboration semantics | `.codex/specs/discovery-routing-skill-collaboration/review.md` | Verify: `rtk grep -n "Route to idea-refine\\|Route to interview-me\\|Route to spec2plan\\|Avoid Loops" idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md spec2plan/references/discovery-routing.md` Output: `.codex/specs/discovery-routing-skill-collaboration/review.md`

## Wave 5: fix review findings
- [x] [coding] Fix review findings from `/data/lcq/.codex/skills/.codex/specs/discovery-routing-skill-collaboration/review.md` | `rtk grep -n "Route to idea-refine\|Route to interview-me\|Route to spec2plan\|Avoid Loops" ...` | Verify: rtk grep -n "Route to idea-refine\\|Route to interview-me\\|Route to spec2plan\\|Avoid Loops" idea-refine/references/discovery-routing.md interview-me/references/discovery-routing.md spec2plan/references/discovery-routing.md
