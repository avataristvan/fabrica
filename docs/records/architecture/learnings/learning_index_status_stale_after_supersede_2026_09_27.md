type: learning
topic: architecture
perspective: agent
created: 1790678553.613667
cue: INDEX.md shows a superseded record as active after a supersede link
---

Observed: A parallel session in another project (migrating its collections to ADR format) reported that INDEX.md stayed stale after `mem_link(..., supersedes)`: the file itself correctly received `superseded_by`, but INDEX.md's status column stayed 'active' until someone manually ran `mem-adr-sync export`/`reindex`. That is more than cosmetic: the librarian ([domain_drop_confidence_for_evidence_and_librarian_2026_09_26](../decisions/domain_drop_confidence_for_evidence_and_librarian_2026_09_26.md)) judges based on INDEX.md, a stale status could make it treat a superseded entry as active.
Cause: The INDEX chunk (docs/sources/adr-migration-chunk-plan.md, formerly docs/adr-migration-chunk-plan.md) deliberately kept regenerate_index() away from the per-mem_add path in order to avoid a read-modify-write race on the one shared file -- correct for the general case, but left no trigger at all for the one case that changes the status of a row (no cron, no mem_dream hook, nothing).
Evidence: Report from that session; tests test_markdown_adr_repository.py::test_supersede_upsert_regenerates_index and test_boost_only_upsert_does_not_regenerate_index; docs/sources/adr-migration-chunk-plan.md (the Tech-Lead findings: diff before write so field order cannot cause churn; temp dirs for smoke tests).
