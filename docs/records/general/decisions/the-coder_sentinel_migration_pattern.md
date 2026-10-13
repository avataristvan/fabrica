id: the-coder_sentinel_migration_pattern
type: pattern
area: general
perspective: the-coder
created: 1781383489.787632
---

Rule: Use a sentinel file to gate one-time migrations in tools without a formal DB migration framework.
When: A breaking schema/data change needs to run exactly once per installation (e.g. backfilling a new metadata field).
Why: Idempotent scripts alone don't prevent redundant runs on every install. A sentinel file (~/.app/.migrations/migration_name.done) records completion per-installation, costs nothing, and survives reinstalls cleanly. The migration script itself stays idempotent as a second safety net.