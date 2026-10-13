id: fix_workspace_collection_catchall_2026_07_31
type: domain
area: architecture
created: 1789252784.944877
edges: [{"target_id": "learning_workspace_collection_catchall_dumped_unrelated_entries_2026_07_31", "edge_type": "derived_from"}]
---

Fix (2026-07-31): a directory that has its own CLAUDE.md but falls outside `AI_MEM_WORKSPACE_ROOT` (or the var is unset) and is not a git repo used to land in the catch-all `WORKSPACE_COLLECTION` and pull in unrelated entries. It now scopes by the directory's own name instead (`repo.<dirname>`, sanitized) -- mirrors the existing git-repo-without-a-remote fallback (`repo.<git_root.name>`) one level earlier. `WORKSPACE_COLLECTION` is now reserved for only two cases: no CLAUDE.md exists anywhere, or CLAUDE.md sits directly at the workspace root itself.
Observation and root cause: learning_workspace_collection_catchall_dumped_unrelated_entries_2026_07_31.
See also: arch_workspace_root_collection_naming, fix_workspace_focus_false_negative, collections_scoping.