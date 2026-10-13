id: todo_symlink_following_delete
type: todo
area: workflow
created: 1791668867.952025
edges: [{"target_id": "learning_glob_id_injection_missed_by_review_2026_10_04", "edge_type": "related"}]
---

TODO (push security review 2026-10-10): adr_paths.iter_record_files uses rglob, which follows symlinked directories under docs/records/, so remove_files can delete real files outside the area. Do not follow symlinks and never touch anything outside adr_dir.
