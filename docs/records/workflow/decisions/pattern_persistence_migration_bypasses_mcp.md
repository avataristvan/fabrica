type: pattern
topic: workflow
created: 1790678885.521196
---

Rule: A migration that changes ai-mem's persistence layer or file layout runs via the Python API with the same repository stack as the server (ChromaMemoryRepository + MarkdownAdrRepository + AddMemoryUseCase/AddEdgeUseCase), never via MCP mem_* tools. Beforehand a backup of the store (copy only), afterwards reconnect the MCP server in all open sessions.
When: After a code commit that changes how or where ai-mem stores entries (file paths, frontmatter, types), and existing entries are to be rewritten.
Why: Running MCP servers keep old code, and the tool schema in the client may be stale; writing through them produces entries in the old layout.

Status 2026-10-04: Build the current stack with repository_factory.build_repository(); mem-adr-sync migrate (ai_mem/infrastructure/records_migration.py) is the canonical example.

## Edges

- derived_from: [learning_mcp_servers_keep_old_code_and_cached_schema_2026_09_29](../learnings/learning_mcp_servers_keep_old_code_and_cached_schema_2026_09_29.md)
- related: [learning_migrate_apply_exit1_has_two_meanings_2026_10_11](../learnings/learning_migrate_apply_exit1_has_two_meanings_2026_10_11.md)
