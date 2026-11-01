id: learning_librarian_files_only_eval_chunk3_2026_10_11
type: learning
topic: evaluation
perspective: the-coder
created: 1791725662.248342
edges: [{"target_id": "eval_librarian_2026_09_26", "edge_type": "related"}, {"target_id": "learning_librarian_read_plan_and_handoff_outside_scope_2026_10_12", "edge_type": "related"}, {"target_id": "domain_internal_material_judged_by_content_and_references_2026_10_31", "edge_type": "related"}]
cue: I am hardening or re-measuring the librarian after it lost its mem_* tools, or reading its Relied on line
---

Observed: Chunk 3 (librarian without mem_* tools, Read/Grep/Glob only): the librarian Greps all of docs/ and cites ids outside the allowed set. Q2 scored 0/3 against control 3/3; the core was met and the chunk was merged anyway (user decision). Haiku sometimes drops the `Relied on:` line.
Cause: Nothing limits the search to docs/records, docs/reference and docs/sources, and the missing `Relied on:` line has no rule yet.
Evidence: scripts/eval_librarian/files_only_2026_10_11.json; baseline eval_librarian_2026_09_26.
