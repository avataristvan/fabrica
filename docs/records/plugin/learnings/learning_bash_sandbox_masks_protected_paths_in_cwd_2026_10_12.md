type: learning
topic: plugin
perspective: agent
created: 1791838323.276697
cue: I am running an unattended claude -p agent in the Bash sandbox and it stops because git status shows a dirty tree
---

Observed: Claude Code's Bash sandbox masks protected paths in its cwd (.bashrc, .bash_profile, .profile, .zshrc, .gitconfig, .mcp.json, .idea, .vscode, .claude/ ...) with /dev/null bind mounts. `git status` in that cwd lists them as untracked, and an agent following "stop if the tree is dirty" stops. Run sandboxed agents with the cwd one level above the checkout (writes are still allowed below it). Strict settings: `{"sandbox": {"enabled": true, "failIfUnavailable": true, "allowUnsandboxedCommands": false, "network": {"allowedDomains": ["pypi.org", "files.pythonhosted.org"]}}}`; writes default to cwd, --add-dir dirs and temp.
Cause: bwrap bind-mounts /dev/null over the protected paths that exist (or are created) in the cwd, so they appear as new untracked files.
Evidence: scripts/upgrade_acceptance/README.md. Verified on Claude Code 2.1.296, Linux bwrap.

## Edges

- related: [learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12](learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12.md)
