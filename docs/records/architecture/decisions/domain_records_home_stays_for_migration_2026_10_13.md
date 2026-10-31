id: domain_records_home_stays_for_migration_2026_10_13
type: domain
area: architecture
perspective: user
created: 1791926219.342161
edges: [{"target_id": "domain_records_model_replaces_chroma_2026_10_04", "edge_type": "related"}, {"target_id": "domain_archivist_writes_home_and_ancestors_only_2026_10_23", "edge_type": "related"}]
cue: I want to remove the ai-mem-records fallback from ai-mem code because the user's own ai-mem-records is gone.
---

Decision: ai-mem's code keeps the records home (`$AI_MEM_WORKSPACE_ROOT/ai-mem-records/<collection>/`) as a fallback, even after the user dissolves their own `../../ai-mem-records`.
Why: other users' ChromaDB migrations (records_v1, `mem-adr-sync migrate`, `reindex --collection`) write global/workspace/subagent.* there. Dissolving the user's own directory is workspace work, done from a session in the workspace root, not a reason to change ai-mem code.
Scope: collection mode / migration only; remove the fallback only when the migration itself is retired.

Closed, historical since fe8403f (2026-10-31, pushed, with a7ba267): the condition of the Scope line was met. The migration went with 3c64e27 (tag v1-last-upgrade-path carries it); fe8403f then removed the records-home fallback, collection mode, the collection mapping file, AI_MEM_RECORDS_HOME and `mem-adr-sync` altogether (the INDEX rebuild in area mode is `mem lint --fix` and the `mem` write commands). The planned todo for this removal is done and was deleted. See domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31.

pseudonymised for publication, 2026-10-31
