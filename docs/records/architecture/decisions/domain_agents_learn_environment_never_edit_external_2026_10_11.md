id: domain_agents_learn_environment_never_edit_external_2026_10_11
type: domain
area: architecture
perspective: user
created: 1791744737.225885
edges: [{"target_id": "todo_doctor_reads_environment_records_2026_10_11", "edge_type": "related"}, {"target_id": "domain_doctor_diagnoses_ritual_erosion_2026_10_10", "edge_type": "related"}, {"target_id": "../fabrica:domain_area_path_is_the_address_of_knowledge_2026_10_10", "edge_type": "related"}, {"target_id": "../fabrica:domain_archivist_who_what_how_2026_10_10", "edge_type": "related"}, {"target_id": "domain_review_is_skill_with_anchor_lint_agent_2026_10_12", "edge_type": "related"}, {"target_id": "domain_retro_default_roles_only_plugin_shipped_agents_2026_10_12", "edge_type": "related"}]
cue: Doctor or setup assistant meets an external agent/skill (graphify) as an exception and you are tempted to edit it or hard-code a list.
---

Decision: ai-mem never edits externally installed agents/skills/plugins (e.g. the graphify skill). What ai-mem's agents (doctor, archivist, librarian) need to know about the environment, e.g. that an external team carries no `handoff-protocol` hook-in by design, lives in records in that environment, not in code and not in edits to the external files. There is no interim exemption: no exclusion list in code, hard-coded or configured. Until the follow-up is done, doctor lists every team without `handoff-protocol`.
Why: an update of an external agent overwrites any edit; exemption lists in code freeze one environment's facts into the product (user: configurative, not hard-coded).
Scope: doctor Wiring check, setup assistant, plugin. Follow-up: todo_doctor_reads_environment_records_2026_10_11.
Outlook (tentative, user: "maybe fantasy"; not a commitment, no later work must follow it): ai-mem's agents might one day evolve in their environment and adapt to its conditions by learning, their records persisting as experience even when the environment is overhauled.
