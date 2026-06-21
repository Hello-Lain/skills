# Debug Skill Report: apply-patch + edit-orchestration

## Verdict
- Impact: mixed
- Confidence: high
- One-line reason: `edit-orchestration` supplied high-quality route/tool gates, while `apply-patch` supplied precise patch grammar; split triggering caused duplication and occasional under-loading of the needed half.

## Evidence Used
- Skill files: `apply-patch/SKILL.md`, `apply-patch/agents/openai.yaml`, `edit-orchestration/SKILL.md`, `edit-orchestration/references/*.md`, `edit-orchestration/scripts/*.py`.
- Conversation / trace: recent edits repeatedly used `edit-orchestration` for route selection and still needed low-level patch grammar from `apply-patch`.
- Artifacts / diffs: current workspace diff for both skill folders.
- Commands / validation: `debug-skill/scripts/skill_audit_core.py --skill apply-patch --json`; `debug-skill/scripts/skill_audit_core.py --skill edit-orchestration --json`.
- External reuse sources: ast-grep, Aider, Comby, Plandex.
- Missing evidence: private session history outside current workspace was not mined.

## Execution Trace
1. Trigger: user requested merging `/data/lcq/.codex/skills/apply-patch` and `/data/lcq/.codex/skills/edit-orchestration`.
2. Skill instructions loaded: `debug-skill`, both target `SKILL.md` files, `skill-creator`, `deprecation-and-migration`, and relevant `edit-orchestration` references/scripts.
3. Decisions: keep `edit-orchestration` as canonical; retain `apply-patch` as compatibility shim to avoid breaking trigger metadata.
4. Actions: move patch grammar into `edit-orchestration/references/apply-patch.md`; update canonical skill body and metadata; shrink legacy skill.
5. Failures / friction: split skills created trigger ambiguity; `apply-patch` had precise grammar but no route/tool gate; `edit-orchestration` had route/tool gate but no local exact patch grammar.
6. Recovery: merge strengths into one canonical skill and preserve redirect.
7. Verification: quick skill validation and script compile.
8. Result: one canonical high-signal edit workflow with legacy compatibility.

## Effectiveness
- Quality: high after merge; route safety and patch precision now co-located.
- Efficiency: better; future edits load one canonical skill instead of two.
- Evidence use: high; current skill files and scripts inspected.
- Context handling: better; compatibility shim prevents duplicate long patch docs.
- Tooling: high; keeps existing helper preparation and self-check scripts.
- Verification: quick validation plus py_compile.
- User friction: lower; old `$apply-patch` still works as redirect.
- Reuse discipline: mature tools retained as selected-route options, not mandatory dependencies.

## Findings
- High: split trigger surface caused duplicate cognitive load. Evidence: `apply-patch` said use `edit-orchestration` for route choice, while `edit-orchestration` referenced `apply_patch` without inline grammar. Impact: agents may load two skills or miss one half.
- Medium: `apply-patch` lacked tool-preparation and diff gates. Evidence: no helper self-check or route matrix in `apply-patch/SKILL.md`. Impact: patch route could be selected for structural edits that need AST/codemod tools.
- Medium: `edit-orchestration` lacked exact apply_patch grammar. Evidence: fast path said use `apply_patch` but grammar lived elsewhere. Impact: malformed patch and visual-match recovery guidance required extra trigger.
- Low: deleting `apply-patch` would break existing skill metadata and user prompts. Evidence: search found explicit `apply-patch` references in other skills/docs. Impact: compatibility shim is safer than removal.

## Reuse Search
- Defect: route ambiguity, unsafe broad textual edits, missing pending-diff review, overbuilding custom tooling.

| Source project/repo | Source link | Mature signal | Borrowed idea | Reusable component/CLI/schema | Adoption mode | Target skill change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ast-grep | https://github.com/ast-grep/ast-grep | AST-based structural search/rewrite CLI | Use syntax-aware rewrite for repeated code patterns | `ast-grep` / `@ast-grep/cli` | direct | Keep structural rewrite route and self-check tooling | Not default for simple edits; too heavy for fast path |
| Aider | https://github.com/aider-ai/aider | terminal AI pair programming over local git repo | Use scoped agent-edit for complex multi-file natural-language edits | `aider-chat` CLI | direct | Keep agent-edit route with scope and diff gate | Not default; external agent can overreach |
| Comby | https://github.com/comby-tools/comby | structural search/replace across many languages | Lightweight structural rewrite concept | `comby` CLI | pattern-only/rejected direct | Inspires structural rewrite route | Not integrated now; install/distribution path not already self-checked |
| Plandex | https://github.com/plandex-ai/plandex | large-task AI coding agent; pending diff review concept | Review generated changes before apply | `plandex diff` concept | pattern-only | Keep review-before-apply route | Full runtime too broad for this skill |

- Search boundary: GitHub and upstream docs for mature structural rewrite, AI edit, and pending diff review tools.
- No mature component found: no better direct replacement for Codex `apply_patch` grammar inside current tool API; preserve it as a reference.
- Reuse-to-candidate mapping: canonical merged skill combines ast-grep/Aider direct options, Plandex review pattern, and apply_patch low-level grammar.

## Candidate Improvements
| Candidate | Target surface | Reuse source | Summary | Benefit | Risk | Fitness |
| --- | --- | --- | --- | --- | --- | --- |
| A | `edit-orchestration` + `apply-patch` | ast-grep, Aider, Plandex, apply_patch grammar | Canonical merge with compatibility redirect | High quality, high efficiency | Low | Best |
| B | Delete `apply-patch` entirely | none | Remove duplicate trigger | Lower context | High trigger breakage | Reject |
| C | Add Comby as new direct supported tool | Comby | Extend structural rewrite tools | More capability | Install/self-check burden | Defer |

## Recommendation
- Recommended action: merge into `edit-orchestration`, keep `apply-patch` as redirect.
- Target files: `edit-orchestration/SKILL.md`, `edit-orchestration/references/apply-patch.md`, `apply-patch/SKILL.md`, `agents/openai.yaml` metadata.
- Verification: quick skill validation and py_compile.
- Reuse rationale: mature components are route options or patterns, not mandatory load-time dependencies.
- Execute now: yes; user explicitly asked to optimize/merge.
