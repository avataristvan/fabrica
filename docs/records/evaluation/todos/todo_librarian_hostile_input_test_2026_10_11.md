id: todo_librarian_hostile_input_test_2026_10_11
type: todo
area: evaluation
perspective: reviewer
created: 1791725662.654372
edges: [{"target_id": "learning_librarian_files_only_eval_chunk3_2026_10_11", "edge_type": "derived_from"}, {"target_id": "todo_librarian_scope_and_relied_on_parser_2026_10_11", "edge_type": "related"}]
cue: I am deciding how far to harden the librarian against hostile input or paths outside its area
---

TODO: Write a hostile-input test for the librarian, and decide whether to harden its scope or keep it prompt-only. Read/Grep/Glob accept `..` and any path; there is no write or network channel. From the review of the files-only librarian.
