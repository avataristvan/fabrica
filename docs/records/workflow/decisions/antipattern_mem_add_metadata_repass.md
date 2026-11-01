id: antipattern_mem_add_metadata_repass
type: anti-pattern
topic: workflow
created: 1781434290.659998
cue: I am about to update an existing record via mem_add.
---

Tried: Manually re-passing all existing metadata fields (access_count, boost_count, confidence, created_at, edges) when calling mem_add to update an entry's text.
Failed because: AddMemoryUseCase already preserves all existing metadata by default — it fetches prior_meta and merges with {**prior_meta, **user_meta}, then explicitly protects created_at and last_accessed_at. Re-passing them was redundant and introduced risk of stale values. (Note: confidence and access_count in this list are legacy fields — dropped as trust signals 2026-09-26, commit b5e5d38; they are no longer computed or read by AddMemoryUseCase at all, only carried forward untouched if already present in stored metadata. The lesson itself — don't re-pass metadata mem_add already preserves — is unchanged.)
Instead: For a text-only update, call mem_add with just documents + ids. Only pass metadatas when you explicitly want to change a field.