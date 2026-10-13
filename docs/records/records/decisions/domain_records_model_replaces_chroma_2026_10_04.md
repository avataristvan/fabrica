id: domain_records_model_replaces_chroma_2026_10_04
type: domain
area: records
created: 1791065383.941984
edges: [{"target_id": "domain_learning_decision_split_subfolders_2026_09_29", "edge_type": "related"}, {"target_id": "learning_librarian_scope_was_the_game_changer_2026_10_11", "edge_type": "related"}, {"target_id": "domain_records_home_stays_for_migration_2026_10_13", "edge_type": "related"}, {"target_id": "domain_bmad_vs_ai_mem_epistemology_2026_09_25", "edge_type": "confirms"}, {"target_id": "pattern_status_markers_rot_in_memory", "edge_type": "confirms"}]
cue: I am about to change ai-mem storage, retrieval or hooks, or introduce a new record type.
---

Decision: ChromaDB is replaced. The source of truth is git-native files in four kinds: decisions/ (domain, pattern, anti-pattern), learnings/ (learning, retros, insight feedback), todos/ (open = file exists; done = delete the file and write a learning with the commit SHA) and FOCUS.md (one file per repo, overwritten, Git keeps the history; replaces current_focus). reference entries become normal documentation under docs/reference/ of the repo, decisions/insights from them move into the logs. Counters (boost_count, last_accessed_at) and the ranker are dropped; cue belongs in the files, because it carries the experience index. Retrieval without a DB: docs/records/INDEX.md + grep, linked via CLAUDE.md.
Why: The pull gap test showed that agents hardly ever call mem_query anyway; status strings in a DB go stale unnoticed (pattern_status_markers_rot_in_memory); files are reviewable in Git, distributable and readable without tooling. Round-trip test 2026-10-03: all 584 typed entries came back identical from the files.
Scope: all collections (repo.*, global, workspace, subagent.*). global/workspace/subagent.* live in the private repo ai-mem-records. User preferences do not belong in records (CLAUDE.md/memory). Implementation in four steps: placement of the 282 non-ADR entries, transfer, switch-over (hook reads FOCUS.md/todos), removal of mem_query/mem_boost/embeddings.

Addendum 2026-10-04: The removal step is implemented (domain_file_backend_replaces_chroma_2026_10_04). Narrowed: preferences that must act in every session go to CLAUDE.md, a role's yardstick stays a user record (domain_user_records_as_role_perspective_2026_10_04).
Addendum 2026-10-13: 'git keeps the history' did not hold while ai-mem's own records were gitignored; going public changed that, see domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13.
