id: domain_no_hardcoded_keyword_pretool_hook_recall_moment_open_2026_10_23
type: domain
area: architecture
perspective: user
created: 1792789846.164136
edges: [{"target_id": "learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23", "edge_type": "derived_from"}, {"target_id": "arch_decision_pretool_push_removed_2026_09_12", "edge_type": "related"}]
cue: Someone proposes a hook that greps records for a list of risky tool names to solve the recall moment.
---

Decision: Rejected (user, 2026-10-23): a PreToolUse hook on Bash that greps records for a hardcoded list of risky tool names (memtool, i2cx, dd, devsh.py, mmcblk ...) and shows the hits. The recall-moment problem (learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23) stays open; no solution is chosen.
Why: The list is hardcoded and the direction is wrong. It also returns to the push before tool calls that arch_decision_pretool_push_removed_2026_09_12 removed, there for context footprint; the reasons differ, the direction does not.
Scope: Proposals for deterministic recall at the moment of a risky action. Does not cover other trigger points (todo_pull_trigger_points_per_situation).
