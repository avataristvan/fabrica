type: domain
topic: architecture
created: 1791634292.098856
---

Decision: Every file under docs/ and docs/reference/ is classified as one of three things:
(1) Current documentation of the new model, rewritten and kept current. Structured after Diátaxis: tutorial, how-to, reference, explanation.
(2) A source: dated evidence of how ai-mem got here, such as measurements, design sketches, plans, comparisons, retired systems and the origin story. Sources move to docs/sources/<slug>.md (raw material in docs/sources/<slug>/) with frontmatter (type, date, origin, status). Their claims are frozen. Conclusions that still hold become learnings and decisions that point to the source (Evidence: / derived_from).
(3) A duplicate, merged into its current counterpart, e.g. docs/developer-guide.md vs docs/reference/developer_guide.md (merged, the result now docs/how-to/develop.md; the former reference id developer_guide no longer exists, edges to merged reference ids dangle).
Sources are part of the model, not an archive. The librarian may follow Evidence links when asked for proof. The archivist creates sources and derives learnings from them, but never edits a source's claims. The doctor lists sources that no learning points to. The format follows a pattern from an interview-notes project: 'what the source says' kept apart from 'our notes'. Internal sources such as measurements, session findings and our own past design docs count as much as external ones such as talks and papers. Every chunk updates the docs it touches. A dedicated chunk does the classification and rewrites the README concept-first.
Why: Much of today's documentation describes retired systems: hybrid search, reranking / confidence lifecycle, collections, the automation pipeline, ChromaDB. Yet it is the evidence behind current decisions. Deleting it loses the why. Keeping it as documentation misleads readers about the current system. As sources it keeps both: frozen evidence plus current docs. This extends [domain_three_kinds_of_knowledge_age_differently_2026_10_10](domain_three_kinds_of_knowledge_age_differently_2026_10_10.md) (evidence never changes) to ai-mem's own history. Diátaxis comes from the ai-architecture handoff (conclusion 1).
Scope: docs/, docs/reference/, README.md, CLAUDE.md, docs/reference/record-format.md (source format), the archivist and doctor. A docs-and-sources chunk in the plugin plan, plus a 'docs touched are updated' exit in every chunk. The user stressed on 2026-10-10 that documentation and README must be adapted and extended.

## Edges

- related: [domain_doctor_retired_system_check_is_keyword_heuristic_2026_10_12](domain_doctor_retired_system_check_is_keyword_heuristic_2026_10_12.md)
- related: [domain_source_status_unprocessed_or_processed_2026_10_12](domain_source_status_unprocessed_or_processed_2026_10_12.md)
- related: [domain_current_docs_hold_history_in_one_upgrade_section_2026_10_12](domain_current_docs_hold_history_in_one_upgrade_section_2026_10_12.md)
- related: [domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12](domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12.md)
- derived_from: [domain_three_kinds_of_knowledge_age_differently_2026_10_10](domain_three_kinds_of_knowledge_age_differently_2026_10_10.md)
