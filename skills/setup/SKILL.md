---
name: setup
description: "Wire the user's teams and CLAUDE.md to ai-mem: team by team, find each team's real boundaries and propose the one-line handoff-protocol hook-in; propose CLAUDE.md additions (routing line, session-start librarian rule) as a diff; judge a `mem doctor` report (which flagged teams have a real boundary, which hits are spurious). Proposes, never overwrites, applies only on approval, writes no records. Run it after installing the plugin, after adding a team, or when `mem doctor` (Wiring) lists teams."
---

# Setup

You set up the user's own configuration so that it uses ai-mem at the right moments. You propose; the user decides. Arguments (`$ARGUMENTS`) may name files, a directory, a `mem doctor` report, or one of the three parts below; then work only on what they name.

At this boundary follow the ai-mem handoff protocol (skill `ai-mem:handoff-protocol`). Ask the librarian once, before the first proposal, with the area path and the teams you are about to examine: which records concern these teams' boundaries, and was a hook-in here tried or rejected before?

## Rules

- **Propose, never overwrite.** Every change is shown first as a diff of the exact lines. Apply it only after the user approves it in this session, or when a standing instruction the user gave (in a CLAUDE.md or a message) says proposed changes of this kind are applied without asking; then quote that instruction when you apply. Silence, a question back, or approval of a different change is not approval. Without approval the file stays byte-identical.
- **Additions only.** Add lines; never reword, reorder or delete the user's existing text. Where a line already says the same thing in other words, propose nothing for it.
- **Only files the user owns.** A file is the user's when it is a regular file in their `~/.claude/` or in a project's `.claude/` or CLAUDE.md, written by them. Never edit what ships with a plugin or a marketplace (anything under `~/.claude/plugins/`, a symlink into another checkout, a file whose frontmatter or header names another author or package), ai-mem's own agents and skills included. For such a file, report the boundary you found and leave it; there is no exclusion list, the judgment is made per file.
- **No records.** You do not run `mem add`, `mem link` or `mem lint --fix` and do not edit `docs/records/`. What should become a record goes into `record_candidates` for `/ai-mem:reflect`, which hands it to the archivist.
- **No settings, no installer.** You do not edit `settings.json`; when one of them is the fix, name the command for the user to run.

## 1. Teams: one hook-in per real boundary

A team is a command, agent or skill that spawns other agents (`Agent(`, `subagent_type`) or reads or stores what earlier sessions decided. Discover them in `~/.claude/commands/*.md`, `~/.claude/agents/*.md`, `~/.claude/skills/*/SKILL.md` and the current project's `.claude/`. Order: teams that orchestrate other teams first (they spawn planners, coders, reviewers), then the agents and skills they spawn, then single skills. Work through one team at a time: read its file and every file it names for the roles it spawns, propose, wait for the decision, then go to the next.

A **real boundary** is an observable moment where one role hands work to another or starts work whose files are known:

- a task or chunk starts in a spawned role (the place is the prompt template that role receives, because a spawned agent starts cold and reads only its prompt and its own definition);
- a plan is drafted, before decomposing;
- a diff or draft goes to review;
- a skill is about to read or store what earlier sessions decided (before the first persona speaks, before the first draft);
- the gate after a role reports back, where its `[retro]` is collected for `/ai-mem:reflect`.

Not a boundary: a role table, an introduction, a list of rules, every step of a loop, a place where nothing is handed over. One line per boundary; if two candidate places describe the same moment, take the one the receiving role actually reads.

At each real boundary propose exactly this line, verbatim:

```
At this boundary follow the ai-mem handoff protocol (skill `ai-mem:handoff-protocol`).
```

Where a team already carries it, or the older form `(skill \`handoff-protocol\`)`, propose nothing new; for the older form propose only the prefix `ai-mem:`. Where a team already asks the librarian at that moment in its own words, the line still goes in (it is what `mem doctor` checks), right before that text. Show each proposal as a diff with two lines of context and one sentence on why this moment is a boundary.

## 2. CLAUDE.md: routing line and session-start rule

Preferences that must act in every session belong in CLAUDE.md, not in records. Read the CLAUDE.md files that apply to the current work: the project's (nearest to the working directory) and the user's `~/.claude/CLAUDE.md`. If none exists at the project, propose a new file with only the two additions. Check what they already say, then propose at most these two additions:

- **Routing line** (project CLAUDE.md), so a session knows where the history is:
  `History and rationale live in \`docs/records/\` (\`FOCUS.md\` = current focus, \`INDEX.md\` = catalogue); for "why is it like this / was this tried before?" ask the \`ai-mem:librarian\` agent.`
- **Session-start librarian rule** (the user's CLAUDE.md, or the project's when the user wants it there only). It names an observable moment, not a category of work; a trigger that needs classifying the session first does not fire:
  `As soon as the user's first message sets the scope (which system or problem), ask the \`ai-mem:librarian\` agent (model haiku) with the area path and 1-3 concrete questions before answering substantively. Ask again when the scope changes. Not for one-off commands.`

Place an addition at the end of the file or under an existing heading where it fits; never inside the user's sentences. Present both as one unified diff per file and ask for approval. Apply only as the Rules say; otherwise leave the file as it is and say so.

## 3. A `mem doctor` report: judge, do not repair

Use the report the user gives, or run `mem doctor` yourself. Its findings are keyword heuristics: hits that are not real problems are expected, and the Effect rates are not evidence of what a team achieves.

**Wiring, "teams without `handoff-protocol`".** The doctor flags every file whose text matches a signal (`Agent(`, `subagent_type`, `ai-mem`, `librarian`, `archivist`, `docs/records`, `mem_add`, `mem_query`) and lacks the substring `handoff-protocol`. For each flagged file, read it and decide:

- **real**: the file has a boundary as defined in part 1 (it hands work to a role it spawns, or reads or stores memory at a fixed moment). If the user owns it, go through part 1 for it. If not, report the boundary and leave the file.
- **spurious**: the signal is incidental. Examples: the word appears in another sense (a "librarian" persona of a story, "memory" of a device), the file is a copy an older ai-mem version installed that the plugin now replaces (the user removes it by hand), or a single-step tool that spawns nothing and stores nothing. Propose no hook-in; say in one line why the hit is spurious.

Give a verdict for every flagged file: path, real or spurious, the evidence (the line or the absence of a handoff), and the proposal or "nothing to change".

**Wiring, hooks.** "plugin enabled" is the target. Hooks still registered in `settings.json` next to the plugin fire twice: tell the user to remove the old hook entries from `settings.json` by hand, or to check out the tag `v1-last-upgrade-path` and run its `install.py --plugin-switch`.

**Records, Sources, State, Effect.** Lint findings, dangling edges, dead-weight candidates, unadopted hand-written records, unprocessed sources, current docs naming a retired system, a stale `FOCUS.md`: none of these is yours to fix. Turn each into a plain-text record candidate (what the doctor reported, where, and why it matters) for the archivist via `/ai-mem:reflect`, or point the user to `/ai-mem:reflect` when the fix is a handoff. Effect rates near zero for a role are a question for the user (has the step become ritual?), not a finding against the team.

## Close

End with a short list: per team the boundaries found and what was applied or left open; per CLAUDE.md the additions applied or left unapplied; per doctor finding the verdict. Then:

```
[retro]
learned: <what surprised you, or "nothing">
blocked: <what got in the way, or "nothing">
next: <suggested todo, or "nothing">
records_consulted: <ids the librarian named that carried a decision, or "none">
record_candidates: <plain text: the doctor's record findings, boundaries that were judged and why, or "none">
```
