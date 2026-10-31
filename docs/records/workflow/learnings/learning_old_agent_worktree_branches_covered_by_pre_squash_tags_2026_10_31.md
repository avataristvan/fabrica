id: learning_old_agent_worktree_branches_covered_by_pre_squash_tags_2026_10_31
type: learning
area: workflow
perspective: agent
created: 1793485173.44348
edges: [{"target_id": "pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13", "edge_type": "related"}]
cue: You are cleaning up leftover worktree-agent-* branches from before the history squash.
---

Observed: Old agent worktree branches from before the history squash are covered by the local tags pre-squash-2026-10-13 and pre-cleanup-2026-10-13, so they can be deleted. Check first with `git merge-base --is-ancestor <branch> <tag>`.
Cause: The tags keep the pre-squash history reachable locally, so deleting a covered branch loses no commit.
Evidence: pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13 (names the refs and that they stay local).
