id: todo_check_no_private_records_before_push_2026_10_12
type: todo
area: workflow
perspective: user
created: 1791838325.126213
edges: [{"target_id": "domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13", "edge_type": "related"}]
cue: I am about to push ai-mem main or the tag v0-last-mcp to a public remote
---

TODO: Before any push (main and tag v0-last-mcp), check that no internal or private record is in ai-mem; then push.
State 2026-10-13: the pseudonymisation pass over docs/records is done (domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13): machine paths, private project names, pointers to local-only files and unpushed SHAs are gone from the records. Left for the user before pushing: run the final name grep over docs/records and docs/sources, check that .git/info/exclude still lists the local-only material, and confirm the squash of the unpushed commits.
