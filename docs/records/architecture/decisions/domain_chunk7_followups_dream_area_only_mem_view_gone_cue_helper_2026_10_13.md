type: domain
topic: architecture
perspective: agent
created: 1791869829.225011
cue: I look for collection mode, mem-view or where cue normalisation lives after the cutover
---

Decision: DreamMemoryUseCase works on areas only (area_refs required; collection prompts, _shared_collection and _propagation_candidates removed). mem-view (view_cli.py) and memory_index.py are removed. normalize_cue and MAX_CUE_CHARS are a domain helper in ai_mem/domain/memory.py. Collection mode now survives only for the records_v1 migration and `mem-adr-sync reindex --collection`.
Why: The collection internals were unreachable from the CLI. normalize_cue is not part of AddMemoryUseCase because there it would also have to tell None (unchanged) from "" (clear).
Scope: ai-mem main after the cutover. Narrows [domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12](domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12.md) (mem-view is no longer kept). Closes todo_chunk7_simplify_followups_dream_memory_mem_view_normalize_cue_2026_10_12.
Evidence: ai_mem/domain/memory.py (normalize_cue, MAX_CUE_CHARS), ai_mem/application/dream_memory.py.

## Edges

- related: [domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12](domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12.md)
