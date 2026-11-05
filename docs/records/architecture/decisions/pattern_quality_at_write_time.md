type: pattern
topic: architecture
created: 1789255454.224921
---

Rule: Memory quality is determined at write time (type tagging, anti-pattern format, TTL, reflect ritual, evidence edges) — not by learned re-ranking at retrieval time.
When: Designing or evaluating the ai-mem retrieval pipeline.
Why: The ranker optimizes for retrieval frequency (popularity); write-time discipline enforces epistemic correctness. When the collection is well-maintained, cosine similarity is sufficient. ML complexity is only justified when the write-time gate fails at scale.
Relates to: [pattern_lightweight_as_feature](pattern_lightweight_as_feature.md), [pattern_taxonomy_as_quality_gate](pattern_taxonomy_as_quality_gate.md), [ai_mem_redesign_2026_06_13](../../general/decisions/ai_mem_redesign_2026_06_13.md).
History: until 2026-09-26 the write-time signal named here was 'confidence start value'; confidence/access_count were then dropped as trust signals in favor of confirms/supersedes/contradicts edges and a librarian agent ([domain_drop_confidence_for_evidence_and_librarian_2026_09_26](domain_drop_confidence_for_evidence_and_librarian_2026_09_26.md)).

## Edges

- related: [pattern_lightweight_as_feature](pattern_lightweight_as_feature.md)
- related: [domain_archivist_write_threshold_2026_10_19](domain_archivist_write_threshold_2026_10_19.md)
