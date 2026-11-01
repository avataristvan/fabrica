id: domain_internal_records_stay_out_of_public_areas_2026_10_12
type: domain
topic: architecture
perspective: user
created: 1791756496.674797
edges: [{"target_id": "domain_fabrica_records_public_as_self_proof_2026_10_10", "edge_type": "related"}, {"target_id": "domain_public_face_experience_report_not_launch_2026_10_24", "edge_type": "related"}]
cue: I am placing a record that documents internals or private history, and the target area has or will have a public remote
---

Decision: Records are a blueprint, and the freedom to clean them is kept. Internal records (internals of the tooling, private history, details of the environment) stay out of public areas. Public areas are those with a public remote or one planned: ai-mem, which since 2026-10-14 also holds Fabrica. Such a record goes to a private area without a remote. The first internal record lives in a private internal area. A gitignored place for internals inside a public repo may follow.
Why: Publishing the line of thought is deliberate (domain_fabrica_records_public_as_self_proof_2026_10_10), but that decision generalises or pseudonymises private details in place. Internals have no public value and cannot be generalised away, so they are placed where they never leave the machine. Keeping them out of the public area also keeps the public records free of cleaning that only serves privacy.
Scope: choosing the area when writing a record (archivist, hand-written records, redistribution). Public area: ai-mem (with Fabrica). Narrows and complements the self-proof decision; the private-by-default stance of domain_ai_mem_records_private_gitignored_2026_10_04 (in the private internal area) now applies to internals only.
