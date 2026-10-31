id: domain_acceptance_checksum_skips_hook_written_paths_2026_10_13
type: domain
area: plugin
perspective: agent
created: 1791869829.001687
edges: [{"target_id": "domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31", "edge_type": "related"}]
cue: The upgrade acceptance run reports a real-data checksum mismatch and I must tell a leak from hook noise
---

Decision: scripts/upgrade_acceptance/run.sh skips reminded/, retro_log.jsonl, doctor_last_run and session_start.txt in the real store when it checksums. adr_collection_roots.json stays checked.
Why: Running sessions' hooks write the skipped paths, so the run was never green although every functional check passed. Only the migration writes adr_collection_roots.json, so a change there is a real leak.
Scope: the acceptance run's real-data checksum. Closes todo_acceptance_checksum_exclude_hook_written_paths_2026_10_12.
Evidence: scripts/upgrade_acceptance/run.sh.

Historical since 3c64e27 (2026-10-31): the acceptance run is removed from main; it lives at tag v1-last-upgrade-path.
