type: domain
topic: plugin
perspective: the-coder
created: 1791833918.959855
cue: Someone asks how a new project gets its first records now that /mem-init is gone
---

Decision: The setup skill (`ai-mem:setup`, successor of /mem-init) does no seeding and writes no records. The first records of a project come from work via `/ai-mem:reflect` and the archivist, or by hand from the tutorial.
Why: Only the archivist and the user write records; seeding by exploration would bypass the archivist. The librarian found no earlier record deciding this.
Scope: skills/setup/SKILL.md.
Evidence: docs/sources/automation_repo_seeder.md (the retired seeder this replaces)

## Edges

- related: [domain_archivist_mechanism_mem_and_mem_dream_2026_10_11](../../architecture/decisions/domain_archivist_mechanism_mem_and_mem_dream_2026_10_11.md)
- related: [domain_dream_proposes_never_applies_2026_10_13](../../workflow/decisions/domain_dream_proposes_never_applies_2026_10_13.md)
