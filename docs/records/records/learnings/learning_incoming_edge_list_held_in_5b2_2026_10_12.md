id: learning_incoming_edge_list_held_in_5b2_2026_10_12
type: learning
area: records
perspective: agent
created: 1791786665.841492
edges: [{"target_id": "pattern_list_incoming_edges_before_moving_or_merging_a_doc_2026_10_12", "edge_type": "confirms"}, {"target_id": "domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12", "edge_type": "related"}]
cue: Reviewing a docs move chunk for dangling paths in records
---

Observed: In the docs-move chunk the coder followed the rule to list referrers before moving docs: it reported the records and READMEs that still name the old paths (adr-format, hooks, architecture, developer-guide, migration-chroma-to-records, skill-agent-integration, collections) instead of leaving dangling paths. The archivist could then fix them. The librarian's answer had also supplied the coder's do-not-touch list (todo_fix_broken_memPalace_link_in_epistemology_framework_2026_10_12, todo_decide_plan_and_rollback_docs_banner_or_sources_2026_10_12).
Cause: The rule was recalled through the librarian and applied at chunk start.
Evidence: pattern_list_incoming_edges_before_moving_or_merging_a_doc_2026_10_12.
