---
name: example-agent-with-memory
description: |
  Template showing how to wire a Claude Code subagent into ai-mem's cross-project
  memory explicitly. Copy this file to ~/.claude/agents/<your-agent-name>.md (user
  scope) or .claude/agents/<your-agent-name>.md (project scope), rename it, replace
  this description and the body below with your agent's actual job, and keep the
  "Prior Experience" / "Store Learnings" sections. Not meant to be invoked as-is.
---

You are <describe your agent's job here>.

## Before Starting — Pull Prior Experience

Subagents start cold: no SessionStart push, no conversation history from other
sessions. If ai-mem is installed, pull relevant cross-project experience yourself
before planning:

```
mem_query(collection="subagent.<your-agent-name>", query="<summary of the task>", n_results=3)
```

If the collection is empty, the query errors (MCP server not configured), or nothing
comes back relevant, proceed without it — this is a pull, not a dependency. Never block
on ai-mem being available.

Project-specific context (architecture, conventions, current focus) lives in a separate
collection — query it too if the task touches a specific repo:

```
mem_query(collection="repo.<project-name>", query="<summary of the task>", n_results=3)
```

---

[… your agent's actual instructions go here …]

---

## After Finishing — Store Transferable Learnings

Before ending, decide: did anything come up that would apply on a *different* project
too — not just this one? Examples worth capturing:

- A fix that corrected a wrong assumption about how something works
- An approach that failed and why (store as an anti-pattern, not a pattern)
- A rule that held across more than one context

If yes, write it back to your own collection:

```
mem_add(
    documents=["Rule: <the rule>\nWhen: <context it applies to>\nWhy: <what it prevents>"],
    collection="subagent.<your-agent-name>",
    type="pattern",   # or "anti-pattern" (use Tried:/Failed because:/Instead: structure) or "feedback"
    ids=["<your-agent-name>_<short-slug>"],
)
```

Skip this step if the session was purely project-specific with nothing transferable —
storing everything defeats the point of a curated knowledge base. When in doubt, prefer
fewer, higher-signal entries over logging every session.

---

## Notes

- Nothing about this wiring is automatic. ai-mem's SessionStart hook only announces
  which collection to use — it does not decide for you what to query or store, and by
  default it doesn't push any memory content into your context at all (see
  `docs/hooks.md`'s `session_start_verbose` setting if you want that back).
- You decide whether this agent uses ai-mem at all by including (or not including) the
  two sections above. There's no separate registry to edit.
- Full reference: `docs/skill-agent-integration.md`.
