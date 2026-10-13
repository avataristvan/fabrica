id: todo_dream_area_refs_refactor
type: todo
area: workflow
created: 1791668870.47886
edges: [{"target_id": "learning_dev_team_plugin_step2_done_2026_10_10", "edge_type": "related"}]
cue: I am changing how mem-dream validates ADD targets in dream_memory.py or the AreaRefs protocol
---

TODO (from the mem-dream area-mode review): replace AreaRefResolver.resolve(..., '<path>:probe') (_area_add_targets in application/dream_memory.py, _PROBE_ID) with a resolve_area method on the AreaRefs protocol. The second point of the review (a per-run scope object instead of branching on area_refs is not None) is gone: area_refs is required now.
