id: pattern_list_incoming_edges_before_moving_or_merging_a_doc_2026_10_12
type: pattern
topic: records
perspective: the-coder
created: 1791758108.060381
edges: [{"target_id": "pattern_check_secondary_edges_before_public_move_2026_10_12", "edge_type": "related"}, {"target_id": "domain_docs_split_into_documentation_and_sources_2026_10_10", "edge_type": "related"}, {"target_id": "learning_incoming_edge_list_held_in_5b2_2026_10_12", "edge_type": "related"}]
cue: About to move, rename or merge a file under docs/ or docs/reference/
---

Rule: Before moving or merging a doc, list every record that points at it (edges and Evidence/text paths) and write the list down for the archivist. Edges to a merged reference id dangle for good, because the id no longer exists as a file; only a moved doc keeps a resolvable slug.
When: Chunks that classify, move or merge files in docs/ or docs/reference/.
Why: `mem move` and lint rewrite referrers of records only, not of docs. In the docs-merge chunk the reference doc hook_system was merged into docs/hooks.md and the edge from arch_decision_sessionstart_pull_based_2026_09_16 dangled; at that time mem had no unlink, so the record had to be rewritten (`mem unlink` exists now, domain_mem_unlink_removes_edges_2026_10_13).
Evidence: learning_incoming_edge_list_held_in_5b2_2026_10_12 (the rule applied in the next docs chunk).
