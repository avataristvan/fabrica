The plugin rebuild and its target picture are closed (domain_plugin_target_picture_implemented_and_closed_2026_10_15). The repo is public as avataristvan/fabrica; the local folder, plugin and marketplace stay ai-mem. The target picture, chunk plan and other internal working material stay local via `.git/info/exclude`; the local tags `pre-cleanup-*`, `pre-squash-*`, `v0-last-mcp-unclean` and the `worktree-agent-*` branch must never be pushed (push only `git push origin main`).

Now: close the long-running rebuild with two items; a third check does not block closing.
1. Run the chunk 0 upgrade acceptance and record its result (todo_record_chunk0_upgrade_acceptance_result_2026_10_15). Agent.
2. Fix the symlink-following delete (todo_symlink_following_delete). Agent.
Not blocking: the on-site check of the external installation's migration and plugin switch (todo_verify_external_installation_migration_and_plugin_switch_2026_10_15). User, in person, whenever.

After that: everything else in todos/ is product backlog, not part of the rebuild (doctor checks, archivist observability, librarian evals, CLI simplifications, the 6 unprocessed sources).
