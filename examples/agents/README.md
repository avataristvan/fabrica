# examples/agents/

Reference subagent definitions that demonstrate wiring ai-mem's memory into a Claude
Code subagent explicitly. Nothing here is auto-installed or auto-registered — copy the
file you want into `~/.claude/agents/<name>.md` (user scope) or
`.claude/agents/<name>.md` (project scope), rename it, and adapt the body to your
agent's actual job.

| File | Description |
|---|---|
| `example-agent-with-memory.md` | Minimal template: pull prior experience before starting, store transferable learnings before finishing |
| `librarian.md` | Prototype ("der Bibliothekar"): cheap read-only retrieval agent, judgment-based catalogue scan instead of similarity ranking, never writes to memory. Fixed call points: `/chunk-plan` (mandatory, before decomposing) and the workspace CLAUDE.md (before architecture decisions). Registered by symlinking this file to `~/.claude/agents/librarian.md` so the source stays the single copy. See repo.ai-mem `todo_bibliothekar_haiku_retrieval_agent_2026_09_25` and the measurement in `scripts/eval_pull/README.md` ("Librarian arm"). |

## Why a template instead of automatic wiring

Earlier, ai-mem could auto-inject context into any subagent listed under
`inject_agents:` in `agents.yaml` — a central registry deciding, on your behalf, which
agents "know about" ai-mem. That's gone in favor of you deciding per agent, by
editing the agent's own file: if the two memory sections in the template are in an
agent's prompt, it uses ai-mem; if not, it doesn't. No separate config to keep in sync
with your agent roster.

`agents.yaml`'s `inject_agents` still exists for a narrower purpose: it lets
SessionStart *name* a custom subagent's `subagent.<name>` collection in its one routing
line (see `docs/hooks.md`) — the actual pulling and storing is still the agent's own
`mem_query`/`mem_add` calls from the template below.

## Writing your own

See `docs/skill-agent-integration.md` for the full pattern (collection routing, type
tags, the `[retro]` block convention for orchestrator-spawned agents) and
`example-agent-with-memory.md` for a copy-pasteable starting point.
