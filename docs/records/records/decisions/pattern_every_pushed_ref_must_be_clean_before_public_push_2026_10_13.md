id: pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13
type: pattern
area: records
perspective: agent
created: 1791889505.517126
edges: [{"target_id": "domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13", "edge_type": "related"}, {"target_id": "domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12", "edge_type": "related"}]
cue: I am about to push a repo to a public remote and it has local tags or branches from before a cleanup or squash
---

Rule: Before making a history public, every ref that is pushed must be clean, not only main. Push refs by name, never `git push --tags`; keep the pre-cleanup refs local only.
When: Squashing or rewriting before a push; any repo with rollback or release tags.
Why: A local tag that points into unpushed history publishes that whole history. v0-last-mcp pointed at 55 unsquashed commits with 57 internal files. It was rebuilt as a cleaned commit on top of origin/main (same code, internal files removed, cleaned records) and the squash was placed on top. The old refs (pre-cleanup-2026-10-13, pre-squash-2026-10-13, v0-last-mcp-unclean, the worktree-agent-* branch) stay local and are never pushed.
