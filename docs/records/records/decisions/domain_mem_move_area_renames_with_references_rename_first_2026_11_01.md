id: domain_mem_move_area_renames_with_references_rename_first_2026_11_01
type: domain
topic: records
perspective: agent
created: 1793524156.850862
edges: [{"target_id": "pattern_batch_referrer_rewrite_needs_versioned_areas_2026_10_12", "edge_type": "confirms"}, {"target_id": "learning_area_move_invalidates_relative_edges_and_editable_install_2026_10_23", "edge_type": "derived_from"}, {"target_id": "learning_lint_and_doctor_check_edge_fields_only_body_ids_go_stale_2026_10_31", "edge_type": "related"}, {"target_id": "learning_folder_rename_orphans_linked_worktrees_run_git_worktree_repair_2026_10_31", "edge_type": "related"}]
cue: You are about to rename or move an area or repo folder and its records hold edges and text references to it.
---

Decision: `mem move-area OLD NEW --root DIR` renames or moves an area folder deterministically and rewrites every edge and text reference into and out of it (nested areas included; text references only when the named file exists). It renames first, then writes, so a failed rename leaves nothing written (a reviewer found the reverse order unsafe). It refuses a hand-kept INDEX.md and areas without git unless --include-unversioned. Machine state (worktrees, editable install, Claude Code project memory, config files) is reported, never touched.
Why: Renaming a repo can happen again (user's idea); by hand, 11 edges dangled once and body references went stale. The refusal rule extends pattern_batch_referrer_rewrite_needs_versioned_areas_2026_10_12 to other areas' referrers with an explicit override. That pattern came from the librarian's answer on area moves (no prior tool) and held again here.
Scope: area and repo folder renames. Evidence: edaebd7; verified on a copy of the real workspace (23 references in 19 records, mem doctor unchanged afterwards).
