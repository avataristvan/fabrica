id: domain_doctor_diagnoses_ritual_erosion_2026_10_10
type: domain
topic: architecture
created: 1791630569.932795
edges: [{"target_id": "todo_doctor_reads_environment_records_2026_10_11", "edge_type": "related"}, {"target_id": "domain_agents_learn_environment_never_edit_external_2026_10_11", "edge_type": "related"}, {"target_id": "todo_detect_skipped_reflect_gate_2026_10_11", "edge_type": "related"}, {"target_id": "learning_doctor_effect_retro_missing_signal_unreliable_2026_10_12", "edge_type": "related"}, {"target_id": "domain_hooks_enforce_that_roles_decide_how_2026_10_10", "edge_type": "derived_from"}, {"target_id": "domain_archivist_who_what_how_2026_10_10", "edge_type": "related"}]
---

Decision: ai-mem gets a doctor, similar to Claude Code's /doctor. It diagnoses whether the practice is still alive and changes nothing itself. Findings go to the setup assistant (wiring) or the archivist (records). Two parts:
- `mem doctor`: a deterministic CLI check, no LLM. It covers wiring (which teams/skills lack the handoff-protocol hook-in, are the hooks active), records (lint, dangling edges also across areas, records still under collection names, hand-written records not yet adopted), state (FOCUS.md or the last handoff older than recent commits), effect (rate of non-'none' records_consulted / record_candidates, hook flags for missing retro fields, lessons learned a third time) and migration (Chroma store without records_v1.done).
- A judgment part in the setup assistant: is this a real boundary in team X, is this really the same lesson.
Division of labour: the setup assistant enables once, hooks enforce per event, the doctor checks the whole picture on demand or periodically.
Why: Conventions do not break loudly, they fade (anti_pattern_convention_fragility_ai_mem_2026_10_04 in collection `workspace`). Hooks catch single events but not erosion over time or wiring that was never done. Facts are checked by code (cheap, reproducible), judgments by a role, mirroring domain_hooks_enforce_that_roles_decide_how_2026_10_10. The plugin thereby enables the user's AI architecture (the ai-architecture area, `..`) instead of being only a store.
Scope: `mem doctor` (growing with later chunks) and the judgment part in the setup assistant.

pseudonymised for publication, 2026-10-31
