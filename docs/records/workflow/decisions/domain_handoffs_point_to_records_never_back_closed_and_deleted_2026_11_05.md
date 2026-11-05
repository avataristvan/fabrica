type: domain
topic: workflow
perspective: user
created: 1793885900.643847
cue: You are writing a record whose evidence lives in a handoff, or closing or deleting a handoff.
---

Decision: Handoffs point to records, never the other way round. A handoff is short-lived state: once its work is done or a newer one replaces it, it is closed and deleted. Open points go to FOCUS.md/BACKLOG.md, conclusions become record candidates, and evidence in it (measurements, experiment results) is first frozen as a source under docs/sources/. A record cites the source, never the handoff. Measurements and experiment logs get their own file under docs/ from the start. FOCUS/BACKLOG lines carry no ids or numbers; a line's history is `git log -S`. This is a generic plugin rule, not an area convention.
Why: In the galaxy-tab-a-2016 area records cited handoffs and FOCUS/BACKLOG carried dangling todo ids; a deleted handoff then leaves the record without its evidence.
Scope: skills/reflect/SKILL.md Step 5, agents/archivist.md, docs/reference/record-format.md; every area.
Evidence: skills/reflect/SKILL.md Step 5, docs/reference/record-format.md, agents/archivist.md.

## Edges

- confirms: [domain_three_kinds_of_knowledge_age_differently_2026_10_10](../../architecture/decisions/domain_three_kinds_of_knowledge_age_differently_2026_10_10.md)
- related: [domain_handoff_points_instead_of_copying_2026_10_19](domain_handoff_points_instead_of_copying_2026_10_19.md)
- related: [pattern_handoff_is_overwritten_not_appended_2026_10_12](pattern_handoff_is_overwritten_not_appended_2026_10_12.md)
- related: [domain_links_between_code_and_docs_go_from_docs_to_code_2026_11_05](domain_links_between_code_and_docs_go_from_docs_to_code_2026_11_05.md)
