id: learning_trigger_must_name_observable_moment_2026_10_10
type: learning
topic: architecture
perspective: agent
created: 1791632072.445893
edges: [{"target_id": "learning_context_boundary_is_read_and_write_point_2026_10_10", "edge_type": "related"}, {"target_id": "pattern_look_up_records_when_task_feels_trivial_2026_10_18", "edge_type": "related"}, {"target_id": "learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23", "edge_type": "related"}]
---

Observed: In the session of 2026-10-10 the orchestrator did not consult memory when the Navigator's first message set the context (ai-mem, experience on demand, librarian). A rule for exactly that moment existed in the Navigator's user-level CLAUDE.md: 'On session start for feature work, query ai-mem ... before planning.' Because of that, predecessors in `global` and `workspace` were found only hours later, after decisions had been written: pattern_retrieval_needs_fixed_trigger_in_role_prompt, pattern_mixed_context_focus_degradation, pattern_convention_enforcement_gap.
Cause: The trigger named a category ('feature work'), and that required classifying the session first. A conceptual conversation about ai-mem did not feel like feature work, so the rule did not fire. A trigger works when it names an observable moment ('the first message sets the scope'), not a category.
Evidence: this session; the Navigator's user-level CLAUDE.md, Memory & Context section, rewritten on 2026-10-10 to an observable trigger.

pseudonymised for publication, 2026-10-11
