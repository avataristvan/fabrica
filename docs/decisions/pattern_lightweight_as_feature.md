id: pattern_lightweight_as_feature
type: pattern
created: 1778849285.957444
edges: [{"target_id": "pattern_quality_at_write_time", "edge_type": "related"}, {"target_id": "pattern_confidence_lifecycle", "edge_type": "related"}]
---

Rule: ai-mem's lightweight design (ChromaDB + cosine similarity, no local inference, no ML ranker) is a deliberate constraint — not a gap.
When: Evaluating whether to add local inference, a learned ranker, or heavier retrieval machinery.
Why: The reflect ritual and write-time discipline (type tagging, anti-pattern format, TTL, confidence lifecycle) deliver high-quality retrieval without ML complexity. Cosine similarity is sufficient when the collection is well-maintained. ML complexity is only justified when write-time discipline fails at scale (hundreds of entries with high thematic overlap).