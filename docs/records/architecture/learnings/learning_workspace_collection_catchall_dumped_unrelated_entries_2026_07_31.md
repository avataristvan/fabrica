id: learning_workspace_collection_catchall_dumped_unrelated_entries_2026_07_31
type: learning
area: architecture
created: 1790678548.833528
---

Observed: If a directory had its own CLAUDE.md but lay outside `AI_MEM_WORKSPACE_ROOT` (or the variable was unset) and was not a git repo, `detect_repo_context` fell back to the shared `WORKSPACE_COLLECTION` ("workspace") instead of scoping by its own directory name. This tipped entries of unrelated projects into the shared `workspace` collection, which then surfaced as noisy, off-topic hits in `userprompt_hook`'s injected context (scores 0.6-0.9, but no real relevance to the current prompt).
Cause: WORKSPACE_COLLECTION was wrongly used as a catch-all.
Evidence: Found via context audit; fixed 2026-07-31. Related: arch_workspace_root_collection_naming, fix_workspace_focus_false_negative, collections_scoping.
