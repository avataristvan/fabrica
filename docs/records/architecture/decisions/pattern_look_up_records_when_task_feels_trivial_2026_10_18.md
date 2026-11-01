id: pattern_look_up_records_when_task_feels_trivial_2026_10_18
type: pattern
topic: architecture
perspective: user
created: 1792360316.935171
edges: [{"target_id": "eval_seniority_available_not_used_confirms_pull_gap_2026_10_18", "edge_type": "derived_from"}, {"target_id": "learning_trigger_must_name_observable_moment_2026_10_10", "edge_type": "related"}, {"target_id": "pattern_retrieval_needs_fixed_trigger_in_role_prompt", "edge_type": "related"}]
cue: I am designing agent instructions or librarian triggers, or an agent finds a task trivial and starts building.
---

Rule: An agent should get curious whenever it would decide differently than a record might suggest: when the task feels trivial but a record might say otherwise, that is the moment to look (ask the librarian or read the records).
When: Writing agent instructions and librarian trigger points; an idea from spot-check S1 of the seniority run, not yet tested.
Why: In the seniority run the records were read in only about half of the runs even when available (eval_seniority_available_not_used_confirms_pull_gap_2026_10_18); the trigger must name an observable moment (learning_trigger_must_name_observable_moment_2026_10_10).
