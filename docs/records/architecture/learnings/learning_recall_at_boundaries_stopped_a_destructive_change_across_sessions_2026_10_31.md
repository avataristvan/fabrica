type: learning
topic: architecture
perspective: user
created: 1793470099.609578
cue: Someone asks whether recall at boundaries works across sessions and agents, or a briefing carries a premise I cannot check.
---

Observed: A briefing written in another session carried a wrong premise ("exactly one user"). The recorded reason (an external installation that auto-updates from main and may not have migrated) surfaced twice before any destructive change was kept: once from the librarian at the start of this session, once from the coder's own librarian call at its chunk start, which made the coder stop and revert. Both catches came from the same records, the same librarian and the same CLAUDE.md rule that calls it: one mechanism working twice, not two independent results. The coder had already started editing before its librarian answer arrived; a separate worktree, not the record, kept that harmless. The wrong premise itself came from a handoff/briefing, a Fabrica practice. The user takes this as evidence that Fabrica and ai-mem hold in a distributed agent system: the records acted not only as knowledge but as a kind of experience. One observed case, not a measurement.
Cause: The reason sat in a record ([domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12](../decisions/domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12.md), todo_verify_external_installation_migration_and_plugin_switch_2026_10_15) and was pulled at a boundary by two agents; the premise lived only in the briefing. The reading "it worked as experience" is the user's.
Evidence: This session (2026-10-31); the two records named above; [learning_librarian_answer_must_be_in_before_first_edit_at_chunk_start_2026_10_31](../../workflow/learnings/learning_librarian_answer_must_be_in_before_first_edit_at_chunk_start_2026_10_31.md). It is field evidence for the hypothesis in docs/fabrica/patterns/seniority-lives-in-the-record.md, not a measured result.

## Edges

- related: [domain_librarian_at_review_handoff_2026_10_10](../../retrieval/decisions/domain_librarian_at_review_handoff_2026_10_10.md)
- related: [domain_fabrica_seniority_from_the_record_2026_10_14](../decisions/domain_fabrica_seniority_from_the_record_2026_10_14.md)
- confirms: [domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12](../decisions/domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12.md)
