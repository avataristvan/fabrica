id: domain_fabrica_method_ai_mem_build_user_environment_use_2026_10_13
type: domain
area: architecture
perspective: user
created: 1791928797.341307
edges: [{"target_id": "domain_framework_named_fabrica_2026_10_10", "edge_type": "related"}, {"target_id": "pattern_findings_about_outside_files_go_to_their_topic_area_2026_10_13", "edge_type": "related"}, {"target_id": "domain_fabrica_practice_not_process_pattern_language_2026_10_14", "edge_type": "related"}, {"target_id": "domain_plugin_target_picture_implemented_and_closed_2026_10_15", "edge_type": "related"}]
cue: I am deciding whether knowledge belongs to the method, to the tool ai-mem, or to the user environment it is used in
---

Decision: Fabrica is the method level: the framework, including the human-agent role definitions. ai-mem complements it with the agent roles (librarian, archivist, anchor-lint) and the tool. Using ai-mem to configure the user's own environment is a third level. Method knowledge and build knowledge both go to ai-mem's area, because Fabrica lives in the ai-mem repo under docs/fabrica/ (decision of 2026-10-14, user; the separate fabrica area is dissolved). Use knowledge goes to the area of the environment it concerns.
Why: Extends domain_framework_named_fabrica_2026_10_10 (ai-mem is the memory plugin that supports Fabrica; the manifesto draft said the same: "ai-mem is one [tool], the memory plugin for Fabrica"; the manifesto is now folded into docs/fabrica/core.md, draft in docs/sources/fabrica_manifesto_draft_2026_10_10.md). Edges from ai-mem into the method level are lineage and stay; edges between the build and the use level do not exist, so the levels stay apart (user, 2026-10-13). Originally (2026-10-13) method knowledge went to a fabrica area of its own; on 2026-10-14 the user put Fabrica into the ai-mem repo, so method and build share one area and the levels are kept apart by topic and by the absence of edges to the use level.
Scope: choosing the area of a record; the rule for ai-mem sessions is pattern_findings_about_outside_files_go_to_their_topic_area_2026_10_13.
