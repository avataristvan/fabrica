type: pattern
topic: records
perspective: the-coder
created: 1791756531.297117
cue: I am applying a pseudonymised or translated text proposal to a record file
---

Rule: A text proposal (pseudonymised or translated) keeps the source record's frontmatter. Apply it by replacing only the body.
When: applying proposals for publication ([domain_fabrica_records_public_as_self_proof_2026_10_10](../../architecture/decisions/domain_fabrica_records_public_as_self_proof_2026_10_10.md), [domain_public_records_are_written_in_english_2026_10_12](../../architecture/decisions/domain_public_records_are_written_in_english_2026_10_12.md)).
Why: The frontmatter carries id, type, created, edges and cue; a proposal that rewrites the whole file drops or alters them.

## Edges

- related: [domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13](domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13.md)
- related: [domain_fabrica_records_public_as_self_proof_2026_10_10](../../architecture/decisions/domain_fabrica_records_public_as_self_proof_2026_10_10.md)
