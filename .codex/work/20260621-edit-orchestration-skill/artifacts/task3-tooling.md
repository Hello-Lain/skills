# Task 3: Tool Preparation And Self-Check Scripts

- Status: complete
- Files changed:
  - `edit-orchestration/scripts/prepare_edit_tools.py`
  - `edit-orchestration/scripts/self_check_edit_tools.py`
  - `edit-orchestration/references/tooling.md`
- Supported tool ids:
  - `ast-grep`
  - `aider`
  - `jscodeshift`
  - `openrewrite`
- Default install root: `${CODEX_HOME:-~/.codex}/tools/edit-orchestration`
- Manifest path: `<root>/manifest.json`

## Verification

- `python3 edit-orchestration/scripts/prepare_edit_tools.py --help` -> exit 0
- `python3 edit-orchestration/scripts/self_check_edit_tools.py --help` -> exit 0
- `python3 edit-orchestration/scripts/prepare_edit_tools.py --list` -> listed `ast-grep`, `aider`, `jscodeshift`, `openrewrite`
- `python3 -m py_compile edit-orchestration/scripts/prepare_edit_tools.py edit-orchestration/scripts/self_check_edit_tools.py` -> exit 0
- `python3 edit-orchestration/scripts/prepare_edit_tools.py --check-only --tool ast-grep --root <tmp> --json` -> exit 1 because `ast-grep` is not installed; this is expected fail-fast behavior.
- Check-only root test: `test ! -e <tmp>` returned 0, proving check-only did not create the root.

## Rework

- Initial self-check treated `/usr/bin/sg` as a possible ast-grep alias. That command is Linux shadow-utils `sg`, not ast-grep.
- Fix: `self_check_edit_tools.py` now accepts `sg` only from the user-level npm install path, while PATH lookup uses `ast-grep` only.
