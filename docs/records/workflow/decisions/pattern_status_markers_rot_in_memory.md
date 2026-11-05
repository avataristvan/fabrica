type: pattern
topic: workflow
perspective: agent
created: 1785517815.038957
cue: I am writing a record or FOCUS line with a status (uncommitted, running, open) or a commit SHA, or trusting one after an abort or amend
---

Rule: Never embed mutable status strings ("NOT YET COMMITTED", "not started", "still open") directly in memory entry text. Reference the commit SHA or ticket ID instead once it exists, and update the entry the moment it does.
When: Writing any memory entry about work-in-progress, especially right before or right after committing.
Why: Three entries written 2026-07-31 (chunk1_daemon_shipped, chunk3_access_count_semantics_shipped, pull_through_measurement_impl) all had stale "NOT YET COMMITTED" markers within the same session, confirmed wrong by git log at the very next mem-dream run. A commit SHA is permanent and self-verifying; a status word rots the instant the state changes and there is no trigger that updates it automatically.

Caveat: A commit SHA is only stable after the last amend/rebase. Therefore cite SHAs only after the final amend, or check them when writing with `git cat-file -e <sha>`. Case 2026-09-29: entries cited a commit's hash from before an amend, and that hash then pointed nowhere (the commit is f4e5122 on main today) -- the cited hash pointed to a discarded state.

Case 2026-10-04: The full history rewrite of ai-mem (records removed, force push) invalidates every SHA cited in the records -- the second SHA invalidation after the amend of 2026-09-29; see todo_remap_commit_shas_in_records.

## Edges

- related: [learning_history_rewrite_orphans_commit_hashes_cited_in_records_2026_11_05](../../records/learnings/learning_history_rewrite_orphans_commit_hashes_cited_in_records_2026_11_05.md)
