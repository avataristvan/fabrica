id: pattern_findings_about_outside_files_go_to_their_topic_area_2026_10_13
type: pattern
area: architecture
perspective: user
created: 1791926513.704019
edges: [{"target_id": "domain_agents_learn_environment_never_edit_external_2026_10_11", "edge_type": "related"}, {"target_id": "../fabrica:domain_area_path_is_the_address_of_knowledge_2026_10_10", "edge_type": "derived_from"}, {"target_id": "pattern_rewiring_grep_old_collection_names_2026_10_11", "edge_type": "related"}]
cue: I am integrating candidates from an ai-mem session that configured the user's environment rather than building ai-mem.
---

Rule: Separate two levels of work in an ai-mem session. Building ai-mem (the plugin code, its agents, skills, docs, evals) -> records go to ai-mem. Using ai-mem as the tool to configure the user's environment (wiring the user's own global skills or commands into the handoff protocol, /ai-mem:setup on a project, cleaning another store) -> findings and decisions go to the environment's area (workspace root area, ai-mem-records/global, or the configured project's area), even when the session runs in the ai-mem repo. Archivist: choose the area by the level and topic of the work, not by the session's repo.
When: Integrating candidates from an ai-mem session that configured the user's environment (e.g. rewiring the persona skills or dev-team) rather than building ai-mem.
Why: Using the tool to configure an environment is a different level from building the tool (user, 2026-10-13). Two persona todos were filed in ai-mem on 2026-10-11, had to be closed again, and their names went public with ai-mem's history. Editing the user's own config at this level is legitimate when asked; the "never edit" rule in domain_agents_learn_environment_never_edit_external_2026_10_11 concerns external third-party agents and does not apply. If the target area is unclear or not writable, report the candidate to the caller instead of filing it in ai-mem.
Evidence: user statement 2026-10-13; pattern_rewiring_grep_old_collection_names_2026_10_11 (cleaned of the leak); fabrica:domain_area_path_is_the_address_of_knowledge_2026_10_10.
