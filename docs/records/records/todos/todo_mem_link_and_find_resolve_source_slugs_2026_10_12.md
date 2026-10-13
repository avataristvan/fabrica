id: todo_mem_link_and_find_resolve_source_slugs_2026_10_12
type: todo
area: records
perspective: the-coder
created: 1791758111.443348
edges: [{"target_id": "todo_policy_for_edges_to_reference_docs_and_sources_2026_10_12", "edge_type": "related"}]
cue: mem link or mem find reports not found for a docs/sources slug that lint accepts
---

TODO: Make `mem link` and `mem find` resolve source slugs (docs/sources/<slug>.md) like record ids. `mem lint` already accepts a slug as an edge target, but `mem find <slug>` answers "not found" and `mem link` cannot write an edge to a slug, so a record can point at a source only through an Evidence path in its text.
