id: domain_archivist_writes_home_and_ancestors_only_2026_10_23
type: domain
area: architecture
perspective: user
created: 1792761669.127496
edges: [{"target_id": "pattern_findings_about_outside_files_go_to_their_topic_area_2026_10_13", "edge_type": "related"}, {"target_id": "domain_records_home_stays_for_migration_2026_10_13", "edge_type": "related"}, {"target_id": "domain_archivist_write_threshold_2026_10_19", "edge_type": "related"}]
cue: I am an archivist about to write a record whose topic belongs to a nested, sibling or other project area.
---

Decision: The archivist writes only into its home area and the areas above it, up to the root (e.g. the workspace root `../..`, which holds global and agent knowledge). It never writes down into a nested area, nor into sibling or other project areas. The one exception is back-references, allowed in any direction. A record whose topic belongs to an area below or beside is not written but reported as "not written: belongs to <area>", for a session in that area to pick up.
Why: User, 2026-10-23: global = the workspace root area; agents' records (today ai-mem-records/subagent.the-coder) move to workspace/docs/records; other projects only when changes in the project are needed from a subproject session; "wenn ich im Root oder einem Project mit subprojects bin, darf der archivist nicht down-bubblen". The scope follows from the folder hierarchy, so no machine-local topology file (considered: $AI_MEM_PATH/write_scope.json) is needed. Cost accepted: findings about a sub-area's topic made from above are deferred, not written. This narrows pattern_findings_about_outside_files_go_to_their_topic_area_2026_10_13 (which routes by topic) to "route by topic, but only upward; otherwise report"; judged related, not a contradiction.
Scope: Archivist writes. Enforced in `mem` (refuse writes outside home + ancestors, except back-references) and stated in agents/archivist.md, both done by the coding session. Depends on the ai-mem-records migration (handed to the session in the workspace root, 2026-10-23; see domain_records_home_stays_for_migration_2026_10_13).

pseudonymised for publication, 2026-10-31
