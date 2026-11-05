type: learning
topic: evaluation
perspective: user
created: 1792360315.821311
cue: I am designing how records reach agents, or judging why a record did not work although the agent read it.
---

Observed: Where the record was read, the agent often built the rejected thing anyway and flagged the conflict afterwards. D3 in A2 scored 1/1/1: the agent read the reason every time and still built `mem prune` with a dry-run default.
Cause: The obstacle is learned solution-space behaviour and self-confidence (an LLM would need to withstand an order), not missing knowledge. Delivering the reason is not enough to make the agent object.
Evidence: [eval_seniority_main_run_result_2026_10_18](eval_seniority_main_run_result_2026_10_18.md) (D3/D4 scores); spot-check items S3, S8, S20 of the seniority run (local, scripts/eval_seniority/results/main-2026-10-16/).

## Edges

- derived_from: [eval_seniority_main_run_result_2026_10_18](eval_seniority_main_run_result_2026_10_18.md)
- related: [domain_dev_team_stops_on_contradiction_blocked_2026_10_19](../../../../../../docs/records/architecture/decisions/domain_dev_team_stops_on_contradiction_blocked_2026_10_19.md)
- related: [learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23](learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23.md)
