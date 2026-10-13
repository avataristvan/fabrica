id: domain_setup_seeds_nothing_first_records_come_from_work_2026_10_12
type: domain
area: plugin
perspective: the-coder
created: 1791833918.959855
edges: [{"target_id": "domain_archivist_mechanism_mem_and_mem_dream_2026_10_11", "edge_type": "related"}, {"target_id": "domain_dream_proposes_never_applies_2026_10_13", "edge_type": "related"}]
cue: Someone asks how a new project gets its first records now that /mem-init is gone
---

Decision: The setup skill (`ai-mem:setup`, successor of /mem-init) does no seeding and writes no records. The first records of a project come from work via `/ai-mem:reflect` and the archivist, or by hand from the tutorial.
Why: Only the archivist and the user write records; seeding by exploration would bypass the archivist. The librarian found no earlier record deciding this.
Scope: skills/setup/SKILL.md.
