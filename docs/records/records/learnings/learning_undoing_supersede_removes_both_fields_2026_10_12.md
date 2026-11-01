id: learning_undoing_supersede_removes_both_fields_2026_10_12
type: learning
topic: records
perspective: the-coder
created: 1791756518.654573
edges: [{"target_id": "domain_mem_unlink_removes_edges_2026_10_13", "edge_type": "related"}]
cue: I am reverting a supersede by hand-editing a record file
---

Observed: Undoing a supersede means removing both `superseded_by` and `valid_until` from the old record, and the `supersedes` edge from the new one. Removing only `superseded_by` leaves the record flagged as expired.
Cause: `mem link --type supersedes` sets the pair together; there was no inverse command, so the edit was by hand (now `mem unlink`, domain_mem_unlink_removes_edges_2026_10_13).
Evidence: a batch of record moves in which records were edited by hand three times; see todo_mem_unlink_command_2026_10_12.
