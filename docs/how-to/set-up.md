# How to set up your teams and CLAUDE.md

How to connect your own commands, agents, skills and CLAUDE.md files to ai-mem with the plugin skill `/ai-mem:setup`. It reads your files, proposes changes as diffs and applies only what you approve. It writes no records.

Run it after installing the plugin, after adding or changing a team, and when `mem doctor` (section Wiring) lists teams.

```
/ai-mem:setup
/ai-mem:setup .claude/commands/release-train.md      # one team only
/ai-mem:setup judge this report: <paste mem doctor output>
```

## What it proposes

**Hook-ins, team by team.** A team is a command, agent or skill that spawns other agents or reads or stores memory. Setup starts with the teams that orchestrate others, reads each team's file and the roles it spawns, and finds the moments where work is handed over: a task starts in a spawned role, a plan is drafted, a diff goes to review, a skill is about to use what earlier sessions decided, a role reports back. At each one it proposes this line, verbatim:

```
At this boundary follow the ai-mem handoff protocol (skill `ai-mem:handoff-protocol`).
```

For a spawned role the line goes into the prompt that role receives, because a spawned agent reads only its prompt and its own definition. What the line triggers is described in [Wire skills and agents](wire-skills-and-agents.md).

**CLAUDE.md additions.** Two lines, only where nothing equivalent is there yet:

- a routing line in the project's CLAUDE.md: where the history lives (`docs/records/`, `FOCUS.md`, `INDEX.md`) and that the `ai-mem:librarian` agent answers "why is it like this / was this tried before?";
- a session-start rule in your `~/.claude/CLAUDE.md` (or the project's, if you want it there only): when the first message sets the scope, ask the librarian before answering substantively. It names an observable moment, so it fires without classifying the session first.

**A verdict per `mem doctor` finding.** The doctor's Wiring check is a keyword match, so it flags files that mention an agent or the word "librarian" in another sense. Setup reads each flagged file and says whether it has a real boundary (then it proposes the hook-in) or the hit is spurious (then nothing changes). Findings about records, sources and state are not fixed by setup: they become record candidates for the archivist, handed over by `/ai-mem:reflect`.

## What it never does

- Change a file without your approval in the session. A standing instruction of yours, for example a CLAUDE.md line saying proposed CLAUDE.md changes are applied without asking, counts as approval; setup quotes it when it applies.
- Reword, reorder or delete your text. It only adds lines.
- Edit agents or skills that come from a plugin or a marketplace, ai-mem's own included. For those it reports the boundary and leaves the file.
- Write records, run `mem lint --fix`, or edit `settings.json`. Where one of these is the fix, it names the change for you to make, for example removing copies an older ai-mem installed into `~/.claude`.

## Check the result

Run `mem doctor`. Wiring should list no team that setup judged real, and show `hooks: ai-mem plugin enabled`. Files setup judged spurious stay on the list; that is expected.
