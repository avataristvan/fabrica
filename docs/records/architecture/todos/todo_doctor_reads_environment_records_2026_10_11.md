id: todo_doctor_reads_environment_records_2026_10_11
type: todo
area: architecture
perspective: user
created: 1791744729.58945
edges: [{"target_id": "domain_doctor_diagnoses_ritual_erosion_2026_10_10", "edge_type": "related"}, {"target_id": "domain_agents_learn_environment_never_edit_external_2026_10_11", "edge_type": "derived_from"}]
cue: Changing the doctor Wiring check or its handling of external teams/skills such as graphify that lack a hook-in.
---

TODO: make `mem doctor` (Wiring) read environment records (e.g. "external team, no handoff-protocol hook-in by design") so it stops listing such teams as findings. Until then doctor lists every team without `handoff-protocol`; there is no code list to drop. Decision: domain_agents_learn_environment_never_edit_external_2026_10_11.
