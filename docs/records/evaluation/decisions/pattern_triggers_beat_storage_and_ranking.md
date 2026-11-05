type: pattern
topic: evaluation
perspective: agent
created: 1790409909.376447
cue: Before investing in retrieval ranking or similarity, I should check what actually triggers retrieval
---

Rule: What gets an agent to access memory is an ID pointer or a situation cue in the context — not better storage or better ranking (cosine, hybrid, confidence weighting).
When: Before time is invested in retrieval improvement (similarity formula, hybrid search, confidence-weighted ranking) instead of in trigger mechanisms (CLAUDE.md pointer, experience index/cue).
Why: [eval_pull_gap_test_2026_09_20](../learnings/eval_pull_gap_test_2026_09_20.md) found 0 mem_query calls in all 7 gap cases; the 3 solved cases ran exclusively via mem_get on an entry ID named in CLAUDE.md, not via similarity search (cosine hit@1 only 3/7 in the replay, and a score threshold does not separate correct from noise — correct hit at 0.20, nonsense query at 0.26). [eval_experience_index_ab_2026_09_21](../learnings/eval_experience_index_ab_2026_09_21.md) confirms the direction: with a SessionStart cue block, 3/3 previously unsolved cases (g2, g5, g6) went directly to the gold entry, versus 1/3 in the baseline without an index. [domain_direction_judgment_over_scores_2026_09_20](../../architecture/decisions/domain_direction_judgment_over_scores_2026_09_20.md) draws the architectural consequence: judgment (boost/cue/supersede) instead of a mechanical score as a protection or maturity signal, because the real bottleneck is the trigger, not the ranking of the candidates.
Limits of the evidence: n=1 per cell, one model, self-report of the tool calls instead of instrumentation, cues were written by the same agent that knew the test questions — this is a statement of direction, not a reliable rate.

Status 2026-10-04: The cue index recommended here was retired for its context cost. The surviving trigger forms are id/records pointers in context and fixed call points in role prompts (reviewer template, the /chunk-plan librarian call).

## Edges

- related: [eval_pull_gap_test_2026_09_20](../learnings/eval_pull_gap_test_2026_09_20.md)
- related: [eval_experience_index_ab_2026_09_21](../learnings/eval_experience_index_ab_2026_09_21.md)
- related: [domain_direction_judgment_over_scores_2026_09_20](../../architecture/decisions/domain_direction_judgment_over_scores_2026_09_20.md)
- derived_from: [eval_pull_gap_test_2026_09_20](../learnings/eval_pull_gap_test_2026_09_20.md)
- derived_from: [eval_experience_index_ab_2026_09_21](../learnings/eval_experience_index_ab_2026_09_21.md)
