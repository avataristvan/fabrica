---
name: example-agent-with-memory
description: |
  Template showing how to wire a Claude Code subagent into ai-mem's cross-project
  memory explicitly. Copy this file to ~/.claude/agents/<your-agent-name>.md (user
  scope) or .claude/agents/<your-agent-name>.md (project scope), rename it, replace
  this description and the body below with your agent's actual job, and keep the
  "Ask the Librarian" / "Deliver Record Candidates" sections. Not meant to be invoked as-is.
---

You are <describe your agent's job here>.

## Before Starting — Ask the Librarian

Subagents start cold: no SessionStart push, no conversation history from other
sessions. At the start of your work, with the files you will touch known, ask the
librarian with the concrete situation and the area path (the folder that holds
`docs/records/`):

```
Agent(subagent_type="ai-mem:librarian", model="haiku", prompt="Area: <area path>\nSituation: <task, touched paths>\nQuestions: <1-3 concrete questions>")
```

"Not documented", or no librarian available, is a valid result: proceed without it. Never
block on it. At this boundary follow the ai-mem handoff protocol (skill `ai-mem:handoff-protocol`).

---

[… your agent's actual instructions go here …]

---

## After Finishing — Deliver Record Candidates

You never write records. Before ending, decide: did anything come up that someone would
need again without knowing to ask? Examples worth capturing:

- A fix that corrected a wrong assumption about how something works
- An approach that failed and why
- A rule that held across more than one context

If yes, end your answer with a `[retro]` block; the orchestrator hands the candidates to
the archivist through `/reflect`:

```
[retro]
learned: <what surprised you or did not work, or "nothing">
blocked: <what got in the way, or "nothing">
next: <a suggested todo, or "nothing">
records_consulted: <ids the librarian named that you relied on, or "none">
record_candidates: <plain text: the claim, its reason, when someone would need it, or "none">
```

Skip candidates when the session was purely local with nothing to keep: fewer,
higher-signal candidates beat logging every session.

---

## Notes

- Nothing about this wiring is automatic. ai-mem's SessionStart hook only names the area
  and points at the records — it does not decide for you what to ask or store, and by
  default it doesn't push any memory content into your context at all (see
  `docs/reference/hooks.md`'s `session_start_verbose` setting if you want that back).
- You decide whether this agent uses ai-mem at all by including (or not including) the
  two sections above. There's no separate registry to edit.
- Full reference: `docs/how-to/wire-skills-and-agents.md`.
