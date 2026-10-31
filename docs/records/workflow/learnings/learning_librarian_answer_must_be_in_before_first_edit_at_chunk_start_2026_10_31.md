id: learning_librarian_answer_must_be_in_before_first_edit_at_chunk_start_2026_10_31
type: learning
area: workflow
perspective: the-coder
created: 1793470087.817007
edges: [{"target_id": "learning_recall_at_boundaries_stopped_a_destructive_change_across_sessions_2026_10_31", "edge_type": "related"}, {"target_id": "domain_librarian_at_review_handoff_2026_10_10", "edge_type": "related"}, {"target_id": "learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23", "edge_type": "related"}]
cue: I am starting a chunk and my librarian call failed or is still running while I am about to begin editing.
---

Observed: At a chunk start the coder's first librarian call failed (a missing parameter). The retry ran in parallel with the work, the answer arrived after edits had been made, and the coder had to revert them.
Cause: The recall was treated as background work instead of a gate; the answer named the reason that made the edits wrong (see learning_recall_at_boundaries_stopped_a_destructive_change_across_sessions_2026_10_31).
Evidence: This session (2026-10-31), the coder's chunk start. The rule that follows: the librarian answer must be in before the first edit; a failed call is retried first, not worked around.
