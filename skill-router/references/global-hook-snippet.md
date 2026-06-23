# Global Soft Hook Snippet

Add under the global `AGENTS.md` **Skill System** section only after explicit user approval.

```markdown
- When multiple skills/tools match the same request, or when routing involves stale routes, missing MCP tools, mode-gated tool calls, duplicate names, or parent/child skill overlap, use `skill-router` first to choose one primary route.
- Do not invoke `skill-router` for a single clear skill/tool match; route directly to the most specific applicable skill/tool.
- Treat `skill-router` decisions as advisory under current system/developer/user instructions, available tools, approval mode, and safety constraints.
```

Intent: soft-hook conflict cases without turning `skill-router` into a global bottleneck.
