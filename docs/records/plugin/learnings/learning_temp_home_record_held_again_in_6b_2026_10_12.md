id: learning_temp_home_record_held_again_in_6b_2026_10_12
type: learning
area: plugin
perspective: agent
created: 1791833920.162076
edges: [{"target_id": "learning_temp_home_cannot_run_claude_p_2026_10_12", "edge_type": "confirms"}]
cue: I am about to plan a claude -p exit test and wonder whether an isolated HOME is possible
---

Observed: learning_temp_home_cannot_run_claude_p_2026_10_12 held again in the setup-skill chunk: it redirected the exit runs to the real HOME with --setting-sources before any attempt at a temp HOME.
Cause: The record was recalled at chunk start, so the dead end was not re-walked.
Evidence: orchestrator note of that chunk's merge.
