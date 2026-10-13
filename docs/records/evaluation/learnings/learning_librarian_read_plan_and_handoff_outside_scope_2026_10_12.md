id: learning_librarian_read_plan_and_handoff_outside_scope_2026_10_12
type: learning
area: evaluation
perspective: the-coder
created: 1791756536.806818
edges: [{"target_id": "learning_librarian_files_only_eval_chunk3_2026_10_11", "edge_type": "confirms"}, {"target_id": "todo_librarian_scope_and_relied_on_parser_2026_10_11", "edge_type": "related"}, {"target_id": "learning_librarian_matched_out_of_scope_files_again_2026_10_12", "edge_type": "related"}]
cue: I am relying on the librarian staying inside docs/records, docs/reference and docs/sources
---

Observed: The librarian read plan and handoff files outside its permitted scope (docs/records, docs/reference, docs/sources).
Cause: Nothing limits its search to those folders; its tools are Read/Grep/Glob over the whole tree.
Evidence: an earlier librarian run; learning_librarian_files_only_eval_chunk3_2026_10_11, todo_librarian_scope_and_relied_on_parser_2026_10_11.
