type: learning
topic: workflow
perspective: agent
created: 1792061620.198584
cue: You are changing how record files are found or deleted, or want to filter symlinks out of the record walk.
---

Observed: The symlink-following delete is fixed in commit dee347c. iter_record_files and find_adr_files walked with rglob, which on Python <= 3.12 enters symlinked folders, so remove_files could delete real files outside the area. Python 3.13+ rglob does not, which is why the bug was invisible on this machine. They now use os.walk(followlinks=False). Symlinked FILES stay visible on purpose: records_lint reports them and mem move refuses them via is_contained; hiding them would let mem move write through the link. remove_files skips any path whose folder resolves outside the area; a symlinked record inside the area is unlinked (unlink never touches the target).
Cause: Behaviour of rglob differs by Python version. A first guard checked the file's own resolved path and silently kept in-area links while callers reported them removed; the review (reviewer) caught it.
Evidence: commit dee347c; tests/infrastructure/test_adr_paths.py (symlink tests); 615 tests passing.

## Edges

- related: [learning_glob_id_injection_missed_by_review_2026_10_04](../../architecture/learnings/learning_glob_id_injection_missed_by_review_2026_10_04.md)
- related: [domain_rebuild_closing_scoped_to_two_todos_2026_10_15](../../architecture/decisions/domain_rebuild_closing_scoped_to_two_todos_2026_10_15.md)
