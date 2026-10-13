id: pattern_text_proposals_replace_body_keep_frontmatter_2026_10_12
type: pattern
area: records
perspective: the-coder
created: 1791756531.297117
edges: [{"target_id": "domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13", "edge_type": "related"}, {"target_id": "domain_fabrica_records_public_as_self_proof_2026_10_10", "edge_type": "related"}]
cue: I am applying a pseudonymised or translated text proposal to a record file
---

Rule: A text proposal (pseudonymised or translated) keeps the source record's frontmatter. Apply it by replacing only the body.
When: applying proposals for publication (domain_fabrica_records_public_as_self_proof_2026_10_10, domain_public_records_are_written_in_english_2026_10_12).
Why: The frontmatter carries id, type, created, edges and cue; a proposal that rewrites the whole file drops or alters them.
