type: learning
topic: architecture
created: 1783085186.096779
valid_until: 1790440080.734041
---

Observed: Entries with a low access_count were not found despite targeted queries, because session-hot entries (access_count 10-12) dominated (mem_dream curation 2026-05-18).
Cause: The confidence ranker always promotes the same 5-10 incumbents regardless of semantic relevance.
Evidence: Examples in the text ([feedback_hook_firefighting_ux](../../../../../../docs/records/general/decisions/feedback_hook_firefighting_ux.md) among others); design questions retained as text.

In sessions that repeatedly query the same collection, entries with low access_count become invisible — the confidence ranker always promotes the same 5-10 high-access incumbents regardless of semantic relevance.

Observed 2026-05-18 during mem_dream curation: [feedback_hook_firefighting_ux](../../../../../../docs/records/general/decisions/feedback_hook_firefighting_ux.md), [feedback_agent_perspective_as_tool](../../../../../docs/records/general/decisions/feedback_agent_perspective_as_tool.md), [wr-sections-cut](../../../../../../ExoDeck-project/business/content-strategy/docs/records/general/decisions/wr-sections-cut.md), wr-<name>-narrative-arc could not be retrieved despite targeted queries, because session-hot entries (access_count 10-12) dominated.

Questions to investigate:
- Should confidence weighting be capped (e.g. log-scaled beyond a threshold)?
- Should access_count decay within a session (to avoid repeated queries inflating the same entries)?
- Is there a way to retrieve by ID directly, bypassing the ranker?

Goal: low-access entries must remain retrievable on semantically specific queries, even in heavy-query sessions.

## Edges

- superseded_by: [domain_drop_confidence_for_evidence_and_librarian_2026_09_26](../decisions/domain_drop_confidence_for_evidence_and_librarian_2026_09_26.md)
