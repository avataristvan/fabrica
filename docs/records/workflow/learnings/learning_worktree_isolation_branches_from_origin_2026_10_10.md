id: learning_worktree_isolation_branches_from_origin_2026_10_10
type: learning
area: workflow
created: 1791668231.552412
edges: [{"target_id": "learning_worktree_isolation_stale_base_2026_10_10", "edge_type": "confirms"}]
cue: before spawning parallel coders with isolation worktree while local main has unpushed commits
---

Observed: Two coders were spawned with Agent isolation "worktree" while local main was 17 commits ahead of origin. Both worktrees started at origin/main (f5d9757), not at local main (3dfd5c5), so Chunk 0 and Chunk 1a were missing. Both coders stopped at the HEAD check in their prompt. The harness auto-removes unchanged worktrees right away, so fast-forwarding them afterwards was not possible.
Cause: isolation "worktree" branches from the remote default branch, not from the local HEAD.
Evidence: /dev-team step 2 on 2026-10-10. Fixed by having the orchestrator run `git worktree add -b <chunk> .claude/worktrees/<chunk> main` and point the coder at it. After the push (ca9f302) isolation should work again (expected, not yet observed).