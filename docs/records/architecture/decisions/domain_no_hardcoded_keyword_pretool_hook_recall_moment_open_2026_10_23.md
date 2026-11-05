type: domain
topic: architecture
perspective: user
created: 1792789846.164136
cue: Someone proposes a hook that greps records for a list of risky tool names to solve the recall moment.
---

Decision: Rejected (user, 2026-10-23): a PreToolUse hook on Bash that greps records for a hardcoded list of risky tool names (memtool, i2cx, dd, devsh.py, mmcblk ...) and shows the hits. The recall-moment problem ([learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23](../../evaluation/learnings/learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23.md)) stays open; no solution is chosen.
Why: The list is hardcoded and the direction is wrong. It also returns to the push before tool calls that [arch_decision_pretool_push_removed_2026_09_12](arch_decision_pretool_push_removed_2026_09_12.md) removed, there for context footprint; the reasons differ, the direction does not.
Scope: Proposals for deterministic recall at the moment of a risky action. Does not cover other trigger points (todo_pull_trigger_points_per_situation).

## Edges

- derived_from: [learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23](../../evaluation/learnings/learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23.md)
- related: [arch_decision_pretool_push_removed_2026_09_12](arch_decision_pretool_push_removed_2026_09_12.md)
