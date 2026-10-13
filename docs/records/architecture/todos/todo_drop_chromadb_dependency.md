id: todo_drop_chromadb_dependency
type: todo
area: architecture
created: 1791111270.221233
superseded_by: domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12
valid_until: 1791838385.931228
edges: [{"target_id": "domain_file_backend_replaces_chroma_2026_10_04", "edge_type": "derived_from"}, {"target_id": "domain_drop_mcp_server_for_cli_plugin_2026_10_10", "edge_type": "related"}, {"target_id": "domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12", "edge_type": "related"}]
---

TODO: Remove the Chroma rollback: chromadb dependency, chroma_repository, markdown_adr_repository, bm25_repository, daemon/daemon_client, experience_index, the unwired posttool/pretool/userprompt hook modules, and their tests. Known external installation (an acquaintance of the user) still runs on Chroma as of 2026-10-10, and an agent there auto-updates ai-mem from git. So the records_v1 migration has to stay runnable on main (lazy optional chromadb import), and UPGRADING.md plus a guard must land before anything breaking. Only after that installation has migrated may the migration code go too.