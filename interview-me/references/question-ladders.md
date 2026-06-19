# Interview Question Ladders

Use the shortest ladder that fits. Ask one question at a time.

## Product / Feature

1. Who is the first user this must work for?
2. What painful moment triggers the need?
3. What would the user do differently if this succeeds?
4. What is the smallest v1 that proves value?
5. What good ideas are intentionally out of scope?
6. What metric or observable behavior proves done?

## Refactor

1. What pain does the current design create?
2. What behavior must stay identical?
3. Which APIs, files, data formats, or users are affected?
4. What risk must the refactor reduce?
5. What regression tests prove equivalence?
6. What is explicitly not being redesigned?

## Performance

1. What operation is too slow or expensive?
2. What baseline and target metric matter?
3. What workload, data size, or user path should be measured?
4. What tradeoffs are acceptable: memory, accuracy, freshness, complexity, cost?
5. How will before/after be measured?

## Bug

1. What is expected vs actual?
2. What is the smallest repro?
3. Who is affected and how severe is it?
4. When did it start or what changed?
5. What regression check prevents recurrence?

## UI / Design

1. Who is looking at this and what job are they trying to complete?
2. What should they notice first?
3. What brand, platform, accessibility, or device constraints bind the design?
4. What interaction or visual state proves the design works?
5. What visual directions are off-limits?

## Docs / Process

1. Who will use this document or workflow?
2. What decision or action should it enable?
3. What current confusion or failure does it remove?
4. What examples, commands, or checks must be included?
5. What belongs elsewhere?

## Vague-Term Probes

- "Scalable" -> "What exact load, data size, team size, or growth path must it handle?"
- "Robust" -> "Which failure must not happen, and what recovery is acceptable?"
- "Modern" -> "What user-visible or operational benefit do you expect?"
- "Clean" -> "What specific maintenance pain should disappear?"
- "AI agent" -> "What decision or action should it perform autonomously, and what must stay human-approved?"
- "Dashboard" -> "What decision should a viewer make after looking at it?"
