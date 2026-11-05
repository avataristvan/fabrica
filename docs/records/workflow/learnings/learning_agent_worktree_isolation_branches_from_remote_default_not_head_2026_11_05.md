type: learning
topic: workflow
perspective: agent
created: 1793905718.251617
cue: You are spawning agents with isolation worktree while local main is ahead of origin or has uncommitted files.
---

Observed: Claude Code's Agent isolation "worktree" branches by default (`worktree.baseRef: "fresh"`) from the remote default branch, not from local HEAD, so unpushed commits and uncommitted files are missing in the worktree. On 2026-11-05 three background agents got worktrees on origin/main (d91b3ef) while main (6f40c13) was 4 commits ahead with the whole link migration.
Cause: The default base is the remote default branch (documented under "Choose the base branch" at code.claude.com/docs/en/worktrees.md).
Evidence: `git rev-parse origin/main` = d91b3ef vs main 6f40c13 at the time; the worktrees docs page above. Instead: commit first and set `worktree.baseRef: "head"` in the project settings, or check the base with `git merge-base` before spawning; hand specs by absolute main-checkout path.

## Edges

- related: [learning_editable_install_python_i_resolves_main_checkout_not_worktree_2026_10_12](learning_editable_install_python_i_resolves_main_checkout_not_worktree_2026_10_12.md)
