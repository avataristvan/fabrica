type: domain
topic: architecture
perspective: user
created: 1791634114.755075
---

Decision: The why of a task reaches the coder through the handoff. /chunk-plan already asks the librarian. It writes the decisions relevant to each chunk into the chunk spec, as id plus one line of why (carry-only-conclusions). At the start of a chunk, the coder asks the librarian only for what the spec does not carry: experience with exactly the files, libraries or tools the chunk touches, from any perspective, with the-coder's own first.
Why: Knowing why a rule exists lets one apply it to cases it did not foresee, and stops one from removing a fence whose purpose is unknown (Chesterton's fence). This holds for humans (Navigator, 2026-10-10) and, as far as known, for models: Anthropic's prompting guidance recommends giving the reason behind an instruction. The planner sees the whole task, the coder the concrete files. Passing the why in the spec costs no extra spawn and keeps nesting flat. This answers the 'coding' trigger point of todo_pull_trigger_points_per_situation.
Scope: chunk-plan.md (spec carries decision ids + why), the-coder.md / dev-team.md coder template (chunk-start librarian call), handoff protocol. How the ai-architecture area applies this: [pattern_approved_decision_goes_into_executor_artifact_2026_10_12](../../../../../docs/records/workflow/decisions/pattern_approved_decision_goes_into_executor_artifact_2026_10_12.md) and [domain_chunk_plan_carries_all_boundary_anchors_2026_10_12](../../../../../docs/records/workflow/decisions/domain_chunk_plan_carries_all_boundary_anchors_2026_10_12.md) there.

pseudonymised for publication, 2026-10-11

## Edges

- derived_from: [learning_context_boundary_is_read_and_write_point_2026_10_10](../learnings/learning_context_boundary_is_read_and_write_point_2026_10_10.md)
- related: [domain_archivist_who_what_how_2026_10_10](domain_archivist_who_what_how_2026_10_10.md)
