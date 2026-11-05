type: learning
topic: workflow
perspective: the-coder
created: 1791738301.237421
cue: I am reading or wrapping the exit code of mem-adr-sync migrate --apply
---

Observed: migrate --apply exits 1 in two different cases: files were written but the plan was not clean, or the store was unreadable and nothing was written. Only the "Report:" line in stdout tells them apart.
Cause: One exit code for two outcomes; the distinction lives in the output.
Evidence: install.py run_records_migration branches its message on "Report:".

Historical since 3c64e27 (2026-10-31): `migrate` and install.py are removed from main; the code is at tag v1-last-upgrade-path.

## Edges

- related: [pattern_persistence_migration_bypasses_mcp](../decisions/pattern_persistence_migration_bypasses_mcp.md)
- related: [domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31](../../architecture/decisions/domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31.md)
