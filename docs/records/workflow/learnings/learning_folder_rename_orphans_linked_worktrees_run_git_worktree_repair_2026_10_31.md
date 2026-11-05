type: learning
topic: workflow
perspective: agent
created: 1793486034.692296
cue: I am renaming or moving a repo folder that has linked git worktrees under .claude/worktrees.
---

Observed: After the repo folder was renamed, a linked worktree (.claude/worktrees/agent-a3b9466a03ee8635a) was orphaned and was deleted on 2026-10-31.
Cause: A linked worktree's `.git` file holds an absolute path to the main checkout, so a folder move breaks it (known git behaviour; not tested here). `git worktree repair` after the move fixes the links.
Evidence: the worktree named above (deleted 2026-10-31); related [learning_mem_in_a_worktree_reports_on_the_main_checkouts_records_2026_10_31](learning_mem_in_a_worktree_reports_on_the_main_checkouts_records_2026_10_31.md).

Addendum 2026-11-01: `mem move-area` reports linked worktrees, it does not repair them ([domain_mem_move_area_renames_with_references_rename_first_2026_11_01](../../records/decisions/domain_mem_move_area_renames_with_references_rename_first_2026_11_01.md)).

## Edges

- related: [learning_area_move_invalidates_relative_edges_and_editable_install_2026_10_23](../../records/learnings/learning_area_move_invalidates_relative_edges_and_editable_install_2026_10_23.md)
- related: [domain_mem_move_area_renames_with_references_rename_first_2026_11_01](../../records/decisions/domain_mem_move_area_renames_with_references_rename_first_2026_11_01.md)
