type: pattern
topic: records
perspective: the-coder
created: 1791756505.762109
cue: I am moving records in a batch and the move would rewrite edges that point at them from other areas
---

Rule: A batch move rewrites referrers only in versioned source areas. Referrers in other areas are reported, not rewritten.
When: `mem move --batch` and any redistribution that relinks edges.
Why: A rewrite replaces the old text, and only git can restore it. In an unversioned area an unnoticed rewrite cannot be undone. This is the precondition of [domain_clear_dead_weight_keep_reasons_2026_10_10](../../architecture/decisions/domain_clear_dead_weight_keep_reasons_2026_10_10.md) holding again in practice (version control under the area).

## Edges

- related: [pattern_batch_move_builds_destination_map_first_2026_10_12](pattern_batch_move_builds_destination_map_first_2026_10_12.md)
- confirms: [domain_clear_dead_weight_keep_reasons_2026_10_10](../../architecture/decisions/domain_clear_dead_weight_keep_reasons_2026_10_10.md)
- related: [domain_mem_move_area_renames_with_references_rename_first_2026_11_01](domain_mem_move_area_renames_with_references_rename_first_2026_11_01.md)
