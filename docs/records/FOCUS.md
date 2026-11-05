Fabrica 0.1.0: the method (docs/fabrica/) and the plugin fabrica@fabrica that implements it (memory part ai-mem: package ai_mem, command mem). The repository is in a presentable state: README with a runnable quick start, glossary, English-only agent texts, past handoffs published as sources.

Now: bring the record format change (no ids; edges and mentions are relative links, `mem lint --fix` migrates) to another area, first galaxy-tab-a-2016 (388 records in the old format, local agents in .claude/agents/, cited handoffs to freeze as sources). Plan it with that session: who runs the migration, how its local agents and docs learn the new format, and when the plugin cache gets updated so the lint_after_write hook does not block old records there. What works there becomes the generic way for every area.

Next:
- README for the first impression: the problem first, then the practice, the plugin and the honest measurement report ([domain_public_face_experience_report_not_launch_2026_10_24](architecture/decisions/domain_public_face_experience_report_not_launch_2026_10_24.md)).
- Keep docs/explanation/how-fabrica-built-itself.md current when a new chain is worth showing.

Committed, awaiting a real run: the Observed/Cause rule and the short archivist interim report ([pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24](architecture/decisions/pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24.md), [pattern_archivist_report_is_an_interim_message_2026_10_24](architecture/decisions/pattern_archivist_report_is_an_interim_message_2026_10_24.md)); the archivist's `searched:` line (one line per candidate, no "none" lines, edges counted).

Rules that hold: pseudonymise in place, paths area-relative, `<workspace>` in docs and fixtures, no person named in ids or bodies. Push is the user's; local-only tags and branches are never pushed.

Backlog: BACKLOG.md.
