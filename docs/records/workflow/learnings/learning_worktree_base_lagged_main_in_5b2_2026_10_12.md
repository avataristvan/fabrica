id: learning_worktree_base_lagged_main_in_5b2_2026_10_12
type: learning
area: workflow
perspective: the-coder
created: 1791786665.629037
edges: [{"target_id": "learning_worktree_isolation_stale_base_2026_10_10", "edge_type": "confirms"}, {"target_id": "pattern_worktree_chunk_copies_git_ignored_files_explicitly_2026_10_12", "edge_type": "related"}]
cue: Starting a coder in a worktree after earlier chunks were merged to local main
---

Observed: The worktree agent of a docs chunk started from a base that lagged behind main and lacked the preceding chunk. The coder had to fast-forward to main before starting.
Cause: Same as in earlier chunks: the worktree is not branched from current local main.
Evidence: that chunk's retro; learning_worktree_isolation_stale_base_2026_10_10, learning_worktree_isolation_branches_from_origin_2026_10_10.
