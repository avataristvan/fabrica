id: domain_rebuild_closing_scoped_to_three_todos_2026_10_15
type: domain
area: architecture
perspective: user
created: 1792061047.277119
superseded_by: domain_rebuild_closing_scoped_to_two_todos_2026_10_15
valid_until: 1792061274.140043
edges: [{"target_id": "domain_plugin_target_picture_implemented_and_closed_2026_10_15", "edge_type": "related"}, {"target_id": "todo_verify_external_installation_migration_and_plugin_switch_2026_10_15", "edge_type": "related"}]
cue: You are asked what is still needed to call the rebuild done, or you pick the next todo.
---

Decision: Closing the long-running rebuild is scoped to three items (user, 2026-10-15): the chunk 0 upgrade acceptance result (todo_record_chunk0_upgrade_acceptance_result_2026_10_15), the symlink-following delete fix (todo_symlink_following_delete), and the on-site check of the external installation (todo_verify_external_installation_migration_and_plugin_switch_2026_10_15).
Why: All other open todos and the 6 unprocessed sources are product backlog and do not block closing the rebuild.
Scope: the choice of the next todo and the statement "rebuild done". Follows domain_plugin_target_picture_implemented_and_closed_2026_10_15.
