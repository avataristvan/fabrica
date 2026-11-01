id: learning_lint_and_doctor_check_edge_fields_only_body_ids_go_stale_2026_10_31
type: learning
topic: records
perspective: agent
created: 1793486033.21918
edges: [{"target_id": "learning_area_move_invalidates_relative_edges_and_editable_install_2026_10_23", "edge_type": "related"}, {"target_id": "..:todo_build_dev_team_plugin_after_chunk_6a_2026_10_12", "edge_type": "related"}, {"target_id": "domain_mem_move_area_renames_with_references_rename_first_2026_11_01", "edge_type": "related"}]
cue: I am renaming or moving an area folder and trust mem lint and mem doctor to find every stale cross-area reference.
---

Observed: After the ai-mem folder was renamed, the body of todo_build_dev_team_plugin_after_chunk_6a_2026_10_12 (area ai-architecture) still cited `../ai-mem:domain_dev_team_own_plugin_ai_mem_ships_record_parts_2026_10_12`, and lint and mem doctor reported nothing for it.
Cause: Both check only the `edges:` field; ids written in record bodies are not parsed (inferred from the checks' behaviour, not from their code). After a rename or move, grep the old area name across other areas' docs/records bodies, not only the edges.
Evidence: the todo above (fixed 2026-10-31 by a real edge); learning_area_move_invalidates_relative_edges_and_editable_install_2026_10_23.

Addendum 2026-11-01: `mem move-area` now rewrites body references too (text references when the named file exists); see domain_mem_move_area_renames_with_references_rename_first_2026_11_01.
