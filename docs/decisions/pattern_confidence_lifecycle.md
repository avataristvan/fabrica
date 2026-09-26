id: pattern_confidence_lifecycle
type: pattern
created: 1789255454.224921
superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26
valid_until: 1790412164.552887
edges: [{"target_id": "pattern_quality_at_write_time", "edge_type": "related"}, {"target_id": "pattern_lightweight_as_feature", "edge_type": "related"}]
---

Rule: Verwende confidence (float 0.0–1.0) als primäres Lifecycle-Signal für Memory-Entries — nicht Retrieval-Frequenz.
When: Entscheidungen über Boost, Decay, proaktive Injektion oder Promotion eines Memory-Eintrags.
Why: Ein ML-Ranker optimiert für Popularität (was oft abgerufen wird). Confidence trackt epistemische Gültigkeit über Zeit: wurde diese Memory zitiert (Boost), widerlegt (Decay), oder ist sie so stabil dass sie immer präsent sein sollte (Promotion)? Das sind verschiedene Fragen.
Konkret: mem_boost(delta=+0.1) bei Reflect-Zitation; Dream-Report flaggt Decay-Kandidaten (<0.3) und Promotion-Kandidaten (>0.9, access_count≥3, boost_count≥1); Hook-Injektion unabhängig von Query für high-confidence Entries.