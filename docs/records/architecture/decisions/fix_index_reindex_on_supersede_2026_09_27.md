id: fix_index_reindex_on_supersede_2026_09_27
type: domain
topic: architecture
created: 1790524300.309417
edges: [{"target_id": "domain_drop_confidence_for_evidence_and_librarian_2026_09_26", "edge_type": "related"}, {"target_id": "learning_index_status_stale_after_supersede_2026_09_27", "edge_type": "derived_from"}]
---

Decision: MarkdownAdrRepository.upsert() now triggers regenerate_index() automatically, but narrowly -- only when an entry's `superseded_by` metadata field actually changes (old file's parsed frontmatter vs. new metadata differ), never on plain creation or a mem_boost-only write.

Why: INDEX.md's status column must not go stale after a supersede, because the librarian agent (domain_drop_confidence_for_evidence_and_librarian_2026_09_26) judges by reading INDEX.md. Plain creates/boosts keep staying off INDEX.md, so the read-modify-write race that the INDEX introduction avoided is not reopened (observation and root cause: learning_index_status_stale_after_supersede_2026_09_27).

Scope: ai_mem/infrastructure/markdown_adr_repository.py. `_sync_file()` now returns whether `superseded_by` changed; `upsert()` calls a new `_reindex()` helper only when that's true. Both call sites that can set `superseded_by` -- `mem_link` (server.py) and `mem_dream --auto_supersede` (dream_memory.py) -- route through `AddEdgeUseCase`'s target upsert (application/add_edge.py), so both are covered without touching AddEdgeUseCase or either dispatch site. Tests: test_markdown_adr_repository.py::test_supersede_upsert_regenerates_index, test_boost_only_upsert_does_not_regenerate_index.

Status 2026-10-04 (checked): FileMemoryRepository rewrites the target's file on supersede and regenerates INDEX.md on any record content change; covered by test_edges_supersede_and_cue_through_the_use_cases.
