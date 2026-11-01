id: todo_detect_skipped_reflect_gate_2026_10_11
type: todo
topic: architecture
perspective: agent
created: 1791745728.302433
edges: [{"target_id": "domain_doctor_diagnoses_ritual_erosion_2026_10_10", "edge_type": "related"}, {"target_id": "domain_reflect_yields_handoff_and_record_candidates_2026_10_10", "edge_type": "related"}, {"target_id": "pattern_reflect_between_chunks", "edge_type": "related"}]
cue: I am extending mem doctor, or I am about to skip /reflect at a chunk boundary because of the budget
---

TODO: Make `mem doctor` detect a skipped reflect gate, e.g. commits on main since the last record or FOCUS.md change.
Why: The reflect gate was skipped for three chunks under the budget rule. The candidates survived only in a handoff file. mem doctor did not notice, because retro data was empty. A convention without a check erodes (domain_doctor_diagnoses_ritual_erosion_2026_10_10).
