type: pattern
topic: records
perspective: the-coder
created: 1791756528.108819
cue: I am about to mem delete a dead-weight copy that other records may still point at
---

Rule: Re-point the edges that target a dead-weight copy to the surviving record before `mem delete`.
When: deleting duplicates or dead-weight records.
Why: Otherwise lint reports the incoming edges as dangling and the reason they carried is lost from the graph. Companion of [pattern_duplicate_ids_delete_covered_copy_2026_10_12](pattern_duplicate_ids_delete_covered_copy_2026_10_12.md). `mem delete` prints a `dangling:` line for each same-area edge it leaves behind ([domain_mem_delete_names_dangling_edges_2026_10_13](domain_mem_delete_names_dangling_edges_2026_10_13.md)).

## Edges

- related: [pattern_duplicate_ids_delete_covered_copy_2026_10_12](pattern_duplicate_ids_delete_covered_copy_2026_10_12.md)
- related: [domain_mem_delete_names_dangling_edges_2026_10_13](domain_mem_delete_names_dangling_edges_2026_10_13.md)
