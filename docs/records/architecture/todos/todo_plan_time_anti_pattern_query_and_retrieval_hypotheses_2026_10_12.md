id: todo_plan_time_anti_pattern_query_and_retrieval_hypotheses_2026_10_12
type: todo
area: architecture
perspective: agent
created: 1791758034.413463
edges: [{"target_id": "todo_pull_trigger_points_per_situation", "edge_type": "related"}]
cue: Designing when anti-patterns surface, or how deep edge traversal and recall versus precision should go
---

TODO: Test three still-open ideas from the 2026-05-12 friction collection, one at a time, against the librarian model (the ranker, SessionStart signals and mem_query it assumed are gone):
1. Query anti-patterns at plan time, before the first file edit, not at edit time. The decision happens in conversation, so a warning after the edit comes too late. The plan-time trigger point is covered by todo_pull_trigger_points_per_situation; this record adds the reason.
2. Hypothesis: anti-patterns need high recall (surface borderline matches, a needless warning is cheap), patterns need high precision. The old system treated both alike; the librarian does not distinguish them yet.
3. Edge traversal depth: the 1-hop budget was chosen pragmatically; whether 2 hops add context or noise is untested. The librarian currently follows one hop.
Cold start is acceptable only where no prior experience existed; the problem is an agent that could have had experience but starts cold.
Evidence: docs/sources/friction-and-research.md (the "done" ranker items in it describe removed code and do not hold).
