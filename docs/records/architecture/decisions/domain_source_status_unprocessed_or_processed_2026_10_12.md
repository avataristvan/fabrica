id: domain_source_status_unprocessed_or_processed_2026_10_12
type: domain
area: architecture
perspective: the-coder
created: 1791758107.216165
edges: [{"target_id": "domain_docs_split_into_documentation_and_sources_2026_10_10", "edge_type": "derived_from"}, {"target_id": "domain_doctor_retired_system_check_is_keyword_heuristic_2026_10_12", "edge_type": "related"}, {"target_id": "domain_mem_source_sets_status_and_link_find_reach_sources_2026_11_01", "edge_type": "related"}]
cue: Deciding whether a file in docs/sources/ may be marked processed
---

Decision: A source in docs/sources/ has `status: unprocessed` or `status: processed`. A source may be processed only when a record points to it: an `Evidence: docs/sources/<slug>.md` path in the record text, or an edge whose target is the slug. A source whose conclusions no longer hold stays `unprocessed`, and the archivist reports why; the doctor lists it as awaiting.
Why: The doctor can check the status mechanically (it lists sources no record points to), and a source with nothing that still holds does not need a record. The status line is the only part of a source that changes; its body is frozen.
Scope: docs/sources/*, docs/reference/record-format.md "Sources", the Sources section of `mem doctor`. Extends domain_docs_split_into_documentation_and_sources_2026_10_10.
