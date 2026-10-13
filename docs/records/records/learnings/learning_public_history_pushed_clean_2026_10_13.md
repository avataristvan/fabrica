id: learning_public_history_pushed_clean_2026_10_13
type: learning
area: records
perspective: user
created: 1791889505.242208
edges: [{"target_id": "domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13", "edge_type": "related"}, {"target_id": "domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12", "edge_type": "related"}]
cue: Someone asks whether the public ai-mem history was checked for private names and machine paths before the push
---

Observed: Going public is done. main (48fabdb) and the tag v0-last-mcp (60d85d8, the cleaned rollback point, parent of the cutover commit) were pushed on 2026-10-13, after a clean scan for private names and machine paths over docs/records and docs/sources.
Cause: The decision domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13 and its pre-push checklist were worked off; the checklist todo is closed by this record.
Evidence: commits 48fabdb and 60d85d8, both on origin/main.
