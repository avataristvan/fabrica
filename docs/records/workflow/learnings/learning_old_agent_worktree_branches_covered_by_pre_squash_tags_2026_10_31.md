type: learning
topic: workflow
perspective: agent
created: 1793485173.44348
cue: You are cleaning up leftover worktree-agent-* branches from before the history squash.
---

Observed: Old agent worktree branches from before the history squash are covered by the local tags pre-squash-2026-10-13 and pre-cleanup-2026-10-13, so they can be deleted. Check first with `git merge-base --is-ancestor <branch> <tag>`.
Cause: The tags keep the pre-squash history reachable locally, so deleting a covered branch loses no commit.
Evidence: [pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13](../../records/decisions/pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13.md) (names the refs and that they stay local).

## Edges

- related: [pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13](../../records/decisions/pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13.md)
