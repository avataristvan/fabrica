type: domain
topic: architecture
created: 1791613170.126814
---

Decision: The MCP server (server.py, mem_* tools) is dropped. ai-mem becomes a Claude Code plugin without .mcp.json: a stdlib CLI for write access (format/path validation), reading via Read/Glob/Grep and the librarian, agents/skills/SessionStart hook as plugin components, plus a setup assistant that builds the framework into the user's own workflows.
Why: The value has shifted from the tool to the practice (records in the repo, fixed retrieval points at handoffs, judgment instead of score). The effective change (librarian in the dev-team review) was conceptual and structural, no tool could have delivered it. The server costs restarts, stale code in running sessions and the dependencies mcp/chromadb; the file path needs only the stdlib.
Scope: Changes todo_plugin_packaging (planned there still with .mcp.json and venv bootstrap). Connected with todo_drop_chromadb_dependency. The ChromaDB storage on disk remains untouched.

## Edges

- derived_from: [domain_file_backend_replaces_chroma_2026_10_04](domain_file_backend_replaces_chroma_2026_10_04.md)
- derived_from: [domain_librarian_at_review_handoff_2026_10_10](../../retrieval/decisions/domain_librarian_at_review_handoff_2026_10_10.md)
- related: [learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12](../../plugin/learnings/learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12.md)
- related: [learning_guard_on_old_backend_artefact_silenced_sessionstart_2026_10_12](../../plugin/learnings/learning_guard_on_old_backend_artefact_silenced_sessionstart_2026_10_12.md)
- related: [domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12](domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12.md)
- related: [domain_record_edges_single_line_json_with_ids_2026_10_23](../../records/decisions/domain_record_edges_single_line_json_with_ids_2026_10_23.md)
