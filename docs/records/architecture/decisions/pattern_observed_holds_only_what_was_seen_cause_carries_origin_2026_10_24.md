id: pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24
type: pattern
topic: architecture
perspective: user
created: 1792868078.426736
edges: [{"target_id": "domain_three_kinds_of_knowledge_age_differently_2026_10_10", "edge_type": "related"}, {"target_id": "domain_drop_confidence_for_evidence_and_librarian_2026_09_26", "edge_type": "related"}]
cue: I am writing or reading a record whose observation comes with an explanation, and about to take that explanation as fact.
---

Rule: The Observed field of a record holds only what was seen. Every attribution of a cause belongs in the Cause field, with its origin (who said it, or what it was inferred from) and its status (open or backed). A reader treats a cause without origin and status as unchecked.
When: The archivist writes or integrates a record whose observation carries an explanation; anyone reads a record and is about to use its cause as a premise.
Why: In hw-projekt-T an agent's guess ("the PMIC manual reset causes that reboot") stood without origin in the Observed field of a perspective:user record, so the whole sentence read as the user's observation. The librarian quoted it correctly, the asking agent took it over as a premise, and only the user's follow-up question exposed it. The later in-place fix is the model: Observed "was seen to ...", Cause "first attributed to ..., not backed by ..., cause open", plus a learning and a todo for the deciding test.
Evidence: docs/sources/field_feedback_librarian_archivist_hw_project_2026_10_24.md (part 2, points 1 and 2). To be carried into agents/archivist.md and the field semantics in docs/reference/record-format.md.
