type: pattern
topic: records
perspective: the-coder
created: 1791756524.429847
cue: I am moving a record into a public area and it has related or derived_from edges
---

Rule: Before a move into a public area, check the secondary edges (`related`, `derived_from`) for targets in internal areas, not only `supersedes`.
When: moving records out of an area that holds internal or private records.
Why: The move re-qualifies each edge into a relative path, and for an internal target that path names the private area, which leaks its existence and layout into the public record. See [domain_internal_records_stay_out_of_public_areas_2026_10_12](../../architecture/decisions/domain_internal_records_stay_out_of_public_areas_2026_10_12.md).

## Edges

- related: [pattern_batch_referrer_rewrite_needs_versioned_areas_2026_10_12](pattern_batch_referrer_rewrite_needs_versioned_areas_2026_10_12.md)
- related: [pattern_repoint_edges_before_deleting_dead_weight_2026_10_12](pattern_repoint_edges_before_deleting_dead_weight_2026_10_12.md)
- related: [pattern_list_incoming_edges_before_moving_or_merging_a_doc_2026_10_12](pattern_list_incoming_edges_before_moving_or_merging_a_doc_2026_10_12.md)
- related: [domain_internal_records_stay_out_of_public_areas_2026_10_12](../../architecture/decisions/domain_internal_records_stay_out_of_public_areas_2026_10_12.md)
