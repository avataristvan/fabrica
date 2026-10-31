Cleaning up the public repo avataristvan/fabrica for a first visit (hiring manager, customer), in small chunks. Briefing: the business area's briefing-aufraeumen-2026-10-31.md (outside this repo). One repo: Fabrica is the method (docs/fabrica/), ai-mem the plugin that implements it.

Done: legacy upgrade path removed (last version: tag v1-last-upgrade-path), collection mode and records home gone, README leads with the problem, and the rename to fabrica is complete inside and outside the repo (folder, plugin fabrica@fabrica, editable install, plugin clone; package ai_mem and CLI mem keep their names). Checked with mem doctor --root <workspace> and a fabrica:librarian smoke test.

Next, in order:
- tell the external installation that the plugin is now fabrica@fabrica (reinstall once); its migration is still unverified (todo_verify_external_installation_migration_and_plugin_switch_2026_10_15).
- the product backlog in todos/; the 6 unprocessed sources.

Rules that hold: pseudonymise in place, paths area-relative, `<workspace>` in docs and fixtures, no person named in ids or bodies. Push is the user's; never push the local tags pre-cleanup-*, pre-squash-*, v0-last-mcp-unclean or worktree-agent-* branches.

Committed, awaiting a real run: the Observed/Cause rule and the short archivist interim report (pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24, pattern_archivist_report_is_an_interim_message_2026_10_24).
