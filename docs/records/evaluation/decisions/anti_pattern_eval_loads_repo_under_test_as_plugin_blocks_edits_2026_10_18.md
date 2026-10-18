id: anti_pattern_eval_loads_repo_under_test_as_plugin_blocks_edits_2026_10_18
type: anti-pattern
area: evaluation
perspective: agent
created: 1792360317.380537
edges: [{"target_id": "eval_seniority_main_run_result_2026_10_18", "edge_type": "related"}]
cue: I am building an eval arm that loads the repo under test as a plugin and expects the agent to edit files.
---

Tried: Running the arm with --plugin-dir pointing at the arm (the repo under test) itself.
Failed because: Claude Code blocks edits to the loaded plugin, so the arm stalls on edit tasks (C1 A3 scored 000; 4 of the 20 spot-check items were A3 permission stalls). A3 results are confounded and not interpretable for edit tasks; they were reported only and are not part of the rule.
Instead: Do not load the edited tree as a plugin in the same run; give the arm the plugin from a separate copy, or exclude edit tasks for that arm. Evidence: scripts/eval_seniority/run.py (build_arm, claude); eval_seniority_main_run_result_2026_10_18.
