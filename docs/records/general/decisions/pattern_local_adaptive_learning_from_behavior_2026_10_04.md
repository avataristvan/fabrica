id: pattern_local_adaptive_learning_from_behavior_2026_10_04
type: domain
topic: general
perspective: user
created: 1791067532.967105
edges: [{"target_id": "domain_drop_confidence_for_evidence_and_librarian_2026_09_26", "edge_type": "related"}, {"target_id": "domain_file_backend_replaces_chroma_2026_10_04", "edge_type": "related"}]
cue: Proposing a cloud service, a pretrained embedding model or hand-labelled data for ai-mem
---

Decision: ai-mem keeps record data local and uses no pretrained embedding model. Both hold today. The third part of the original philosophy, learning from real behavior (passive labels, an adaptive ranker), is superseded.

Why: Records are plain files in the user's own repos and are never uploaded; the user keeps control of what the system knows. Retrieval is keyword overlap plus judgment by the librarian and archivist, so no embedding model is needed. "No cloud" holds for the record data only: the librarian and archivist call a cloud model, which reads the records it is given.

Superseded: learning from real behavior and passive labels. The ML ranker was removed, and trust now rests on traceable evidence edges and the librarian's judgment rather than on scores learned from usage (domain_drop_confidence_for_evidence_and_librarian_2026_09_26, domain_librarian_replaces_experience_index_2026_10_04, domain_file_backend_replaces_chroma_2026_10_04). Do not propose behavior-learned ranking or passive labels on the strength of this record.

Scope: ai-mem design decisions overall.

Evidence: domain_drop_confidence_for_evidence_and_librarian_2026_09_26 (ranker and score removal), domain_file_backend_replaces_chroma_2026_10_04 (files as the only store).
