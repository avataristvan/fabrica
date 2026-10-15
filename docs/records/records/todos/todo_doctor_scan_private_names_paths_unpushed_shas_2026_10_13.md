id: todo_doctor_scan_private_names_paths_unpushed_shas_2026_10_13
type: todo
area: records
perspective: agent
created: 1791889506.339908
edges: [{"target_id": "learning_public_history_pushed_clean_2026_10_13", "edge_type": "related"}, {"target_id": "domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13", "edge_type": "related"}, {"target_id": "learning_push_check_2026_10_15_was_clean", "edge_type": "related"}]
cue: I am about to push an area to a public remote and need to scan its records and sources for private material
---

TODO: A `mem doctor` (or `mem lint`) check that lists hits in docs/records and docs/sources for configurable private names, machine paths (/home/<user>) and commit SHAs the remote does not have, so the pre-push scan is one command instead of a hand-written grep. Dangling cross-area edges are already found by lint and doctor and are not part of this.
Origin: the archivist's own retro and the agent, after the push of 2026-10-13 (learning_public_history_pushed_clean_2026_10_13).
