# Rework Guidance

- Evidence: `task1-verification.md` recorded `VERIFY_FAILED`; `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt` lacked `quality=verified`.
- Defect: Task 1 acceptance requires both `feature=enabled` and `quality=verified`, but only one required line exists.
- Impact: Final acceptance must remain `INCOMPLETE` until the missing line is added and verification passes.
- Required change: Add exactly one `quality=verified` line to the fixture.
- Writable scope: `/data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`
- Verification: `grep -qx 'feature=enabled' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt && grep -qx 'quality=verified' /data/lcq/.codex/skills/.codex/work/20260621-plan2do-capability-test/fixture/status.txt`
- Cycle: 1
