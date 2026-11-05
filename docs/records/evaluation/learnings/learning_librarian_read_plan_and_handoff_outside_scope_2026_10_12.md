type: learning
topic: evaluation
perspective: the-coder
created: 1791756536.806818
cue: I am relying on the librarian staying inside docs/records, docs/reference and docs/sources
---

Observed: The librarian read plan and handoff files outside its permitted scope (docs/records, docs/reference, docs/sources).
Cause: Nothing limited its search to those folders; its tools are Read/Grep/Glob over the whole tree.
Evidence: an earlier librarian run; [learning_librarian_files_only_eval_chunk3_2026_10_11](learning_librarian_files_only_eval_chunk3_2026_10_11.md), todo_librarian_scope_and_relied_on_parser_2026_10_11.
Update 2026-10-13: the scope rule now exists (agents/librarian.md "Scope your reads") and held: the librarian called the chunk plan "not readable under my scope".

## Edges

- confirms: [learning_librarian_files_only_eval_chunk3_2026_10_11](learning_librarian_files_only_eval_chunk3_2026_10_11.md)
- related: [learning_librarian_matched_out_of_scope_files_again_2026_10_12](learning_librarian_matched_out_of_scope_files_again_2026_10_12.md)
