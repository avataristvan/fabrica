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

pseudonymised for publication, 2026-10-31
