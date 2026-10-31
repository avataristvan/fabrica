id: domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31
type: domain
area: architecture
perspective: user
created: 1793470086.23224
edges: [{"target_id": "domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12", "edge_type": "related"}, {"target_id": "domain_repo_renamed_fabrica_folder_and_plugin_stay_2026_10_15", "edge_type": "related"}, {"target_id": "todo_verify_external_installation_migration_and_plugin_switch_2026_10_15", "edge_type": "related"}]
cue: I am about to remove migration, upgrade or cleanup code while other installations that auto-update from main may still lag behind.
---

Decision: Before an upgrade, migration or cleanup path is removed from main, the last version that still carries it gets a tag, and the README names that tag. Only after that may main lose the path.
Why: An installation that auto-updates from main and has not migrated would otherwise pull a version with neither the migration nor the guard; the tag is its way forward. This replaces the reason "keep the migration code until it is known to have migrated" with a mechanism that does not depend on knowing the state of every installation.
Scope: Removing migration, upgrade or cleanup code while other installations may lag behind. Done for the legacy path: tag v1-last-upgrade-path (ed7d282, pushed), README section "Upgrading from the earlier versions". The legacy-removal chunk removes install.py, uninstall.py, UPGRADING.md, the records_v1 migration, the upgrade guard and scripts/upgrade_acceptance from main; v1-last-upgrade-path is the way forward for unmigrated installations, v0-last-mcp the MCP rollback. That chunk is committed on a worktree branch and is not merged or pushed (pending evidence, not done); the consequences for the records below take effect with that merge. Affected: the clause "the migration code stays until it is known to have migrated" in domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12, and the "installed users" reason for keeping the plugin name in domain_repo_renamed_fabrica_folder_and_plugin_stay_2026_10_15 (the rename of folder and plugin to fabrica is now planned, see todo_rename_folder_and_plugin_to_fabrica_2026_10_31; the area-path reason of that record still holds).
Evidence: tag v1-last-upgrade-path; README.md "Upgrading from the earlier versions". At the merge, add the file or test that shows the removal instead of a commit SHA.
