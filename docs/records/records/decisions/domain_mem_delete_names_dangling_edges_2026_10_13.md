id: domain_mem_delete_names_dangling_edges_2026_10_13
type: domain
topic: records
perspective: user
created: 1791876533.8049
edges: [{"target_id": "domain_mem_unlink_removes_edges_2026_10_13", "edge_type": "related"}, {"target_id": "pattern_repoint_edges_before_deleting_dead_weight_2026_10_12", "edge_type": "related"}]
cue: I am closing a todo or deleting a record that other records point to
---

Decision: `mem delete` prints `dangling: REF --TYPE--> ID` for every same-area edge that pointed at a deleted record and changes nothing else. The archivist's close-todo rule (agents/archivist.md, step 7) repoints each such edge to the result record (`mem link`, then `mem unlink` of the old target) or drops it. Edges in other areas are left to `mem doctor`.
Why: Closing a todo deletes its file, and the incoming edges went dangling unnoticed until a later lint. Rewriting them automatically would put a judgment (which record answers the todo) into code; printing them makes the cost visible in the same step and leaves the judgment with the archivist.
Scope: ai_mem/application/delete_memory.py, agents/archivist.md step 7. Closes todo_repoint_incoming_edges_when_record_closed_2026_10_12. `mem move` still leaves incoming edges dangling (domain_mem_unlink_removes_edges_2026_10_13).
