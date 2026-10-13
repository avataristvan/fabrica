# examples/agents/

A reference subagent definition that demonstrates wiring ai-mem's memory into a Claude
Code subagent explicitly. Nothing here is auto-installed or auto-registered — copy the
file into `~/.claude/agents/<name>.md` (user scope) or
`.claude/agents/<name>.md` (project scope), rename it, and adapt the body to your
agent's actual job.

| File | Description |
|---|---|
| `example-agent-with-memory.md` | Minimal template: ask the librarian before starting, deliver `record_candidates` in the `[retro]` block before finishing (agents never write records) |

The librarian, the archivist and `anchor-lint` ship with the plugin in `agents/` (as `ai-mem:librarian`, `ai-mem:archivist`, `ai-mem:anchor-lint`); they share one navigation reference, `reference/navigating_records.md`, which their texts name as `${CLAUDE_PLUGIN_ROOT}/reference/navigating_records.md`. Only the template below stays here.

## Why a template instead of automatic wiring

Earlier, ai-mem could auto-inject context into any subagent listed under
`inject_agents:` in `agents.yaml` — a central registry deciding, on your behalf, which
agents "know about" ai-mem. That's gone in favor of you deciding per agent, by
editing the agent's own file: if the two memory sections in the template are in an
agent's prompt, it uses ai-mem; if not, it doesn't. No separate config to keep in sync
with your agent roster.

`agents.yaml`'s `inject_agents` still exists for a narrower purpose: it lets
SessionStart *name* a custom subagent's `subagent.<name>` collection in its one routing
line (see `docs/reference/hooks.md`) — the actual asking (the `librarian`) and delivering (`record_candidates` in the `[retro]` block, integrated by the `archivist` via `/reflect`) is still the agent's own
step from the template below.

## Writing your own

See `docs/how-to/wire-skills-and-agents.md` for the full pattern (areas, who reads and writes, the `[retro]` block convention for orchestrator-spawned agents) and
`example-agent-with-memory.md` for a copy-pasteable starting point.
