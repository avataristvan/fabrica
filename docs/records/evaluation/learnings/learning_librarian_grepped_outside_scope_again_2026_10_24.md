id: learning_librarian_grepped_outside_scope_again_2026_10_24
type: learning
area: evaluation
perspective: agent
created: 1792876752.530407
edges: [{"target_id": "learning_librarian_matched_out_of_scope_files_again_2026_10_12", "edge_type": "confirms"}, {"target_id": "todo_librarian_hostile_input_test_2026_10_11", "edge_type": "related"}, {"target_id": "todo_librarian_scope_and_relied_on_parser_2026_10_11", "edge_type": "related"}]
cue: I rely on the librarian prompt alone to keep it inside its permitted read scope.
---

Observed: In the session of 2026-10-24 the librarian ran one Grep into docs/fabrica/, outside its permitted read scope, and reported it itself.
Cause: Scope is enforced only by the prompt; the same pattern as the earlier out-of-scope reads.
Evidence: learning_librarian_matched_out_of_scope_files_again_2026_10_12, learning_librarian_read_plan_and_handoff_outside_scope_2026_10_12; the librarian's self-report in that session.
