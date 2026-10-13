id: pattern_planner_run_exit_criterion_greps_on_current_tree_2026_10_12
type: pattern
area: workflow
perspective: reviewer
created: 1791788133.506723
edges: [{"target_id": "learning_plan_exit_criterion_conflicted_with_do_not_touch_list_2026_10_12", "edge_type": "confirms"}]
cue: I am writing exit criteria (greps) for a chunk plan, or a chunk that adds an agent to a symlink-deployed set
---

Rule: Run every exit-criterion grep against the current tree before writing it. A grep that is non-empty before the chunk starts is a hidden scope item or a wrong criterion. A chunk that adds an agent to a symlink-deployed set lists install.py and uninstall.py (both link one by one, no glob) and the later packaging chunk's move of that file.
When: Planning a chunk (planner), writing exit criteria.
Why: In a plan review the tech-lead found ai_mem/hooks/retro_check.py DEFAULT_ROLES already matching the criterion. Evidence: that tech-lead review (2026-10-12); second case after learning_plan_exit_criterion_conflicted_with_do_not_touch_list_2026_10_12.
