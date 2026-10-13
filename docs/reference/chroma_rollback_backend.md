---
status: historical
---
> **Historical.** The Chroma backend, the MCP server and the query daemon no longer exist in the code. This page only says where they went.

# Chroma rollback backend (removed)

Until the plugin cutover ai-mem could run on ChromaDB (`AI_MEM_BACKEND=chroma`) with a Markdown projection and a BM25 hybrid ranker, served by an MCP server and a warm query daemon. The record files became the only store on 2026-10-04 (`domain_file_backend_replaces_chroma_2026_10_04`); the rest was removed with the MCP server (`domain_drop_mcp_server_for_cli_plugin_2026_10_10`).

- **The last commit that still has all of it is the tag `v0-last-mcp`.** `git checkout v0-last-mcp` in a clone gives the server, the daemon, `repository_factory.py` with `ChromaMemoryRepository`/`MarkdownAdrRepository`/`BM25MemoryRepository`, `mem-adr-sync export`/`import`, the push hooks, `agent_context.py`, `session_stats.py`, `injection_log.py`; that version needs `pip install -e . chromadb` (and `rank_bm25` for the hybrid ranker).
- **The ChromaDB store on disk is never deleted or written by ai-mem.** The records_v1 migration (`mem-adr-sync migrate`) reads it read-only with Python's own `sqlite3` and needs no extra package ([how-to](../how-to/migrate-to-records.md)); `$STORE.bak-*` backups stay where they are.
- Facts about the removed stack (cosine from l2 distance, the daemon's locking, what `MarkdownAdrRepository` kept out of the files) are in the tag's copy of this page and in the records of the area (`docs/records/`), not repeated here.
- `memory_index.py` (MEMORY.md auto-demotion, never wired to a trigger) and `mem-view` were removed after the cutover; both are in the tag too.
