id: domain_plugin_target_picture_implemented_and_closed_2026_10_15
type: domain
topic: architecture
perspective: user
created: 1792016092.786992
edges: [{"target_id": "domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13", "edge_type": "related"}, {"target_id": "domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12", "edge_type": "related"}, {"target_id": "domain_fabrica_method_ai_mem_build_user_environment_use_2026_10_13", "edge_type": "related"}, {"target_id": "domain_user_records_as_role_perspective_2026_10_04", "edge_type": "related"}, {"target_id": "domain_rebuild_closing_scoped_to_three_todos_2026_10_15", "edge_type": "related"}, {"target_id": "domain_rebuild_closing_scoped_to_two_todos_2026_10_15", "edge_type": "related"}]
cue: Someone asks whether the plugin rebuild or its target picture is finished, or what is still open from it.
---

Decision: The plugin target picture (docs/target_picture_plugin.md, local only) is implemented and closed as of 2026-10-15. All chunks of docs/plan_plugin_chunks.md are merged. The target picture and the chunk plan stay local as the archive.
Why: The planner decisions resolved its open points: the context map is generated (`mem context --map`); the environment area is the workspace root's docs/records/; `user` stays a kind and also carries `perspective: user`. The earlier idea "framework records go to a separate fabrica folder" is superseded: Fabrica lives in docs/fabrica/ of this repo.
Scope: What remains open lives in todos, not in the target picture. Evidence: docs/handoff-2026-10-13.md, `mem context --help`.
