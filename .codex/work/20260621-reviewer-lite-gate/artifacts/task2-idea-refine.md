# Task 2 Execution

- Task: Patch `idea-refine` reviewer-lite gate.
- Context pack: `.codex/work/20260621-reviewer-lite-gate/artifacts/context-wave1.md`
- Changed files: `idea-refine/SKILL.md`
- Acceptance: mandatory exit gate, direction-only scope, save confirmation, and routing handoff remain intact.
- Verification: `git diff --check -- reviewer idea-refine interview-me spec2plan plan2do .codex/work/20260621-reviewer-lite-gate` passed.
- Verification: `rg -n "reviewer-lite|REVISE|BLOCK|lite-gate-integration" idea-refine/SKILL.md` finds the consumer hook.
- Notes: reviewer lite runs only after the mandatory exit gate passes.
