id: todo_verify_external_installation_migration_and_plugin_switch_2026_10_15
type: todo
area: architecture
perspective: user
created: 1792016093.273849
edges: [{"target_id": "domain_plugin_target_picture_implemented_and_closed_2026_10_15", "edge_type": "related"}, {"target_id": "domain_rebuild_closing_scoped_to_three_todos_2026_10_15", "edge_type": "related"}, {"target_id": "domain_rebuild_closing_scoped_to_two_todos_2026_10_15", "edge_type": "related"}, {"target_id": "domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31", "edge_type": "related"}, {"target_id": "todo_tell_external_installation_plugin_is_now_fabrica_2026_10_31", "edge_type": "related"}]
cue: You are about to rely on the external installation with an auto-updating agent having migrated to the plugin.
---

TODO (user, in person): check on site the external installation with an auto-updating agent: did it run the records_v1 migration and the plugin switch (is `.migrations/records_v1.done` present)?

Update 2026-10-31 (user): no longer a push gate. The user pushed the legacy-removal chunk (3c64e27) before this was verified, because the tag is the path for that installation. It stays open: if the installation has not migrated, it must check out tag v1-last-upgrade-path and follow the steps there (domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31).
