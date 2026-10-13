id: pattern_deployed_artifact_source_classes
type: pattern
area: workflow
created: 1790440791.965188
cue: I am about to change a file under ~/.claude/ (command, skill, agent).
---

Rule: Before editing a deployed file (skill, command, agent), determine its source class: (1) repo source plus installed copy (a command copied from the repo into ~/.claude/commands/): edit the source, then synchronise the copy; (2) symlink or in-place plugin file (e.g. ~/.claude/agents/librarian.md -> the repo file, or the plugin's agents/ and skills/): edit the repo file; agent definitions are only re-read after a restart of Claude Code; (3) purely global, without a repo source (~/.claude/commands/chunk-plan.md, dev-team.md): edit directly in place.
When: A file under ~/.claude/ is to be changed.
Why: All three cases occurred on 2026-09-26. A direct change to a copy of class (1) drifts silently and is overwritten at the next install; for class (3) there is no source one could edit instead.
Clarification (user, 2026-09-26): Class (3) is not a versioning hole to be closed. It is the exception to CLAUDE.md's invariant 'never edit ~/.claude/commands/*.md directly', which applies only to files with a repo source -- without a source there is nothing a copy could diverge from.
