id: pattern_confidence_lifecycle
type: pattern
topic: architecture
created: 1789255454.224921
superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26
valid_until: 1790412164.552887
edges: [{"target_id": "pattern_quality_at_write_time", "edge_type": "related"}, {"target_id": "pattern_lightweight_as_feature", "edge_type": "related"}]
---

Rule: Use confidence (float 0.0–1.0) as the primary lifecycle signal for memory entries — not retrieval frequency.
When: Decisions about boost, decay, proactive injection or promotion of a memory entry.
Why: An ML ranker optimises for popularity (what is retrieved often). Confidence tracks epistemic validity over time: was this memory cited (boost), refuted (decay), or is it so stable that it should always be present (promotion)? These are different questions.
Concretely: mem_boost(delta=+0.1) on reflect citation; the dream report flags decay candidates (<0.3) and promotion candidates (>0.9, access_count≥3, boost_count≥1); hook injection independent of the query for high-confidence entries.
