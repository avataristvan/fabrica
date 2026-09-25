id: pattern_status_markers_rot_in_memory
type: pattern
created: 1785517815.038957
---

Rule: Never embed mutable status strings ("NOT YET COMMITTED", "not started", "noch offen") directly in memory entry text. Reference the commit SHA or ticket ID instead once it exists, and update the entry the moment it does.
When: Writing any memory entry about work-in-progress, especially right before or right after committing.
Why: Three entries written 2026-07-31 (chunk1_daemon_shipped, chunk3_access_count_semantics_shipped, pull_through_measurement_impl) all had stale "NOT YET COMMITTED" markers within the same session, confirmed wrong by git log at the very next mem-dream run. A commit SHA is permanent and self-verifying; a status word rots the instant the state changes and there is no trigger that updates it automatically.