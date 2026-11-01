# How to wire skills and agents into ai-mem

How to wire Claude Code skills and agents into the records, so they use what earlier sessions decided instead of starting cold. The one rule: **reads go through the librarian, writes go through the archivist.** A skill or agent never writes records itself.

---

## Core concepts

### Areas and kinds

Knowledge lives in record files under the nearest `docs/records/` of the work (an "area"; `mem context` prints it). Kinds: decisions (`domain`, `pattern`, `anti-pattern`), learnings, todos, `user`. State is `FOCUS.md` and `docs/handoff-*.md`, written by the orchestrator through `/reflect`. Format: [record format](../reference/record-format.md). Reading procedure: `reference/navigating_records.md`. The reasoning behind the roles: [Organisational memory](../explanation/organisational-memory.md).

### Who reads, who writes

| Role | Does |
|---|---|
| any skill or agent | asks the `librarian` (read-only) at a boundary; delivers `record_candidates` in its `[retro]` block |
| orchestrator | `/reflect` writes the handoff and hands all candidates to the `archivist` |
| `archivist` | decides new / update / supersede / confirm / contradict, area, `perspective:`, `cue:`, edges; writes only through the `mem` CLI |
| user | may write or edit records by hand; the archivist adopts them |

### The loop

```
Boundary (chunk start, planning, review handoff) -> ask the librarian (situation + area path)
      |
Work
      |
End of the work -> [retro] with records_consulted + record_candidates
      |
/reflect -> handoff (state) + candidates to the archivist
```

The shared contract for the boundary step is the skill `handoff-protocol` (`skills/handoff-protocol/SKILL.md`, shipped by the plugin as `fabrica:handoff-protocol`). A team file adds one line at each boundary: "At this boundary follow the ai-mem handoff protocol (skill `fabrica:handoff-protocol`)." `mem doctor` (Wiring) lists the teams that lack it, and `/fabrica:setup` proposes the line at each real boundary ([Set up your teams and CLAUDE.md](set-up.md)).

---

## The skill pattern

Skills run in the orchestrator context. At the moment the skill would otherwise read or store memory:

```markdown
At this boundary follow the ai-mem handoff protocol (skill `fabrica:handoff-protocol`).

Ask the librarian with the situation and the area path:

Agent(subagent_type="fabrica:librarian", model="haiku", prompt="Area: <area path>\nSituation: ...\nQuestions: ...")

"Not documented" is a valid result: proceed without it.

At the end, name what should become a record as plain-text candidates for /reflect.
```

Name an observable moment ("before drafting the first script"), not a category ("for feature work"): a trigger that needs classifying the session first does not fire (`learning_trigger_must_name_observable_moment_2026_10_10`).

**Reference implementation:** `skills/reflect/SKILL.md` (the /reflect ritual itself).

---

## The agent pattern

Agents start cold: no conversation history and no memory content pushed at session start (SessionStart names the area and points at the records). Compensate in the agent's own prompt (`~/.claude/agents/<name>.md`):

- at the start of the work, when the files are known: ask the librarian (as above);
- at the end: the `[retro]` block below.

**The `[retro]` block**

```
[retro]
learned: <what surprised you or did not work, or "nothing">
blocked: <what got in the way, or "nothing">
next: <suggested todo, or "nothing">
records_consulted: <ids that carried a decision or a finding, or "none">
record_candidates: <plain text: what should become a record, or which record is touched or refuted, or "none">
```

The enforcing `SubagentStop` hook ([hooks](../reference/hooks.md)) checks `records_consulted` and `record_candidates` for the roles in the plugin option `retro_roles` (default only `fabrica:anchor-lint`; add your own teams with `/plugin configure fabrica@fabrica`). The orchestrator reads the blocks during `/reflect` (Step 1); `learned:` and `record_candidates:` become candidates for the archivist.

**Reference implementation (shipped with this repo):** `examples/agents/example-agent-with-memory.md` — copy it to `~/.claude/agents/<name>.md`, rename, and fill in the actual job.

---

## What the plugin sets up

The plugin (see the [README](../../README.md)) ships the agents (`fabrica:librarian`, `fabrica:archivist`, `fabrica:anchor-lint`), the skills (`fabrica:reflect`, `fabrica:setup`, `fabrica:handoff-protocol`), the navigation reference, the `mem` and `mem-dream` commands and all four hooks.

It does **not** wire your skills or agents: those are local configuration that you own. `/fabrica:setup` proposes the wiring and applies it on your approval. `examples/agents/` ships a starting point to copy, not a file installed automatically.

## Check the wiring

`mem doctor` (section Wiring) lists every command, agent or skill that spawns agents or names memory but lacks the `handoff-protocol` line; section Effect shows, per agent type, how often `records_consulted` and `record_candidates` were actually given.
