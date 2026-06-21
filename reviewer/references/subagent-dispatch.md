# Subagent Dispatch

Use this when review is heavy, mandatory isolation is requested, or subagent tooling is otherwise required by the packet.

## Dispatch Packet

Send only:

- review goal;
- artifact path or excerpt;
- expected artifact type and lifecycle stage;
- source-of-truth paths;
- coordinator working directory from `pwd`;
- for local workspace artifacts: both cwd-relative path and absolute path when available;
- local artifact existence evidence already checked by the coordinator when available;
- applicable local rules and skill contracts;
- allowed commands or no-command instruction;
- review focus and `max_findings`;
- review mode and route;
- output schema requirement;
- readiness evidence for plan2do/skill-production reviews, such as `python3 plan2do/scripts/pre_review_ready.py <plan-workspace> --stage draft --require-production-report --require-final-report`;
- read-only instruction;
- no nested subagents instruction;
- cleanup requirement: archive or kill the reviewer subagent after report collection when supported;
- output artifact path when saving is requested.

Do not send:

- full main-thread conversation;
- private or irrelevant user context;
- intended answer or expected verdict;
- raw long logs unless the log itself is the artifact;
- hidden diagnosis from the coordinator.

## Prompt Skeleton

```text
Use reviewer behavior to review the artifact described in this packet.
Stay read-only. Do not edit files, git state, config, or generated outputs.
Do not spawn nested reviewer subagents.
You are already the isolated reviewer when you receive this packet; do not launch another reviewer even for heavy mode.
If the packet concerns plan2do or skill-production execution, treat missing readiness evidence as a review finding unless the packet records a deliberate partial-review reason.
Use the listed sources as authority. Treat summaries as navigation only.
Before reporting a local artifact missing, run or request `pwd` plus path existence checks for the cited cwd-relative and absolute path forms when commands are allowed.
If commands are not allowed, cite the exact path form supplied by the packet and mark the missing-artifact finding as unverified by command.
Any missing local artifact finding must name the checked cwd, cwd-relative path, absolute path when supplied, and check result.
Derive a rubric before findings.
Return the Review Report Template shape with exactly one top-level Verdict: PASS, REVISE, or BLOCK.

Packet:
<compact packet>
```

After report collection, the coordinator must archive or kill the reviewer subagent when supported and record cleanup status. Do not cancel or archive a reviewer that is still normally working.

## Health Checks And Abort

Set a coordinator health-check policy before dispatch.

- Lite inline: no subagent.
- Mandatory-isolation lite: if the subagent appears abnormal, poll exactly 2 times, 45 seconds per poll.
- Heavy subagent: if the subagent appears abnormal, poll exactly 2 times, 45 seconds per poll.
- Multi-subagent: if a launched reviewer appears abnormal, poll that reviewer at most 2 times, 45 seconds per poll, unless the user explicitly accepts more diagnostic cost.

A transient wait, provider fluctuation, or temporary network interruption is not a valid reason to downgrade a heavy or mandatory-isolation review to inline review while the subagent remains healthy or making progress.

Poll only after an abnormal signal:

- no status update or visible activity for an unexpectedly long interval;
- status API is ambiguous or contradictory;
- permission, tool, provider, or network anomaly interrupts progress;
- repeated same output or context/tooling loop;
- scope broadens beyond the packet;
- read-only or no-nested-subagent rule is violated.

If the reviewer subagent is `running` with new activity or plausible progress, keep waiting. Do not count healthy running time against the abnormal diagnostic policy. Do not cancel or archive it solely because two 45-second waits elapsed.

If the reviewer remains abnormal after the 2 x 45s diagnostic policy:

- cancel the run when cancel tooling exists and cancellation is safer than leaving it active;
- archive or kill the subagent immediately after cancel or confirmed failure;
- record `Cleanup: archive after cancel`, `Cleanup: kill after cancel`, or `Cleanup: unavailable with reason`;
- keep any partial transcript out of main context;
- relaunch only with a narrower packet after cleanup, or return `BLOCK` with the abnormal-state reason;
- do not use inline fallback unless the route is reclassified for a non-wait reason such as user-approved scope reduction or unavailable subagent tooling before launch.

## Coordinator Checks

Before presenting results, the coordinator checks:

- verdict matches finding severities;
- critical and major findings cite evidence;
- missing local artifact findings cite the checked cwd and path form;
- revision instructions are concrete;
- skipped validators have reasons;
- report states mode as `lite`, `heavy`, or `blocked`;
- report states route as `inline`, `subagent`, `multi-subagent`, or `blocked`;
- report records cleanup status when a subagent was launched;
- no raw transcript or irrelevant private context leaked into output;
- saved reports pass `python3 reviewer/scripts/validate_review_report.py <report.md>`.

If the reviewer report fails these checks, request one repair from the reviewer or return `BLOCK` with the formatting defect.

## Route Selection

- `inline`: default for lite reviews.
- `subagent`: default for heavy reviews.
- `multi-subagent`: use for broad high-risk review needing independent lenses such as correctness, security, performance, architecture, or research feasibility.
- `blocked`: use when mandatory isolation or required evidence is unavailable.

## Cleanup

After receiving the synthesized report:

- archive the reviewer subagent when archive tooling is available;
- kill the reviewer subagent when archive is unavailable or ineffective and kill tooling is available;
- record `Cleanup: archive`, `Cleanup: kill`, or `Cleanup: unavailable with reason`;
- keep only the synthesized report in the main context, not raw transcript streams.
