type: domain
topic: architecture
created: 1791111270.18417
---

Decision: The record files are ai-mem's only store. FileMemoryRepository implements the MemoryRepository protocol directly on docs/records/ (record types), FOCUS.md (current_focus) and docs/reference/ (reference); server, mem-dream, hooks and view_cli get it from repository_factory.build_repository(). mem_add rejects types without a file (feedback, project, fact, dilemma, untyped); mem_query is a keyword search; counters, TTL and whole-collection delete are gone. The PostToolUse hook is retired (it only bumped last_accessed_at). AI_MEM_BACKEND=chroma restores the old stack as a rollback.
Why: Carries out [domain_records_model_replaces_chroma_2026_10_04](../../records/decisions/domain_records_model_replaces_chroma_2026_10_04.md). The librarian confirmed from the records that semantic search never earned its place ([eval_pull_gap_test_2026_09_20](../../evaluation/learnings/eval_pull_gap_test_2026_09_20.md), [domain_direction_judgment_over_scores_2026_09_20](domain_direction_judgment_over_scores_2026_09_20.md)) and that the daemon only existed for Chroma latency. Rejecting untyped writes keeps the taxonomy as the quality gate ([pattern_taxonomy_as_quality_gate](pattern_taxonomy_as_quality_gate.md)).
Scope: ai-mem runtime. chromadb stays installed until other installations have run the records_v1 migration (mem-adr-sync migrate) and as the rollback; daemon, BM25, experience_index and the unwired hook modules are dormant, not deleted.

## Edges

- derived_from: [domain_records_model_replaces_chroma_2026_10_04](../../records/decisions/domain_records_model_replaces_chroma_2026_10_04.md)
- related: [domain_librarian_replaces_experience_index_2026_10_04](domain_librarian_replaces_experience_index_2026_10_04.md)
- related: [pattern_taxonomy_as_quality_gate](pattern_taxonomy_as_quality_gate.md)
- supersedes: [decision_hybrid_fusion_cosine_saturated_bm25_2026_10_04](../../general/decisions/decision_hybrid_fusion_cosine_saturated_bm25_2026_10_04.md)
- related: [pattern_local_adaptive_learning_from_behavior_2026_10_04](../../general/decisions/pattern_local_adaptive_learning_from_behavior_2026_10_04.md)
- related: [domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12](domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12.md)
- confirms: [domain_direction_judgment_over_scores_2026_09_20](domain_direction_judgment_over_scores_2026_09_20.md)
