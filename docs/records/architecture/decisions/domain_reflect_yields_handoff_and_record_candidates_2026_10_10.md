id: domain_reflect_yields_handoff_and_record_candidates_2026_10_10
type: domain
topic: architecture
perspective: user
created: 1791629954.244394
edges: [{"target_id": "learning_context_boundary_is_read_and_write_point_2026_10_10", "edge_type": "derived_from"}, {"target_id": "domain_three_kinds_of_knowledge_age_differently_2026_10_10", "edge_type": "related"}, {"target_id": "learning_our_orchestration_matches_magentic_2026_10_11", "edge_type": "related"}, {"target_id": "domain_handoff_points_instead_of_copying_2026_10_19", "edge_type": "related"}, {"target_id": "domain_next_steps_live_in_focus_and_backlog_todo_records_retired_2026_11_02", "edge_type": "related"}]
---

Decision: /reflect at a context boundary produces two things. (1) A carry-only-conclusions handoff: charter, conclusions, open points, no history. This is state and updates FOCUS.md or a docs/handoff-<date>.md. (2) Record candidates for the archivist: decisions and learnings. The next session's charter or briefing is the question to the librarian. So every boundary has a read side (librarian) and a write side (archivist). The orchestrator runs /reflect for the overview, and subagents deliver candidates in their [retro] block.
Why: A context boundary is where the situation is explicit (learning_context_boundary_is_read_and_write_point_2026_10_10). Troy's handoff is the trigger for writing that ai-mem lacked. Separating handoff from records keeps state and decisions apart (domain_three_kinds_of_knowledge_age_differently_2026_10_10).
Scope: /reflect, the handoff protocol skill, the setup assistant (finds a team's boundaries).
