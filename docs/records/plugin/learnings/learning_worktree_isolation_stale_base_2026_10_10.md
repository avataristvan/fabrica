id: learning_worktree_isolation_stale_base_2026_10_10
type: learning
area: plugin
created: 1791666108.851098
edges: [{"target_id": "../ai-architecture:learning_user_facing_artifacts_not_in_scratchpad_2026_10_10", "edge_type": "related"}, {"target_id": "../fabrica:domain_why_travels_with_chunk_spec_2026_10_10", "edge_type": "related"}, {"target_id": "../ai-architecture:pattern_parallel_agents_disjoint_files", "edge_type": "related"}, {"target_id": "pattern_worktree_chunk_copies_git_ignored_files_explicitly_2026_10_12", "edge_type": "related"}, {"target_id": "learning_worktree_base_lagged_main_in_5b2_2026_10_12", "edge_type": "related"}]
---

Observed: Both parallel the-coder spawns with isolation="worktree" (step 1 of the plugin plan) got a worktree at f5d9757, 12 commits behind main 8cf0be3, without file_repository.py or records_migration.py. Each coder noticed it and fast-forwarded with `git merge --ff-only main`, which is not on the allowed git list.
Cause: isolation "worktree" branches from origin/main, not local main (see learning_worktree_isolation_branches_from_origin_2026_10_10). The fast-forward worked here only because the worktrees were still alive.
Evidence: chunk 0 and 1a retro blocks 2026-10-10; merges b6af2be, 54c69fb.