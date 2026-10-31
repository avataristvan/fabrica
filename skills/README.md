# skills/

This directory holds the skills of the ai-mem plugin; the plugin loads them, namespaced
as `fabrica:<skill>`. Your own skills go into `~/.claude/skills/` or the project's
`.claude/skills/`.

## What ships with the plugin

| Skill | Description |
|---|---|
| `reflect/SKILL.md` (`/fabrica:reflect`) | Standup at a context boundary: collect learnings, write the handoff (`FOCUS.md`, optionally `docs/handoff-<date>.md`) directly, and hand record candidates to the `fabrica:archivist` agent, whose integration report it shows. Writes no records itself. |
| `setup/SKILL.md` (`/fabrica:setup`) | Proposes the one-line hook-in at each real boundary of your teams, routing and session-start lines for CLAUDE.md, and a verdict per `mem doctor` Wiring finding. Applies only what you approve; writes no records. How-to: [Set up your teams and CLAUDE.md](../docs/how-to/set-up.md). |
| `handoff-protocol/SKILL.md` (`fabrica:handoff-protocol`) | The ai-mem protocol at a boundary: ask the librarian, check the work against the records it names, report `records_consulted` / `record_candidates` in the `[retro]` block. |

## Writing your own skills

A skill file is a Markdown file with YAML frontmatter:

```markdown
---
name: my-skill
description: "One-line description shown in /help"
---

Instructions for the agent...
```

Skills read memory through the `librarian` agent (situation plus the area path) and never write records: what should be kept goes to the orchestrator as plain-text record candidates, and `/fabrica:reflect` hands them to the `archivist`. The shared contract is the skill `handoff-protocol` (`skills/handoff-protocol/SKILL.md`); a skill adds one line at its boundary: "At this boundary follow the ai-mem handoff protocol (skill `fabrica:handoff-protocol`)." `/fabrica:setup` proposes it where it is missing.

See `examples/agents/` for the equivalent pattern applied to subagents.
