# Task 2 — Implement route and toolchain scripts

- Status: COMPLETE
- Scope: `structural-edit/scripts/`
- Changed: `structural-edit/scripts/route_decision.py`, `structural-edit/scripts/prepare_structural_tools.py`, `structural-edit/scripts/self_check_structural_tools.py`, `structural-edit/scripts/manifest_report.py`, `structural-edit/scripts/validate_structural_routes.py`
- Verification:
  - `python3 structural-edit/scripts/prepare_structural_tools.py --list` → PASS
  - `python3 structural-edit/scripts/self_check_structural_tools.py --tool ast-grep --json` → PASS as readiness probe; reports missing local tool deterministically under `/data/lcq/.codex/tools/structural-edit`
  - `python3 structural-edit/scripts/manifest_report.py --summary` → PASS (`No prepared tools recorded.`)
  - `python3 structural-edit/scripts/validate_structural_routes.py` → PASS
- Notes:
  - Route classifier covers generator-owned, Python, JS/TS, JSON, YAML, Markdown, Java/OpenRewrite, strict fallback, unknown-file `block`.
  - Tool prep refuses system roots and records manifest metadata only in user-controlled roots.
  - Missing-tool behavior is explicit diagnostic, not silent downgrade.

