id: pattern_planner_run_exit_criterion_greps_on_current_tree_2026_10_12
type: pattern
topic: workflow
perspective: reviewer
created: 1791788133.506723
cue: I am planning a chunk that adds an agent to a symlink-deployed set
---

Rule: A chunk that adds an agent to a symlink-deployed set lists install.py and uninstall.py (both link one by one, no glob) and the later packaging chunk's move of that file.
When: Planning a chunk that adds an agent.
Why: In a plan review ai_mem/hooks/retro_check.py DEFAULT_ROLES already matched an exit-criterion grep (2026-10-12). The generic rule about running exit-criterion greps on the current tree lives outside ai-mem.
