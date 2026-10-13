id: domain_archivist_mechanism_mem_and_mem_dream_2026_10_11
type: domain
area: architecture
perspective: agent
created: 1791754873.605618
edges: [{"target_id": "../fabrica:domain_archivist_who_what_how_2026_10_10", "edge_type": "derived_from"}, {"target_id": "domain_setup_seeds_nothing_first_records_come_from_work_2026_10_12", "edge_type": "related"}, {"target_id": "domain_dream_proposes_never_applies_2026_10_13", "edge_type": "related"}]
cue: when you need to know which tools the archivist writes and normalises records with
---

Decision: `mem` and `mem-dream` are the archivist's tools, and it calls mem-dream itself when a write needs more than the neighbourhood of the new record. `mem lint` reports and normalises drift in hand-written records instead of only rejecting it (adopting them: normalise to docs/reference/record-format.md, regenerate INDEX.md, set edges). mem-dream's job shifts accordingly: it consolidates by writing good cues, which prepares future recognition.
Why: Separating who (roles), what (records, agent definitions) and how (mem, mem-dream) keeps mem-dream from being a step someone has to remember to run. This is the mechanism half of domain_archivist_who_what_how_2026_10_10 (the role half lives in fabrica).
Scope: ai-mem's CLI tools only (`mem`, `mem-dream`, `mem lint`). Split off from domain_archivist_who_what_how_2026_10_10 in the 2026-10-11 redistribution (decision text of 2026-10-10, mechanism sentences unchanged).
