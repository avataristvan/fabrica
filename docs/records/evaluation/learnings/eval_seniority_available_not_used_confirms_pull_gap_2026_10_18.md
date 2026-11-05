type: learning
topic: evaluation
perspective: agent
created: 1792360316.043297
cue: I assume that having all records in the repo means the agent will read them.
---

Observed: With all records in the repo (arm A2), the agent read docs/records/ in only 11 of 24 runs. Available is not used.
Cause: Same as the pull gap of 2026-09-20: no trigger makes the agent look when code or docs offer a plausible substitute answer.
Evidence: [eval_seniority_main_run_result_2026_10_18](eval_seniority_main_run_result_2026_10_18.md) (tool trace); [eval_pull_gap_test_2026_09_20](eval_pull_gap_test_2026_09_20.md).

## Edges

- derived_from: [eval_seniority_main_run_result_2026_10_18](eval_seniority_main_run_result_2026_10_18.md)
- confirms: [eval_pull_gap_test_2026_09_20](eval_pull_gap_test_2026_09_20.md)
- related: [learning_whole_record_not_better_than_decisions_alone_2026_10_24](learning_whole_record_not_better_than_decisions_alone_2026_10_24.md)
