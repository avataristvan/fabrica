type: domain
topic: architecture
perspective: user
created: 1793656212.927951
cue: I notice a current doc naming ChromaDB, MCP server, BM25 or daemon, or want to extend the doctor's retired-system check.
---

Decision: The doctor's retired-system check (RETIRED_KEYWORDS in ai_mem/doctor_sources.py) was a migration aid and is retired; the removal follows in the next chunk of the session of 2026-11-02. It is not extended with synonyms: the "softer wording" gap is not closed.
Why: The migration is tagged (v0-last-mcp, v1-last-upgrade-path), so the old systems stay reachable in git and a keyword heuristic that can be sidestepped by other wording earns no more work.
Scope: ai_mem/doctor_sources.py, Sources section of `mem doctor`. Evidence: git tags v0-last-mcp, v1-last-upgrade-path.

## Edges

- supersedes: [domain_doctor_retired_system_check_is_keyword_heuristic_2026_10_12](domain_doctor_retired_system_check_is_keyword_heuristic_2026_10_12.md)
- related: [learning_banner_label_and_paraphrase_pass_retired_check_2026_10_12](../learnings/learning_banner_label_and_paraphrase_pass_retired_check_2026_10_12.md)
