id: todo_librarian_scope_and_relied_on_parser_2026_10_11
type: todo
area: evaluation
perspective: the-coder
created: 1791725662.451336
edges: [{"target_id": "learning_librarian_files_only_eval_chunk3_2026_10_11", "edge_type": "derived_from"}, {"target_id": "learning_librarian_read_plan_and_handoff_outside_scope_2026_10_12", "edge_type": "related"}]
cue: I am about to re-run the librarian eval or score its answers
---

TODO: Limit the librarian's search to docs/records, docs/reference and docs/sources. Add a committed `Relied on` parser to scripts/eval_librarian/score.py, plus a rule for a missing `Relied on:` line. Needs a new eval run (budget).
