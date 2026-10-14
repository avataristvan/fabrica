id: domain_archivist_integration_visible_to_navigator_2026_10_15
type: domain
area: architecture
perspective: user
created: 1792016093.02779
edges: [{"target_id": "domain_archivist_who_what_how_2026_10_10", "edge_type": "related"}, {"target_id": "todo_split_manifest_and_name_framework", "edge_type": "related"}]
cue: Someone worries the archivist changes the records without the human seeing it.
---

Decision: Mutual visibility is resolved: the archivist does not integrate silently. /reflect shows the archivist's integration report to the Navigator, who corrects placements through the archivist.
Why: The human must see every change to the record; the report is the point where placement errors are caught.
Scope: Stated in skills/reflect/SKILL.md (step 7) and in the Archivist row of the roles table in docs/fabrica/core.md.
