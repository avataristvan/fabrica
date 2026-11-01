id: learning_migrate_apply_exit1_has_two_meanings_2026_10_11
type: learning
topic: workflow
perspective: the-coder
created: 1791738301.237421
edges: [{"target_id": "pattern_persistence_migration_bypasses_mcp", "edge_type": "related"}, {"target_id": "domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31", "edge_type": "related"}]
cue: I am reading or wrapping the exit code of mem-adr-sync migrate --apply
---

Observed: migrate --apply exits 1 in two different cases: files were written but the plan was not clean, or the store was unreadable and nothing was written. Only the "Report:" line in stdout tells them apart.
Cause: One exit code for two outcomes; the distinction lives in the output.
Evidence: install.py run_records_migration branches its message on "Report:".

Historical since 3c64e27 (2026-10-31): `migrate` and install.py are removed from main; the code is at tag v1-last-upgrade-path.
