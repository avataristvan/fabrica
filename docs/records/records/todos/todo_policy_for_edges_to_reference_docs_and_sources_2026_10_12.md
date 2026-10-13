id: todo_policy_for_edges_to_reference_docs_and_sources_2026_10_12
type: todo
area: records
perspective: the-coder
created: 1791756542.736177
edges: [{"target_id": "pattern_list_incoming_edges_before_moving_or_merging_a_doc_2026_10_12", "edge_type": "related"}, {"target_id": "todo_mem_link_and_find_resolve_source_slugs_2026_10_12", "edge_type": "related"}, {"target_id": "domain_docs_split_into_documentation_and_sources_2026_10_10", "edge_type": "related"}]
cue: A record points at a docs/reference or docs/sources file that may move or be renamed
---

TODO: Decide a policy for edges and Evidence paths that point at reference docs and sources. They dangle when the doc moves (case: the dev_stack_assessment_2026_05 doc during a records redistribution), and `mem move` does not rewrite them because a doc is not a record.

Partly answered (2026-10-12): `mem lint` accepts a source slug as an edge target (an area with docs/sources/<slug>.md resolves it). Still open: `mem link` and `mem find` do not resolve slugs (todo_mem_link_and_find_resolve_source_slugs_2026_10_12), and edges to merged reference ids dangle for good (pattern_list_incoming_edges_before_moving_or_merging_a_doc_2026_10_12).
