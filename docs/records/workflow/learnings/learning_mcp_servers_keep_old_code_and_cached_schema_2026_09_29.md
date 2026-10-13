id: learning_mcp_servers_keep_old_code_and_cached_schema_2026_09_29
type: learning
area: workflow
created: 1790678885.521196
edges: [{"target_id": "pattern_blindtest_methodik", "edge_type": "contradicts"}, {"target_id": "..:feedback_agents_dir_symlink_read_at_start", "edge_type": "related"}]
---

Observed: After a change to the persistence layer (record layout docs/records, commit b0063b8), three ai_mem.server processes from different sessions kept running with old code; every mem_add through them would have written files in the old flat layout. After a session restart a new server process was indeed running (start time after the commit, server.py contains `area` and `derived_from`), but the tool schema shown by Claude Code (ToolSearch) still showed the old schema without the `area` parameter and without `derived_from` in the mem_link enum.
Cause: MCP servers load the code only at start and are started per session; the tool schema is cached on the client side, independently of the restarted server process (exact cache mechanism not investigated). The observation 'one server process per session' holds for the CLI client; for the desktop app it is unverified and may differ.
Evidence: pgrep -af ai_mem.server on the four server processes, ps lstart vs. git log; migration 093dc1b therefore ran via the Python API.
