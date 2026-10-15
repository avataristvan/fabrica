id: learning_glob_id_injection_missed_by_review_2026_10_04
type: learning
area: architecture
created: 1791138589.146879
edges: [{"target_id": "todo_holistic_opus_review_adr_migration_2026_09_25", "edge_type": "confirms"}, {"target_id": "pattern_hook_stdin_is_untrusted_2026_10_11", "edge_type": "related"}, {"target_id": "learning_symlink_following_walk_fixed_python_312_2026_10_15", "edge_type": "related"}]
cue: Ids or names from tool input become file names, paths or glob patterns, or I am writing a review prompt.
---

Observed: find_adr_files built a glob from the entry id (`**/<id>.md`), so mem_delete(ids=['*']) deleted every record of a collection, and a subagent.* collection name could leave the records home via '../'. Neither the author nor the four /simplify reviewers (reuse, quality, efficiency, architecture) found it. Only the automatic security review after the commit did.
Cause: None of the review prompts asked about hostile input. Ids and collection names come from MCP tool arguments, i.e. from model output, and they reached filesystem globs and path joins unvalidated.
Evidence: fix(security) commit 'ids and collection names can no longer act as glob patterns or escape the records home'; tests test_glob_like_ids_never_select_other_records, test_rootless_collection_names_cannot_leave_the_records_home.