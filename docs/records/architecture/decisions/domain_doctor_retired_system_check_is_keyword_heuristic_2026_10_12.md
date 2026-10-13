id: domain_doctor_retired_system_check_is_keyword_heuristic_2026_10_12
type: domain
area: architecture
perspective: the-coder
created: 1791758106.579595
edges: [{"target_id": "domain_docs_split_into_documentation_and_sources_2026_10_10", "edge_type": "derived_from"}, {"target_id": "learning_doctor_effect_retro_missing_signal_unreliable_2026_10_12", "edge_type": "related"}, {"target_id": "pattern_doctor_exit_criterion_check_scanner_covers_destination_2026_10_12", "edge_type": "related"}, {"target_id": "todo_doctor_retired_system_check_sidestepped_by_softer_wording_2026_10_12", "edge_type": "related"}]
cue: Wondering why mem doctor flags or misses a doc as describing a retired system
---

Decision: The doctor's "retired system in current doc" check is a keyword heuristic over the documentation (ChromaDB, MCP server, BM25, daemon, experience index). A doc counts as marked when it has `status: historical` or `status: plan` frontmatter, or a `>` banner in its first 5 lines that names superseded, dropped, historical or retired.
Why: It is deterministic: the same files always give the same findings, with no model judgment. The plan of the docs chunk prescribed the keywords. The price: a doc may mention a keyword legitimately (it then needs a marker or a rewrite) and a retired system under another name is missed.
Scope: ai_mem/doctor_sources.py, the Sources section of `mem doctor`. Evidence: ai_mem/doctor_sources.py.
