type: learning
topic: records
perspective: agent
created: 1793905709.862686
cue: You are rewriting or squashing history, or reviewing records before a push, and records cite commit hashes.
---

Observed: A history rewrite orphaned commit hashes cited in records: five hashes from before the 2026-10-04 rewrite (093dc1b, ffb7bc9, b0063b8, b7559c8, e509eda) lived only on a local backup branch or nowhere, invisible to anyone cloning. `mem review` found them at the push; the equivalents on main were found by identical commit subject and repointed (commit 8d4f26c).
Cause: Hashes are only stable after the last amend or rewrite; the records cited them earlier. The review at the push is the moment this surfaces.
Evidence: commit 8d4f26c; ai_mem/review.py.

## Edges

- confirms: [pattern_status_markers_rot_in_memory](../../workflow/decisions/pattern_status_markers_rot_in_memory.md)
- related: [pattern_cite_file_or_test_not_unpushed_sha_before_squash_2026_10_13](../decisions/pattern_cite_file_or_test_not_unpushed_sha_before_squash_2026_10_13.md)
