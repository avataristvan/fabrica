type: domain
topic: architecture
perspective: user
created: 1792016092.786992
cue: Someone asks whether the plugin rebuild or its target picture is finished, or what is still open from it.
---

Decision: The plugin target picture (docs/target_picture_plugin.md, local only) is implemented and closed as of 2026-10-15. All chunks of docs/plan_plugin_chunks.md are merged. The target picture and the chunk plan stay local as the archive.
Why: The planner decisions resolved its open points: the context map is generated (`mem context --map`); the environment area is the workspace root's docs/records/; `user` stays a kind and also carries `perspective: user`. The earlier idea "framework records go to a separate fabrica folder" is superseded: Fabrica lives in docs/fabrica/ of this repo.
Scope: What remains open lives in todos, not in the target picture. Evidence: docs/sources/handoff_2026_10_13.md, `mem context --help`.

## Edges

- related: [domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13](../../records/decisions/domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13.md)
- related: [domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12](domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12.md)
- related: [domain_fabrica_method_ai_mem_build_user_environment_use_2026_10_13](domain_fabrica_method_ai_mem_build_user_environment_use_2026_10_13.md)
- related: [domain_user_records_as_role_perspective_2026_10_04](domain_user_records_as_role_perspective_2026_10_04.md)
- related: [domain_rebuild_closing_scoped_to_three_todos_2026_10_15](domain_rebuild_closing_scoped_to_three_todos_2026_10_15.md)
- related: [domain_rebuild_closing_scoped_to_two_todos_2026_10_15](domain_rebuild_closing_scoped_to_two_todos_2026_10_15.md)
