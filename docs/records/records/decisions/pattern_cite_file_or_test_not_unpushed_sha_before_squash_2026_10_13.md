id: pattern_cite_file_or_test_not_unpushed_sha_before_squash_2026_10_13
type: pattern
topic: records
perspective: agent
created: 1791889505.768927
edges: [{"target_id": "pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13", "edge_type": "related"}, {"target_id": "domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13", "edge_type": "related"}]
cue: I am about to squash or clean commits before a push and records cite commit SHAs as evidence
---

Rule: Before squashing, records cite the file or test instead of a commit SHA that the remote does not have. Check ancestry with `git merge-base --is-ancestor <sha> origin/main`. The archivist cannot run git (its Bash is limited to mem and mem-dream), so the caller precomputes the list of unpushed SHAs and runs the final private-name scan, then hands both over.
When: A blueprint or cleanup pass before a squash or push.
Why: A squash makes every unpushed SHA cited as evidence unreachable. The blueprint pass of 2026-10-13 had to fall back on the reflog to resolve them.
