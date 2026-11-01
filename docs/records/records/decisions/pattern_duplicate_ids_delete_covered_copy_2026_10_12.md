id: pattern_duplicate_ids_delete_covered_copy_2026_10_12
type: pattern
topic: records
perspective: user
created: 1791756513.147468
edges: [{"target_id": "domain_clear_dead_weight_keep_reasons_2026_10_10", "edge_type": "related"}]
cue: The same record id exists in two areas after a move or redistribution and I am tempted to rename one
---

Rule: When an id exists in two areas, delete the copy whose substance is covered elsewhere, in a versioned area. Do not rename it.
When: redistribution, merging areas, any `mem find` that lists one id twice.
Why: Renaming leaves two records with the same content under different ids, so the duplicate survives and the edges multiply. Deleting is safe where git stands behind the area (domain_clear_dead_weight_keep_reasons_2026_10_10).
