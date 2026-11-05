type: domain
topic: workflow
perspective: user
created: 1791869828.778418
cue: I want mem-dream to write links, supersedes or deletes itself instead of only proposing them
---

Decision: mem-dream proposes, it never applies. The auto-apply path of DreamMemoryUseCase (auto_link, auto_supersede, auto_delete) is removed; the report sections (merge conflicts, split candidates, propagation) stay. The archivist judges each proposal and applies it with `mem`.
Why: After the MCP removal nothing calls the auto-apply path (no CLI flag in ai_mem/dream_cli.py, and /reflect does not call mem-dream). Applying model output would make Dream a third writer beside the archivist and the user, who are the only writers.
Scope: ai_mem/application/dream_memory.py and its tests. Overrides the "auto_link and auto_supersede on, auto_delete off" setting in [domain_dream_after_every_reflect_2026_09_26](domain_dream_after_every_reflect_2026_09_26.md); the rest of that decision (run after every reflect, limited to the active area, neighbourhood focus) is untouched. Moots todo_dream_dangling_cross_area_edge_warning (auto_delete is gone).
Evidence: ai_mem/dream_cli.py (no auto flags).

## Edges

- related: [domain_dream_after_every_reflect_2026_09_26](domain_dream_after_every_reflect_2026_09_26.md)
- related: [domain_archivist_mechanism_mem_and_mem_dream_2026_10_11](../../architecture/decisions/domain_archivist_mechanism_mem_and_mem_dream_2026_10_11.md)
- related: [domain_setup_seeds_nothing_first_records_come_from_work_2026_10_12](../../plugin/decisions/domain_setup_seeds_nothing_first_records_come_from_work_2026_10_12.md)
