id: learning_context_boundary_is_read_and_write_point_2026_10_10
type: learning
area: architecture
perspective: user
created: 1791629940.055744
edges: [{"target_id": "domain_librarian_at_review_handoff_2026_10_10", "edge_type": "confirms"}, {"target_id": "pattern_retrieval_needs_fixed_trigger_in_role_prompt", "edge_type": "related"}]
---

Observed: Chelsea Troy's practices (DDD Europe 2026, distilled in the records of the interview-notes project) put a handoff at every context boundary, and what stays of it becomes a record. Each new conversation starts with a charter (scope, terminology, mode). In ai-mem the pull gap test showed that agents read memory only at a fixed trigger, and the review handoff in dev-team.md is such a trigger. Together: a context boundary is both the point to read (the charter or briefing coming in is the question for the librarian) and the point to write (the handoff going out feeds the archivist).
Cause: At a boundary the situation is stated explicitly (charter, diff, chunk spec). Mid-conversation it is implicit, and nothing prompts a read or a write.
Evidence: pattern_conversation_charter_2026_10_10 and pattern_carry_only_conclusions_handoff_2026_10_10 (interview-notes project), eval_pull_gap_test_2026_09_20, domain_librarian_at_review_handoff_2026_10_10. Extends the reading half of the older pattern_retrieval_needs_fixed_trigger_in_role_prompt (2026-10-04) with a writing half. That record was missed when this one was written on 2026-10-10.

pseudonymised for publication, 2026-10-11
