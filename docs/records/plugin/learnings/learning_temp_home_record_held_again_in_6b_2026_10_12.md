type: learning
topic: plugin
perspective: agent
created: 1791833920.162076
cue: I am about to plan a claude -p exit test and wonder whether an isolated HOME is possible
---

Observed: [learning_temp_home_cannot_run_claude_p_2026_10_12](learning_temp_home_cannot_run_claude_p_2026_10_12.md) held again in the setup-skill chunk: it redirected the exit runs to the real HOME with --setting-sources before any attempt at a temp HOME.
Cause: The record was recalled at chunk start, so the dead end was not re-walked.
Evidence: orchestrator note of that chunk's merge.

## Edges

- confirms: [learning_temp_home_cannot_run_claude_p_2026_10_12](learning_temp_home_cannot_run_claude_p_2026_10_12.md)
