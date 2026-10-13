id: pattern_worktree_chunk_copies_git_ignored_files_explicitly_2026_10_12
type: pattern
area: workflow
perspective: the-coder
created: 1791758109.126924
edges: [{"target_id": "learning_worktree_isolation_stale_base_2026_10_10", "edge_type": "related"}, {"target_id": "learning_worktree_base_lagged_main_in_5b2_2026_10_12", "edge_type": "related"}, {"target_id": "learning_editable_install_python_i_resolves_main_checkout_not_worktree_2026_10_12", "edge_type": "related"}]
cue: Starting or finishing a worktree chunk that reads or writes a git-ignored file
---

Rule: Git-ignored files exist only in the main checkout. A worktree chunk that needs one must have it copied in explicitly; the orchestrator copies git-ignored outputs back to the main checkout before it removes the worktree.
When: Spawning a coder with isolation "worktree", and when removing the worktree afterwards.
Why: The worktree is a fresh checkout, so ignored files are absent there, and removing the worktree deletes ignored outputs for good (git cannot restore them). Case: a private, git-ignored source file under docs/sources/ needed by a docs chunk.
Evidence: see learning_worktree_isolation_stale_base_2026_10_10 for the other worktree pitfall.
