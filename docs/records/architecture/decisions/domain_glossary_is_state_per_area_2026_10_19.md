id: domain_glossary_is_state_per_area_2026_10_19
type: domain
topic: architecture
perspective: agent
created: 1792419303.863204
edges: [{"target_id": "domain_handoff_points_instead_of_copying_2026_10_19", "edge_type": "related"}, {"target_id": "domain_three_kinds_of_knowledge_age_differently_2026_10_10", "edge_type": "related"}, {"target_id": "domain_record_key_topic_replaces_area_2026_11_01", "edge_type": "related"}]
cue: I coin a new term, or notice two sessions using one word differently
---

Decision: Each area may keep a glossary at docs/reference/glossary.md (ai-mem has one). It is state, like FOCUS.md: overwritten in place by the session that coins or changes a term (/reflect Step 5), free of implementation details, with a "not to be confused with" column. The reason for a term change goes to the archivist as a candidate.
Why: Chosen over glossary-as-records because term meanings are current truth, not history; chosen over the per-briefing terminology table (target_picture_plugin.md) because that one dies with the briefing. Seeded from that table; it surfaces an existing clash: the frontmatter key area: names the topic folder, not the area. Source: Pocock's domain-modeling skill (glossary maintained live during the session).
Scope: docs/reference/glossary.md, skills/reflect/SKILL.md Step 5.
