Cleaning up the public repo avataristvan/fabrica for a first visit (hiring manager, customer), in small chunks. Briefing: the business area's briefing-aufraeumen-2026-10-31.md (outside this repo). One repo: Fabrica is the method (docs/fabrica/), ai-mem the plugin that implements it.

Done: the legacy upgrade path is removed from main (install.py, uninstall.py, UPGRADING.md, records_v1 migration, upgrade guard, Chroma fixtures). Tag v1-last-upgrade-path is the last version that carries it and the path for any installation not yet migrated; the external installation is still unverified (todo_verify_external_installation_migration_and_plugin_switch_2026_10_15).

Done as well: collection mode and the records home are gone; the README leads with the problem; plugin and marketplace are renamed to fabrica in the repo (agents fabrica:<agent>; package ai_mem and CLI mem stay, by the user's call).

Next, in order:
- the outside part of the rename, run by the user with no session open: folder ai-mem -> fabrica, cross-area edges, ~/.claude and CLAUDE.md references, the plugin clone ~/.local/share/fabrica-plugin, editable install, auto-memory folder. Then a new session: mem doctor --root <workspace>, smoke test of fabrica:librarian, and the record candidates of the rename go to the archivist.
- tell the external installation that the plugin is now fabrica@fabrica (reinstall once).
- resolve the tension between domain_fabrica_records_public_as_self_proof_2026_10_10 (publish the lodge book) and domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13 (handoffs stay local).

Rules that hold: pseudonymise in place, paths area-relative, `<workspace>` in docs and fixtures, no person named in ids or bodies. Push is the user's; never push the local tags pre-cleanup-*, pre-squash-*, v0-last-mcp-unclean or worktree-agent-* branches.

Committed, awaiting a real run: the Observed/Cause rule and the short archivist interim report (pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24, pattern_archivist_report_is_an_interim_message_2026_10_24).

Later: the product backlog in todos/; the 6 unprocessed sources.
