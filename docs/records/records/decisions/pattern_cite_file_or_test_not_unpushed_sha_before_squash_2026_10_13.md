type: pattern
topic: records
perspective: agent
created: 1791889505.768927
cue: I am about to squash or clean commits before a push and records cite commit SHAs as evidence
---

Rule: Before squashing, records cite the file or test instead of a commit SHA that the remote does not have. Check ancestry with `git merge-base --is-ancestor <sha> origin/main`. The archivist cannot run git (its Bash is limited to mem and mem-dream), so the caller precomputes the list of unpushed SHAs and runs the final private-name scan, then hands both over.
When: A blueprint or cleanup pass before a squash or push.
Why: A squash makes every unpushed SHA cited as evidence unreachable. The blueprint pass of 2026-10-13 had to fall back on the reflog to resolve them.

## Edges

- related: [pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13](pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13.md)
- related: [domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13](domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13.md)
- related: [learning_history_rewrite_orphans_commit_hashes_cited_in_records_2026_11_05](../learnings/learning_history_rewrite_orphans_commit_hashes_cited_in_records_2026_11_05.md)
