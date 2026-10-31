id: domain_handoffs_stay_local_records_and_sources_public_2026_11_01
type: domain
area: records
perspective: user
created: 1793490845.933027
edges: [{"target_id": "domain_fabrica_records_public_as_self_proof_2026_10_10", "edge_type": "related"}, {"target_id": "domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13", "edge_type": "confirms"}]
cue: I am deciding what of the lodge book goes public, or someone proposes committing a docs/handoff-*.md
---

Decision: Handoffs (docs/handoff-*.md) stay local and are not published. Records and sources are public (pseudonymised); handoffs are not.
Why: A handoff is the roadmap (Fahrplan): where the work goes next, not the line of thought behind a decision. This resolves the tension between domain_fabrica_records_public_as_self_proof_2026_10_10, whose lodge book lists handoffs as public, and domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13, which keeps handoffs local. Already true in practice: docs/handoff-*.md is in .git/info/exclude and none is tracked.
Scope: the public ai-mem/fabrica repo. Narrows the handoffs mention in domain_fabrica_records_public_as_self_proof_2026_10_10. User decision, 2026-11-01.
