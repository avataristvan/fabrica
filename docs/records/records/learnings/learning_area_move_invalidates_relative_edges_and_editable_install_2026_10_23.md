type: learning
topic: records
perspective: agent
created: 1792747177.637129
cue: I am moving or renaming an area folder (or the repo) and assume mem and its records keep working afterwards.
---

Observed: After ai-mem moved under ai-architecture/, 11 cross-area edges dangled (written with pre-move relative prefixes) and the pyenv editable install still mapped ai_mem to the old path, so `mem` on PATH failed with ModuleNotFoundError.
Cause: Relative area paths in edges and editable installs both encode the folder location; moving an area invalidates them silently. Incoming edges from other areas are affected too (mem move already notes this for single records).
Evidence: mem doctor 2026-10-23 (edge-dangling-xarea 6, edge-unresolved 5); __editable___ai_mem_0_1_0_finder.py MAPPING pointed to the old folder (ai-mem directly in the workspace root). After the move: run mem doctor --root <workspace root>, rewrite edges with mem unlink + mem link, reinstall the editable package.

pseudonymised for publication, 2026-10-31

Addendum 2026-11-01: `mem move-area` now rewrites the edges and text references; the editable install is only reported, not touched ([domain_mem_move_area_renames_with_references_rename_first_2026_11_01](../decisions/domain_mem_move_area_renames_with_references_rename_first_2026_11_01.md)).

## Edges

- related: [domain_repo_renamed_fabrica_folder_and_plugin_stay_2026_10_15](../../architecture/decisions/domain_repo_renamed_fabrica_folder_and_plugin_stay_2026_10_15.md)
- related: [domain_plugin_renamed_fabrica_package_and_cli_keep_names_2026_10_31](../../architecture/decisions/domain_plugin_renamed_fabrica_package_and_cli_keep_names_2026_10_31.md)
- related: [learning_lint_and_doctor_check_edge_fields_only_body_ids_go_stale_2026_10_31](learning_lint_and_doctor_check_edge_fields_only_body_ids_go_stale_2026_10_31.md)
- related: [learning_folder_rename_orphans_linked_worktrees_run_git_worktree_repair_2026_10_31](../../workflow/learnings/learning_folder_rename_orphans_linked_worktrees_run_git_worktree_repair_2026_10_31.md)
- related: [domain_mem_move_area_renames_with_references_rename_first_2026_11_01](../decisions/domain_mem_move_area_renames_with_references_rename_first_2026_11_01.md)
