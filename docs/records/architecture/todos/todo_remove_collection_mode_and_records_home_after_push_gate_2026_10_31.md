id: todo_remove_collection_mode_and_records_home_after_push_gate_2026_10_31
type: todo
area: architecture
perspective: user
created: 1793470100.396984
edges: [{"target_id": "domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31", "edge_type": "derived_from"}, {"target_id": "domain_records_home_stays_for_migration_2026_10_13", "edge_type": "related"}]
cue: The legacy-removal chunk has been pushed and I see collection mode or the ai-mem-records fallback still in the code.
---

TODO (user confirmed): After the push gate of the legacy-removal chunk, remove collection mode and the records-home fallback. domain_records_home_stays_for_migration_2026_10_13 says to remove the fallback once the migration itself is retired; the removal chunk retires it, with the way forward for laggards in the tag named by the README (domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31).
