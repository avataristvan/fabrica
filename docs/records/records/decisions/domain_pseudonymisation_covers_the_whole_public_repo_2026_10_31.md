type: domain
topic: records
perspective: user
created: 1793470086.891643
cue: I am adding a path, name or fixture to records, sources or docs of the public repo and wonder how it must be written.
---

Decision: Pseudonymisation applies to the whole public repo, not only to records. Paths in records and sources are area-relative; docs and fixtures use `<workspace>` as placeholder; no person is named in ids or bodies; each change to a record or source is noted "pseudonymised for publication, <date>".
Why: It carries out the exception made in [domain_fabrica_records_public_as_self_proof_2026_10_10](../../architecture/decisions/domain_fabrica_records_public_as_self_proof_2026_10_10.md) (protecting people outweighs immutability of evidence) for everything a reader of the repo can open.
Scope: docs/records, docs/sources, docs/, test fixtures and scripts in the repo. Evidence: commit ed7d282. It refines the naming rules of [domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13](domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13.md) (machine paths as `~/...`) towards `<workspace>` and area-relative paths.

## Edges

- related: [domain_internal_material_judged_by_content_and_references_2026_10_31](domain_internal_material_judged_by_content_and_references_2026_10_31.md)
- derived_from: [domain_fabrica_records_public_as_self_proof_2026_10_10](../../architecture/decisions/domain_fabrica_records_public_as_self_proof_2026_10_10.md)
- related: [domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13](domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13.md)
