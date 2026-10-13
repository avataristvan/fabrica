id: domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12
type: domain
area: architecture
perspective: the-coder
created: 1791838318.005809
edges: [{"target_id": "domain_drop_mcp_server_for_cli_plugin_2026_10_10", "edge_type": "derived_from"}, {"target_id": "domain_file_backend_replaces_chroma_2026_10_04", "edge_type": "related"}, {"target_id": "domain_chunk7_followups_dream_area_only_mem_view_gone_cue_helper_2026_10_13", "edge_type": "related"}, {"target_id": "learning_public_history_pushed_clean_2026_10_13", "edge_type": "related"}, {"target_id": "pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13", "edge_type": "related"}]
cue: I am about to look for the MCP server, daemon, Chroma/BM25 backend or mem-adr-sync export/import and wonder whether they still exist
---

Decision: The cutover (chunk 7 of the plugin plan) removed the MCP server, the daemon, the unwired push hooks, the server-only use cases, the Chroma/BM25/markdown_adr backends and the AI_MEM_BACKEND=chroma rollback, `mem-adr-sync export/import` and `mem-dream --collection/--expert` (`--area` is required). `pyproject` has `dependencies = []`. Kept: `repo_context` plus the collection mapping (for the migration only; mem-view was removed afterwards, see domain_chunk7_followups_dream_area_only_mem_view_gone_cue_helper_2026_10_13) and the records_v1 migration with the stdlib sqlite reader and no extra. `install.py --plugin-switch` offers removal of the MCP registration and `mcp__ai-mem__*` permissions. The tag `v0-last-mcp` (local) marks the last commit with the MCP stack and is the rollback for humans. `docs/reference/chroma_rollback_backend.md` is now a short historical page pointing at that tag.
Why: Closes todo_drop_chromadb_dependency. The migration had to stay runnable on main because an external installation (auto-updating from git) ran on Chroma on 2026-10-10; that installation's state is still unknown, so the migration code stays until it is known to have migrated.
Scope: ai-mem main after the cutover. The historical page resolves todo_decide_plan_and_rollback_docs_banner_or_sources_2026_10_12 for the rollback doc; the plan docs are local working material outside the repo, so nothing is left to decide there.
Evidence: tag v0-last-mcp; docs/reference/chroma_rollback_backend.md.
