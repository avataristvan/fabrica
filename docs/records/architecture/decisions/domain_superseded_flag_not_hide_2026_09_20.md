id: domain_superseded_flag_not_hide_2026_09_20
type: domain
area: architecture
perspective: user
created: 1789927320.601691
edges: [{"target_id": "domain_direction_judgment_over_scores_2026_09_20", "edge_type": "related"}, {"target_id": "domain_doctor_lists_external_skills_apart_2026_10_23", "edge_type": "related"}]
---

Decision: An entry that has been superseded via 'supersedes' is marked on retrieval (superseded_by, valid_until) and its current successor is attached — it is not hidden and not deleted automatically.
Why: Decision and design entries carry the why and the rejected alternatives; that is exactly the non-derivable knowledge ai-mem is meant to preserve. Hiding would conceal it, deleting would destroy it. The agent should judge for itself whether the old entry still has something to offer for the current question (judgment instead of score, see domain_direction_judgment_over_scores_2026_09_20). What is dangerous is not the outdated as such, but the outdated that looks like the current.
Scope: Edge type supersedes (source = new entry, target = old). Because edges are stored only on the source entry and retrieval only follows outgoing edges, the old entry carries the marking itself as metadata. Retrieval follows chains to the newest successor still present; this successor takes priority over ordinary edges in the attachment budget (2). A superseded entry may not supersede another (no cycles). mem_dream protects supersedes targets neither via the edge nor via access_count. Undo: mem_add with metadatas [{"superseded_by": "", "valid_until": ""}]. Does not apply to entries that are overwritten in place by convention (current_focus).
