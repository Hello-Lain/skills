Salvaged-From-Worker: review-1

### Findings
Artifact write blocked by approval tooling (`apply_patch` rejected by auto-review provider error). Complete review body:

```markdown
Verdict: PASS

Findings:
- None.

Checks:
- Trigger coverage: PASS. `deprecation-and-migration/SKILL.md:3` expands invocation to documentation lifecycle cleanup, including stale, duplicate, temporary, redundant, process, result, and agent-generated docs while preserving authoritative records.
- Token discipline: PASS. `deprecation-and-migration/SKILL.md:8` keeps the entrypoint lean and delegates detailed workflow to `references/upstream.md`.
- Safety gates: PASS. `deprecation-and-migration/SKILL.md:16`, `deprecation-and-migration/SKILL.md:17`, and `deprecation-and-migration/SKILL.md:18` require classification, merge-before-delete, and reference/consumer verification. `deprecation-and-migration/references/upstream.md:196` through `deprecation-and-migration/references/upstream.md:204` adds explicit delete gates.
- Broad deletion risk: PASS. No broad deletion behavior was introduced without gates; `deprecation-and-migration/references/upstream.md:198` says all delete gates must pass, and `deprecation-and-migration/references/upstream.md:204` blocks sweeping broad directories or unrelated histories.
- Agent docs handling: PASS. `deprecation-and-migration/references/upstream.md:206` through `deprecation-and-migration/references/upstream.md:213` separates temporary process docs from durable result docs and preserves unique decisions.
- UI metadata: PASS. `deprecation-and-migration/agents/openai.yaml:3` and `deprecation-and-migration/agents/openai.yaml:4` reflect the expanded scope concisely.
- Validation: PASS. Ran `git -C /data/lcq/.codex/skills diff -- deprecation-and-migration/SKILL.md deprecation-and-migration/references/upstream.md deprecation-and-migration/agents/openai.yaml`; scoped diff shows only the intended three files. Ran `python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/deprecation-and-migration`; output: `Skill is valid!`.

Residual risks:
- The frontmatter trigger is broader than before, so it may fire on some ordinary documentation cleanup requests. This is consistent with the spec and mitigated by the preservation language in `deprecation-and-migration/SKILL.md:3`.
```

### Verification
- See worker result; artifact was salvaged by run_wave.py after worker write failure.
