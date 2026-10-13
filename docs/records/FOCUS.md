The rebuild (plugin on plain record files, MCP server and Chroma removed) is closed. Public: main and the tag `v0-last-mcp` (the cleaned rollback point). Internal working material (raw eval transcripts, chunk plan, target picture, handoffs) stays local via `.git/info/exclude`; local tags `pre-cleanup-*`, `pre-squash-*`, `v0-last-mcp-unclean` and the `worktree-agent-*` branch still hold the old history and must never be pushed.

The archivist acceptance is closed without a rerun (domain_archivist_acceptance_closed_fail_use_carries_2026_10_13); its two gaps are todos.

Open work is the todo backlog; candidates for a next step: the `mem doctor` scan for private names, machine paths and unpushed SHAs, the archivist's records-home search and cross-area duplicate check, and a dead-weight pass over the older todos.
