id: learning_pull_needs_situation_triggers_2026_10_04
type: learning
area: evaluation
perspective: user
created: 1791138589.146879
edges: [{"target_id": "pattern_triggers_beat_storage_and_ranking", "edge_type": "confirms"}, {"target_id": "domain_records_model_replaces_chroma_2026_10_04", "edge_type": "confirms"}]
---

Observed: In the Navigator's experience ranking and push brought misdirected noise into the context. Pull works, but only if it happens in specific situations. The Navigator's guesses for good situations are review, bugfixing, possibly while coding, and possibly sometimes as operator. Records beat ChromaDB because they become part of a repo's or project's documentation. The Navigator sees ai-mem on the way to a good Claude Code plugin.
Cause: A stored entry has no relevance of its own; it becomes relevant in a situation. A score computed without the situation cannot tell signal from noise (eval_pull_gap_test_2026_09_20), and a push fires regardless of the situation.
Evidence: the Navigator's statement in /reflect 2026-10-04; eval_pull_gap_test_2026_09_20; learning_context_load_after_pull_switch_2026_10_04.

pseudonymised for publication, 2026-10-11
