id: todo_librarian_hostile_input_test_2026_10_11
type: todo
topic: evaluation
perspective: reviewer
created: 1791725662.654372
edges: [{"target_id": "learning_librarian_files_only_eval_chunk3_2026_10_11", "edge_type": "derived_from"}, {"target_id": "todo_librarian_scope_and_relied_on_parser_2026_10_11", "edge_type": "related"}, {"target_id": "learning_librarian_grepped_outside_scope_again_2026_10_24", "edge_type": "related"}]
cue: I am deciding how far to harden the librarian against hostile input or paths outside its area
---

TODO: Write a hostile-input test for the librarian, and decide whether to harden its scope beyond the prompt. Read/Grep/Glob accept `..` and any path; there is no write or network channel. agents/librarian.md "Scope your reads" now limits it by prompt to docs/records, docs/reference and docs/sources and held once (2026-10-13), but no hostile-input test exists. From the review of the files-only librarian.
