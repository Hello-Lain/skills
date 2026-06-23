# Introspector Validation

Run these checks for material updates.

## Deterministic Validators

```bash
python /data/lcq/.codex/skills/.system/skill-creator/scripts/quick_validate.py /data/lcq/.codex/skills/introspector
rg "block|falsifier|delta review|verdict stability|evidence acquisition|reviewer" /data/lcq/.codex/skills/introspector /data/lcq/.codex/skills/introspector/references
```

## Scenario Gate

Check at least these scenarios:

- a clearly overbuilt design should not get polite local patch advice;
- a clearly good design should not get fake skepticism;
- an ambiguous case should allow `block`;
- an iterative revision that changes verdict must explain the change cause.

Record RED and GREEN results in the production report.

## Reviewer Gate

- Route final acceptance through `reviewer` heavy by default.
- Use adversarial focus unless a narrower scope is explicitly justified.
- Reviewer agreement is necessary, not sufficient; keep evidence classes and falsifiers in the packet.

## Cleanup

- Do not leave placeholder scaffold text.
- Do not leave example resource files that are not used.
- Keep raw logs in workspace artifacts, not in the skill folder.
