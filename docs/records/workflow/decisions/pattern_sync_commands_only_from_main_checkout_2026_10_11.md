id: pattern_sync_commands_only_from_main_checkout_2026_10_11
type: pattern
topic: workflow
perspective: the-coder
created: 1791738307.581806
edges: [{"target_id": "learning_bang_commands_have_no_stdin_2026_10_12", "edge_type": "related"}]
cue: I am about to run install.py --sync-commands or --plugin-switch while working in a git worktree
---

Rule: Run install.py --sync-commands and install.py --plugin-switch only from the main checkout, never from a worktree.
When: Installing or syncing commands/agents, or switching to the plugin, while working with worktrees.
Why: The symlinks --sync-commands creates point at the checkout that ran it; from a worktree they would dangle once the worktree is removed. For --plugin-switch, REPO_ROOT is the worktree, so links into the main checkout are not seen.
