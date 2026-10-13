id: pattern_repoint_edges_before_deleting_dead_weight_2026_10_12
type: pattern
area: records
perspective: the-coder
created: 1791756528.108819
edges: [{"target_id": "pattern_duplicate_ids_delete_covered_copy_2026_10_12", "edge_type": "related"}, {"target_id": "domain_mem_delete_names_dangling_edges_2026_10_13", "edge_type": "related"}]
cue: I am about to mem delete a dead-weight copy that other records may still point at
---

Rule: Re-point the edges that target a dead-weight copy to the surviving record before `mem delete`.
When: deleting duplicates or dead-weight records.
Why: Otherwise lint reports the incoming edges as dangling and the reason they carried is lost from the graph. Companion of pattern_duplicate_ids_delete_covered_copy_2026_10_12. `mem delete` prints a `dangling:` line for each same-area edge it leaves behind (domain_mem_delete_names_dangling_edges_2026_10_13).
