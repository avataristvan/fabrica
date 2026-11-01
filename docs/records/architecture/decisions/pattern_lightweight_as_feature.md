id: pattern_lightweight_as_feature
type: pattern
topic: architecture
created: 1778849285.957444
edges: [{"target_id": "pattern_quality_at_write_time", "edge_type": "related"}, {"target_id": "pattern_confidence_lifecycle", "edge_type": "related"}]
---

Rule: ai-mem's lightweight design (ChromaDB + cosine similarity, no local inference, no ML ranker) is a deliberate constraint — not a gap.
When: Evaluating whether to add local inference, a learned ranker, or heavier retrieval machinery.
Why: The reflect ritual and write-time discipline (type tagging, anti-pattern format, TTL, evidence edges -- confirms/supersedes/contradicts, replacing the earlier confidence lifecycle, see domain_drop_confidence_for_evidence_and_librarian_2026_09_26) deliver high-quality retrieval without ML complexity. Cosine similarity is sufficient when the collection is well-maintained. ML complexity is only justified when write-time discipline fails at scale (hundreds of entries with high thematic overlap).

Status 2026-10-04: The lightweight design is now record files + keyword search + INDEX.md, without a database or embeddings; ChromaDB + cosine survives only as the rollback backend.
