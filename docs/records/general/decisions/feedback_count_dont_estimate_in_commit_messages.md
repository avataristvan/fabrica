id: feedback_count_dont_estimate_in_commit_messages
type: pattern
area: general
created: 1790678891.368484
edges: [{"target_id": "../fabrica:pattern_status_markers_rot_in_memory", "edge_type": "related"}]
---

Count numbers in commit messages and completion reports (files, entries, tests) before writing them; do not assemble them from memory. On 2026-09-29 the migration commit message (093dc1b; the original hash ffb7bc9 was discarded by amend) first said '39 decisions, 16 learnings', actually 35/20 (find | uniq -c); corrected by amend.

Why: Numbers assembled from memory deviate unnoticed (here 39/16 instead of 35/20), and a commit message or a report afterwards reads like a substantiated statement.
How to apply: Count immediately before writing the number -- `find ... | uniq -c` or `git log` -- and take the value from that output, not from an earlier count in the conversation.
