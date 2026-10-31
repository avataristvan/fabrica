id: todo_verify_external_installation_migration_and_plugin_switch_2026_10_15
type: todo
area: architecture
perspective: user
created: 1792016093.273849
edges: [{"target_id": "domain_plugin_target_picture_implemented_and_closed_2026_10_15", "edge_type": "related"}, {"target_id": "domain_rebuild_closing_scoped_to_three_todos_2026_10_15", "edge_type": "related"}, {"target_id": "domain_rebuild_closing_scoped_to_two_todos_2026_10_15", "edge_type": "related"}, {"target_id": "domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31", "edge_type": "related"}]
cue: You are about to rely on the external installation with an auto-updating agent having migrated to the plugin.
---

TODO (user, in person): check on site the external installation with an auto-updating agent: did it run the records_v1 migration and the plugin switch (is `.migrations/records_v1.done` present)?

Update 2026-10-31 (user): this is now a push gate. Close it before the legacy-removal chunk is pushed; it is no longer "not blocking". The chunk is committed on a worktree branch, not merged or pushed. The tag v1-last-upgrade-path named in the README is the way forward for an installation that has not migrated (domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31).
