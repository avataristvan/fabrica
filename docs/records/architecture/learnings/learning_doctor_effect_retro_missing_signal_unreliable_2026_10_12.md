id: learning_doctor_effect_retro_missing_signal_unreliable_2026_10_12
type: learning
area: architecture
perspective: agent
created: 1791758109.768173
edges: [{"target_id": "domain_doctor_diagnoses_ritual_erosion_2026_10_10", "edge_type": "related"}, {"target_id": "todo_verify_retro_log_measurement_against_real_report_2026_10_12", "edge_type": "related"}, {"target_id": "domain_doctor_retired_system_check_is_keyword_heuristic_2026_10_12", "edge_type": "related"}]
cue: Reading the doctor Effect section to judge whether agents still report records_consulted and record_candidates
---

Observed: In the doctor's Effect section the `[retro]` fields show as "missing" for 75-100% of the-coder and reviewer stops (the-coder: 4 stops, 75% missing; code-reviewer: 3 stops, 100%), although the coder reports in the same session carried records_consulted and record_candidates. So the erosion signal is unreliable until it is verified against a real report.
Cause: unknown. Not yet checked: whether retro_check logs the stop before the final message exists, how nested subagent stops and duplicates are counted (see todo_chunk4c_retro_log_dedupe_and_doctor_constant_2026_10_11), or whether the parser misses the report's format.
Evidence: `mem doctor --root .` on 2026-10-12 (Effect section); the coder reports of the docs-classification session. Touches domain_doctor_diagnoses_ritual_erosion_2026_10_10.
