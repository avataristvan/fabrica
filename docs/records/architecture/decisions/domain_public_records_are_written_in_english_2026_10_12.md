id: domain_public_records_are_written_in_english_2026_10_12
type: domain
topic: architecture
perspective: user
created: 1791756505.482973
edges: [{"target_id": "domain_internal_records_stay_out_of_public_areas_2026_10_12", "edge_type": "related"}, {"target_id": "domain_fabrica_records_public_as_self_proof_2026_10_10", "edge_type": "related"}]
cue: I am writing or moving a record into an area that is or will be public, or find German records there
---

Decision: Records that go public are written in English. German records are translated before publication.
Why: A public record base is read by people outside the workspace; one language keeps it readable and searchable. Evidence: 80 records were translated before publication (the batch QA pass is pattern_translation_batch_qa_pass in the ai-architecture area).
Scope: public areas (ai-mem, which holds Fabrica). Private areas may keep their language. Translated text follows the pseudonymisation rule of domain_fabrica_records_public_as_self_proof_2026_10_10.
