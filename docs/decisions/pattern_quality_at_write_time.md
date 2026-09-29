id: pattern_quality_at_write_time
type: pattern
created: 1789255454.224921
edges: [{"target_id": "pattern_lightweight_as_feature", "edge_type": "related"}]
---

Rule: Memory quality is determined at write time (type tagging, anti-pattern format, TTL, reflect ritual, evidence edges) — not by learned re-ranking at retrieval time.
When: Designing or evaluating the ai-mem retrieval pipeline.
Why: The ranker optimizes for retrieval frequency (popularity); write-time discipline enforces epistemic correctness. When the collection is well-maintained, cosine similarity is sufficient. ML complexity is only justified when the write-time gate fails at scale.
Relates to: pattern_lightweight_as_feature, pattern_taxonomy_as_quality_gate, ai_mem_redesign_2026_06_13.
History: until 2026-09-26 the write-time signal named here was 'confidence start value'; confidence/access_count were then dropped as trust signals in favor of confirms/supersedes/contradicts edges and a librarian agent (domain_drop_confidence_for_evidence_and_librarian_2026_09_26).