Fabrica 0.1.0: the method (docs/fabrica/) and the plugin fabrica@fabrica that implements it (memory part ai-mem: package ai_mem, command mem). The repository is in a presentable state: README with a runnable quick start, glossary, English-only agent texts, past handoffs published as sources.

Now: the documentation map and how a project gets there (plan: [docs/plans/documentation-map/](../plans/documentation-map/chunks.md)): every kind of content gets one place and lifecycle (experiments in docs/experiments/, raw data in a git-ignored data/), `mem doctor` and `/fabrica:setup` bring a project there, a triage skill dissolves handoffs. Pilot: galaxy-tab-a-2016, which then also gets the record format migration.

Next:
- README for the first impression: the problem first, then the practice, the plugin and the honest measurement report ([domain_public_face_experience_report_not_launch_2026_10_24](architecture/decisions/domain_public_face_experience_report_not_launch_2026_10_24.md)).
- Keep docs/explanation/how-fabrica-built-itself.md current when a new chain is worth showing.

Committed, awaiting a real run: the Observed/Cause rule and the short archivist interim report ([pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24](architecture/decisions/pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24.md), [pattern_archivist_report_is_an_interim_message_2026_10_24](architecture/decisions/pattern_archivist_report_is_an_interim_message_2026_10_24.md)); the archivist's `searched:` line (one line per candidate, no "none" lines, edges counted).

Rules that hold: pseudonymise in place, paths area-relative, `<workspace>` in docs and fixtures, no person named in ids or bodies. Push is the user's; local-only tags and branches are never pushed.

Backlog: BACKLOG.md.
