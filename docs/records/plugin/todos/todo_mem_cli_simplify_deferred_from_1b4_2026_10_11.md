id: todo_mem_cli_simplify_deferred_from_1b4_2026_10_11
type: todo
area: plugin
perspective: agent
created: 1791745728.520275
edges: [{"target_id": "pattern_lookup_refs_use_consumer_validation_2026_10_11", "edge_type": "related"}]
cue: I am touching mem_cli _link, mem find, the area qualify code or reference-doc lookup
---

TODO (deferred from a /simplify review of the mem CLI): (1) a TargetNotFound exception instead of matching error text in mem_cli._link; (2) qualify should validate its own output; (3) the reference-doc lookup exists three times (file_repository._reference_file, records_lint._stems, mem_cli._locate), make it one; (4) mem find rglobs every area, bound or index it.
