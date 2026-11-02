id: domain_todo_prefix_ambiguity_2026_10_04
type: domain
topic: workflow
created: 1791140688.298982
edges: [{"target_id": "domain_next_steps_live_in_focus_and_backlog_todo_records_retired_2026_11_02", "edge_type": "related"}]
---

Decision: The id prefix todo_ is ambiguous in repo.ai-mem and stays so. Older todo_* ids (e.g. todo_adr_migration_2026_09_25, todo_bibliothekar_haiku_retrieval_agent_2026_09_25) are closed results filed as learnings or decisions. Open work is exactly what has type todo, i.e. a file under docs/records/<area>/todos/.
Why: Renaming the old ids would break the edges and citations that point at them. Readers judge by type and folder, not by the prefix.
Scope: repo.ai-mem records; INDEX.md's type column and the todos/ folders are authoritative.