id: todo_chunk4c_retro_log_dedupe_and_doctor_constant_2026_10_11
type: todo
area: plugin
perspective: user
created: 1791738307.851608
edges: [{"target_id": "todo_doctor_wiring_deferred_from_4c_2026_10_11", "edge_type": "related"}, {"target_id": "learning_doctor_effect_retro_missing_signal_unreliable_2026_10_12", "edge_type": "related"}]
cue: I am reading retro_log.jsonl or the doctor_last_run pointer, or changing how retro_check logs stops
---

TODO: (1) Deduplicate retro_log.jsonl by agent_id, since a blocked agent logs twice; (2) give doctor_last_run one shared constant between doctor.py (writer) and hook._doctor_pointer (reader).
