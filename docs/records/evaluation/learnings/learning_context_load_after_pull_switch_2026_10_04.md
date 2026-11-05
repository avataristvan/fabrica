type: learning
topic: evaluation
created: 1791134292.96881
---

Observed: /context in a fresh session after the switch (1M window) shows ai-mem's fixed cost below ~1k tokens: SessionStart output ~90 tokens (344 chars, was ~925); its 14 tool schemas (~3.8k tokens together, mem_add 742 the largest) are deferred and cost nothing until ToolSearch loads them; the librarian agent definition is 278 tokens; 'MCP server instructions' is 717 tokens for all servers together, of which ai-mem's text is ~1.1k chars (the Claude Docs server's instructions are the larger share -- per-server split not shown). The ai-mem CLAUDE.md (~4.5k chars) and CLAUDE.local.md fall under 'Memory files' (6k for all instruction files) and would be read anyway. Before the switch the same pieces were about hook ~925 + tool schemas ~3.7k (when not deferred) + instructions ~2k tokens.
Cause: Pull switch ([domain_librarian_replaces_experience_index_2026_10_04](../../architecture/decisions/domain_librarian_replaces_experience_index_2026_10_04.md)), shortened tool descriptions and instructions ([domain_file_backend_replaces_chroma_2026_10_04](../../architecture/decisions/domain_file_backend_replaces_chroma_2026_10_04.md)), and the client loading MCP schemas on demand.
Evidence: /context output of 2026-10-04 (ai-mem tool table), hook output measured with python3 -m ai_mem.hook. Not measured: the original ~5% figure's window size and composition.

## Edges

- confirms: [domain_librarian_replaces_experience_index_2026_10_04](../../architecture/decisions/domain_librarian_replaces_experience_index_2026_10_04.md)
