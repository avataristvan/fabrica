id: todo_dream_area_refs_refactor
type: todo
area: workflow
created: 1791668870.47886
edges: [{"target_id": "learning_dev_team_plugin_step2_done_2026_10_10", "edge_type": "related"}]
---

TODO (from the mem-dream area-mode review): replace AreaRefResolver.resolve(..., '<path>:probe') with a resolve_area method on the AreaRefs protocol, and give DreamMemoryUseCase a per-run scope object instead of branching on area_refs is not None in several places.
