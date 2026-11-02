id: eval_seniority_available_not_used_confirms_pull_gap_2026_10_18
type: learning
topic: evaluation
perspective: agent
created: 1792360316.043297
edges: [{"target_id": "eval_seniority_main_run_result_2026_10_18", "edge_type": "derived_from"}, {"target_id": "eval_pull_gap_test_2026_09_20", "edge_type": "confirms"}, {"target_id": "learning_whole_record_not_better_than_decisions_alone_2026_10_24", "edge_type": "related"}]
cue: I assume that having all records in the repo means the agent will read them.
---

Observed: With all records in the repo (arm A2), the agent read docs/records/ in only 11 of 24 runs. Available is not used.
Cause: Same as the pull gap of 2026-09-20: no trigger makes the agent look when code or docs offer a plausible substitute answer.
Evidence: eval_seniority_main_run_result_2026_10_18 (tool trace); eval_pull_gap_test_2026_09_20.
