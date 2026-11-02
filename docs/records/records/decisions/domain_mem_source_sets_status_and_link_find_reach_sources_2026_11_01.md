id: domain_mem_source_sets_status_and_link_find_reach_sources_2026_11_01
type: domain
topic: records
perspective: agent
created: 1793524156.530212
edges: [{"target_id": "domain_source_status_unprocessed_or_processed_2026_10_12", "edge_type": "related"}]
cue: You are processing a source and need to flip its status, or want a record to point at a docs/sources slug.
---

Decision: `mem link` accepts a source slug (docs/sources/<slug>.md) as target (not for supersedes) and `mem find` lists sources. New `mem source SLUG --status processed|unprocessed` changes only the status frontmatter line.
Why: The archivist may write only through mem, so the doctor's source queue could not be closed by it; on 2026-11-01 six sources had to be flipped by hand. Before, a record could point at a source only through an Evidence path in its text.
Scope: records and sources of every area mem reaches. Evidence: bf4c3b0, tests/test_mem_cli.py test_source_*. Closes todo_mem_link_and_find_resolve_source_slugs_2026_10_12.
