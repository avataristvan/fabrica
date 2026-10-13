id: domain_mem_unlink_removes_edges_2026_10_13
type: domain
area: records
perspective: the-coder
created: 1791869829.445028
edges: [{"target_id": "learning_undoing_supersede_removes_both_fields_2026_10_12", "edge_type": "confirms"}, {"target_id": "domain_mem_delete_names_dangling_edges_2026_10_13", "edge_type": "related"}]
cue: I need to remove an edge, undo a supersede, or clear a dangling edge after a todo is closed
---

Decision: `mem unlink SOURCE TARGET [--type T]` (RemoveEdgeUseCase, ai_mem/application/remove_edge.py) removes edges as stored, also when the target no longer exists. Removing a supersedes edge clears superseded_by and valid_until on the target only when the target names this source.
Why: Edges were hand-edited three times during a batch of record moves (learning_undoing_supersede_removes_both_fields_2026_10_12); the dangling edge in learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12 (to a closed todo) was removed with it.
Scope: the mem CLI. Repointing or dropping incoming edges when a todo is closed (and on mem delete / mem move) was not built with it: todo_repoint_incoming_edges_when_record_closed_2026_10_12 (since closed by domain_mem_delete_names_dangling_edges_2026_10_13). Closes todo_mem_unlink_command_2026_10_12.
Evidence: ai_mem/application/remove_edge.py and its tests.
