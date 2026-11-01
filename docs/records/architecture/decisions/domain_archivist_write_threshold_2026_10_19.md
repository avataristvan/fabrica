id: domain_archivist_write_threshold_2026_10_19
type: domain
topic: architecture
perspective: agent
created: 1792419303.538902
edges: [{"target_id": "pattern_knowledge_distribution_rule_2026_10_04", "edge_type": "related"}, {"target_id": "pattern_quality_at_write_time", "edge_type": "derived_from"}, {"target_id": "domain_archivist_may_retype_weak_confirms_2026_10_23", "edge_type": "related"}, {"target_id": "domain_archivist_writes_home_and_ancestors_only_2026_10_23", "edge_type": "related"}]
cue: I am deciding whether a reflect candidate deserves a record at all, or why the archivist dropped one
---

Decision: The archivist applies a write threshold. A candidate becomes a record only when it is not derivable from code, docs or another record and would surprise someone without its context. A decision record also needs a real trade-off (an alternative weighed or rejected). Hard to reverse raises the weight but is not required: cheap-to-undo decisions still carry a "why" someone asks about later. Bodies stay short, 1-3 sentences per field.
Why: Quality is set at write time (pattern_quality_at_write_time), and derivable material only adds noise the librarian must sift. Adapted from Matt Pocock's ADR criteria (github.com/mattpocock/skills, skills/engineering/domain-modeling/ADR-FORMAT.md), handed over by the ai-architecture session 2026-10-19; the user delegated the decision to the agent.
Scope: agents/archivist.md Procedure step 1 (what is kept or dropped). Does not change the record formats.
