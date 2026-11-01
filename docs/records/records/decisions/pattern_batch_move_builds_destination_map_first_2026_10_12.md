id: pattern_batch_move_builds_destination_map_first_2026_10_12
type: pattern
topic: records
perspective: the-coder
created: 1791756496.958505
edges: [{"target_id": "..:pattern_bulk_changes_as_deterministic_plan_apply_command_2026_10_12", "edge_type": "related"}]
cue: I am planning a batch of record moves or edge rewrites whose rows may depend on each other
---

Rule: Build the destination map for all rows of a batch first, before planning any edge or referrer rewrite for a single row.
When: any batch that moves or relinks many records (`mem move --batch`, a redistribution plan).
Why: With the full map in hand, each row is planned against the final location of every other row, so the batch is order-independent. Resume comes for free: a rerun recomputes the same plan and finds finished rows already done. Evidence: ai_mem/application/move_memory.py `plan_batch`.
