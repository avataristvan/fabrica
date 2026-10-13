id: todo_archivist_report_names_searched_areas_2026_10_11
type: todo
area: architecture
perspective: user
created: 1791745728.959503
edges: [{"target_id": "domain_archivist_acceptance_closed_fail_use_carries_2026_10_13", "edge_type": "related"}, {"target_id": "domain_archivist_who_what_how_2026_10_10", "edge_type": "related"}]
cue: I am changing agents/archivist.md or judging whether an archivist report searched the records home and other areas.
---

TODO: Make the archivist's search of the records home (ai-mem-records/global, workspace, user/) observable or enforced. Its definition says to search it (steps 3 and 6), but in the acceptance run it mapped the areas and read only one file there, so it found 0/4 predecessors. Lever: the report names the areas it searched, so a missed predecessor is visible. Measure in real use whether it raises the rate of cross-area edges. (The acceptance eval was closed on 2026-10-13, see domain_archivist_acceptance_closed_fail_use_carries_2026_10_13.)
