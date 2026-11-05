type: domain
topic: records
perspective: user
created: 1793491177.422389
cue: I am deciding whether a docs/handoff-*.md goes into the public repo, or someone cites handoffs as local-only
---

Decision: Handoffs (docs/handoff-*.md) may be published after all, pseudonymised in place like records and sources (the rules of [domain_fabrica_records_public_as_self_proof_2026_10_10](../../architecture/decisions/domain_fabrica_records_public_as_self_proof_2026_10_10.md)). Publishing the handoff files themselves waits for the user's review of the pseudonymised versions; they are committed locally, not pushed.
Why: A handoff can be very insightful for a reader: it shows how the work was steered from session to session, which is part of the self-proof. The earlier reason (a handoff is the roadmap) is not dropped but no longer decisive. Weighed against [domain_handoffs_stay_local_records_and_sources_public_2026_11_01](domain_handoffs_stay_local_records_and_sources_public_2026_11_01.md), made earlier the same day.
Scope: the public ai-mem/fabrica repo. User decision, 2026-11-01. The review has happened: the user approved publication of the two past handoffs, now sources.
Evidence: docs/sources/handoff_2026_10_13.md, docs/sources/handoff_2026_10_21.md

## Edges

- supersedes: [domain_handoffs_stay_local_records_and_sources_public_2026_11_01](domain_handoffs_stay_local_records_and_sources_public_2026_11_01.md)
- related: [domain_fabrica_records_public_as_self_proof_2026_10_10](../../architecture/decisions/domain_fabrica_records_public_as_self_proof_2026_10_10.md)
- related: [domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13](domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13.md)
