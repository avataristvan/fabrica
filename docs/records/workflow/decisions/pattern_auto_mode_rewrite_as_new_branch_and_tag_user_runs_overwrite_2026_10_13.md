id: pattern_auto_mode_rewrite_as_new_branch_and_tag_user_runs_overwrite_2026_10_13
type: pattern
area: workflow
perspective: agent
created: 1791889506.054793
edges: [{"target_id": "pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13", "edge_type": "related"}]
cue: An agent in auto mode has to rewrite local git history, and reset or tag -f is blocked
---

Rule: Build the rewritten target as a new branch and a new tag (git commit-tree onto origin/main) and leave the one overwrite command to the user.
When: Auto mode blocks destructive git (reset, tag -f) and local history must be rewritten.
Why: It worked cleanly on 2026-10-13: nothing was destroyed by the agent, the old refs stayed as a safety net, and the user decided the single destructive step.
