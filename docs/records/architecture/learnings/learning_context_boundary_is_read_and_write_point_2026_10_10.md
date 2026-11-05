type: learning
topic: architecture
perspective: user
created: 1791629940.055744
---

Observed: Chelsea Troy's practices (DDD Europe 2026, distilled in the records of the interview-notes project) put a handoff at every context boundary, and what stays of it becomes a record. Each new conversation starts with a charter (scope, terminology, mode). In ai-mem the pull gap test showed that agents read memory only at a fixed trigger, and the review handoff in dev-team.md is such a trigger. Together: a context boundary is both the point to read (the charter or briefing coming in is the question for the librarian) and the point to write (the handoff going out feeds the archivist).
Cause: At a boundary the situation is stated explicitly (charter, diff, chunk spec). Mid-conversation it is implicit, and nothing prompts a read or a write.
Evidence: [pattern_conversation_charter_2026_10_10](../../../../../briefing-interviewer/docs/records/practices/decisions/pattern_conversation_charter_2026_10_10.md) and [pattern_carry_only_conclusions_handoff_2026_10_10](../../../../../briefing-interviewer/docs/records/practices/decisions/pattern_carry_only_conclusions_handoff_2026_10_10.md) (interview-notes project), [eval_pull_gap_test_2026_09_20](../../evaluation/learnings/eval_pull_gap_test_2026_09_20.md), [domain_librarian_at_review_handoff_2026_10_10](../../retrieval/decisions/domain_librarian_at_review_handoff_2026_10_10.md). Extends the reading half of the older [pattern_retrieval_needs_fixed_trigger_in_role_prompt](../../general/decisions/pattern_retrieval_needs_fixed_trigger_in_role_prompt.md) (2026-10-04) with a writing half. That record was missed when this one was written on 2026-10-10.

pseudonymised for publication, 2026-10-11

## Edges

- confirms: [domain_librarian_at_review_handoff_2026_10_10](../../retrieval/decisions/domain_librarian_at_review_handoff_2026_10_10.md)
- related: [pattern_retrieval_needs_fixed_trigger_in_role_prompt](../../general/decisions/pattern_retrieval_needs_fixed_trigger_in_role_prompt.md)
