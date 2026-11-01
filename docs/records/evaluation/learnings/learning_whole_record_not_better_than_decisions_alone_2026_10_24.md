id: learning_whole_record_not_better_than_decisions_alone_2026_10_24
type: learning
topic: evaluation
perspective: agent
created: 1792876751.636788
edges: [{"target_id": "eval_seniority_main_run_result_2026_10_18", "edge_type": "derived_from"}, {"target_id": "domain_fabrica_seniority_from_the_record_2026_10_14", "edge_type": "related"}, {"target_id": "eval_seniority_available_not_used_confirms_pull_gap_2026_10_18", "edge_type": "related"}]
cue: Someone claims that learnings or the whole record carry more than decisions alone, as ADR practice assumes.
---

Observed: In the seniority measurement the whole record (A2) was not better than decisions alone (A1). Dead ends avoided (score 2) on D1-D6 per repeat: A1 (decisions only) 3/3/3, A2 (whole record) 2/2/4; A0 1/1/3; A3 4/4/5 (confounded, reported only).
Cause: Not established. Consistent with eval_seniority_available_not_used_confirms_pull_gap_2026_10_18 (records are read in only 11 of 24 runs), but the measurement does not separate the two.
Evidence: score strings in eval_seniority_main_run_result_2026_10_18 (computed from them; no earlier record stated this comparison); docs/explanation/what-we-measured.md (commit b954cc4).
