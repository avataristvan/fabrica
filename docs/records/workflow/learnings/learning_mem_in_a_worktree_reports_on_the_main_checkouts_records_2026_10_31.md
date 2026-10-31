id: learning_mem_in_a_worktree_reports_on_the_main_checkouts_records_2026_10_31
type: learning
area: workflow
perspective: the-coder
created: 1793471377.493848
edges: [{"target_id": "learning_editable_install_python_i_resolves_main_checkout_not_worktree_2026_10_12", "edge_type": "related"}]
cue: I run bin/mem doctor or another mem command from a git worktree and expect it to report on the worktree's own records.
---

Observed: In a worktree, `bin/mem doctor` reports on the main checkout's records, not on the worktree's.
Cause: Worktrees map to their main checkout (`_to_main_checkout`, also used by areas.py), so the area resolves to the main checkout's docs/records/.
Evidence: removal chunk of 2026-10-31 (fe8403f, pushed); ai_mem/infrastructure/areas.py. Related: learning_editable_install_python_i_resolves_main_checkout_not_worktree_2026_10_12.
