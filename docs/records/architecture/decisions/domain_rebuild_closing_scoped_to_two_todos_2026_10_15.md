id: domain_rebuild_closing_scoped_to_two_todos_2026_10_15
type: domain
area: architecture
perspective: user
created: 1792061273.883129
edges: [{"target_id": "domain_rebuild_closing_scoped_to_three_todos_2026_10_15", "edge_type": "supersedes"}, {"target_id": "domain_plugin_target_picture_implemented_and_closed_2026_10_15", "edge_type": "related"}, {"target_id": "todo_record_chunk0_upgrade_acceptance_result_2026_10_15", "edge_type": "related"}, {"target_id": "todo_symlink_following_delete", "edge_type": "related"}, {"target_id": "todo_verify_external_installation_migration_and_plugin_switch_2026_10_15", "edge_type": "related"}]
cue: You are asked what is still needed to call the rebuild done, or you pick the next todo.
---

Decision: Closing the long-running rebuild needs two items (user, 2026-10-15): the chunk 0 upgrade acceptance result (todo_record_chunk0_upgrade_acceptance_result_2026_10_15) and the symlink-following delete fix (todo_symlink_following_delete).
Why: The on-site check of the external installation (todo_verify_external_installation_migration_and_plugin_switch_2026_10_15) does not block closing; the user does it themselves whenever. All other open todos and the 6 unprocessed sources are product backlog and do not block closing either. Corrects the first version of this decision (three items), which counted the on-site check.
Scope: the choice of the next todo and the statement "rebuild done". Follows domain_plugin_target_picture_implemented_and_closed_2026_10_15.
