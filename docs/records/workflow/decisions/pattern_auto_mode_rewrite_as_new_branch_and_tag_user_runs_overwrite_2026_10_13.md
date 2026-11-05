type: pattern
topic: workflow
perspective: agent
created: 1791889506.054793
cue: An agent in auto mode has to rewrite local git history, and reset or tag -f is blocked
---

Rule: Build the rewritten target as a new branch and a new tag (git commit-tree onto origin/main) and leave the one overwrite command to the user.
When: Auto mode blocks destructive git (reset, tag -f) and local history must be rewritten.
Why: It worked cleanly on 2026-10-13: nothing was destroyed by the agent, the old refs stayed as a safety net, and the user decided the single destructive step.

## Edges

- related: [pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13](../../records/decisions/pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13.md)
