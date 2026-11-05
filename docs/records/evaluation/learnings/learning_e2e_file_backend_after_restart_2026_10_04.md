type: learning
topic: evaluation
created: 1791134202.528678
---

Observed: After the restart on the file backend everything worked through the real MCP server. SessionStart printed only the routing line and the Records pointer. One mem_add with two ids and type todo wrote two files under docs/records/<area>/todos/ plus INDEX rows. type feedback came back as a readable 'Error: ... is not stored'. mem_boost(cue=...) wrote the cue line into the file. mem_delete removed the files, the emptied area folder and the INDEX rows. The librarian answered a 'why' question with Read/Grep on docs/records only (INDEX.md, a '^cue:' grep, four record files) and no mem_* call. Its answer was correct, plus one embellished side claim about hook latency that no record makes.
Cause: The file backend and the file-first librarian work as designed. A deferred-tool schema in the client can show a stale tool description (mem_get) after a restart, while the server code is current.
Evidence: this session's MCP calls with ids todo_e2e_probe_a/_b (deleted afterwards), the librarian's reported tool calls, ai_mem/server.py mem_get description.

## Edges

- confirms: [domain_file_backend_replaces_chroma_2026_10_04](../../architecture/decisions/domain_file_backend_replaces_chroma_2026_10_04.md)
- confirms: [domain_librarian_replaces_experience_index_2026_10_04](../../architecture/decisions/domain_librarian_replaces_experience_index_2026_10_04.md)
- confirms: [learning_mcp_servers_keep_old_code_and_cached_schema_2026_09_29](../../workflow/learnings/learning_mcp_servers_keep_old_code_and_cached_schema_2026_09_29.md)
- related: [eval_librarian_2026_09_26](eval_librarian_2026_09_26.md)
