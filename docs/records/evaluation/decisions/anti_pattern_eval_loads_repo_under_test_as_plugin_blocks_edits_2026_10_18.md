type: anti-pattern
topic: evaluation
perspective: agent
created: 1792360317.380537
cue: I am building an eval arm that loads the repo under test as a plugin and expects the agent to edit files.
---

Tried: Running the arm with --plugin-dir pointing at the arm (the repo under test) itself.
Failed because: Claude Code blocks edits to the loaded plugin, so the arm stalls on edit tasks (C1 A3 scored 000; 4 of the 20 spot-check items were A3 permission stalls). A3 results are confounded and not interpretable for edit tasks; they were reported only and are not part of the rule.
Instead: Do not load the edited tree as a plugin in the same run; give the arm the plugin from a separate copy, or exclude edit tasks for that arm. Evidence: scripts/eval_seniority/run.py (build_arm, claude); [eval_seniority_main_run_result_2026_10_18](../learnings/eval_seniority_main_run_result_2026_10_18.md).

## Edges

- related: [eval_seniority_main_run_result_2026_10_18](../learnings/eval_seniority_main_run_result_2026_10_18.md)
- related: [learning_plugin_keeps_loading_from_clean_clone_when_marketplace_repointed_2026_10_31](../../plugin/learnings/learning_plugin_keeps_loading_from_clean_clone_when_marketplace_repointed_2026_10_31.md)
