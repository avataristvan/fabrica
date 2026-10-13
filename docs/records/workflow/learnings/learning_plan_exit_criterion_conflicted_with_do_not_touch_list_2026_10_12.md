id: learning_plan_exit_criterion_conflicted_with_do_not_touch_list_2026_10_12
type: learning
area: workflow
perspective: agent
created: 1791786665.411311
edges: [{"target_id": "todo_fix_broken_memPalace_link_in_epistemology_framework_2026_10_12", "edge_type": "related"}, {"target_id": "pattern_planner_run_exit_criterion_greps_on_current_tree_2026_10_12", "edge_type": "related"}]
cue: Writing a chunk plan whose exit criterion depends on files the same chunk must not touch
---

Observed: The plan of a docs-rewrite chunk demanded zero doctor hits while forbidding edits to two of the flagged files (docs/epistemology-framework.md and an untracked plan doc). The conflict surfaced only at chunk start. User decision: the orchestrator adds a banner to the untracked plan doc (untracked files never reach a worktree), and epistemology-framework.md stays as the one known remaining hit.
Cause: The exit criterion and the do-not-touch list were written separately and never checked against each other.
Evidence: When planning, check each chunk's exit criteria against its do-not-touch list (pattern_planner_run_exit_criterion_greps_on_current_tree_2026_10_12).
