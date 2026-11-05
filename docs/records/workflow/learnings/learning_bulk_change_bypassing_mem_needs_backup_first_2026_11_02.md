type: learning
topic: workflow
perspective: agent
created: 1793657748.289373
cue: I am about to change records in bulk across areas or repos, especially with a script that bypasses the mem CLI.
---

Observed: Git is no safety net everywhere: 5 repos do not version docs/records (a-i-d-e, kitchen-chat-mcp, post-production, looper, okkularion) and 2 areas have no git at all (workspace root, ExoDeck-project/filmproduction). Other sessions leave uncommitted records in the same folders, so a commit must stage per file (a diff filter on the changed frontmatter lines worked).
Cause: Repo layout, not a fault; a script+Haiku migration without mem has no undo outside git.
Evidence: backup of the 74 deleted todos in ~/.local/share/ai-mem.bak-todos-2026-11-02/. Rule: back up before the change, stage per file.
