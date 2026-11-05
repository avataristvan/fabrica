type: domain
topic: architecture
perspective: user
created: 1791744737.225885
cue: Doctor or setup assistant meets an external agent/skill (graphify) as an exception and you are tempted to edit it or hard-code a list.
---

Decision: ai-mem never edits externally installed agents/skills/plugins (e.g. the graphify skill). What ai-mem's agents (doctor, archivist, librarian) need to know about the environment, e.g. that an external team carries no `handoff-protocol` hook-in by design, lives in records in that environment, not in code and not in edits to the external files. There is no interim exemption: no exclusion list in code, hard-coded or configured. Until the follow-up is done, doctor lists every team without `handoff-protocol`.
Why: an update of an external agent overwrites any edit; exemption lists in code freeze one environment's facts into the product (user: configurative, not hard-coded).
Scope: doctor Wiring check, setup assistant, plugin. Follow-up: todo_doctor_reads_environment_records_2026_10_11.
Outlook (tentative, user: "maybe fantasy"; not a commitment, no later work must follow it): ai-mem's agents might one day evolve in their environment and adapt to its conditions by learning, their records persisting as experience even when the environment is overhauled.

## Edges

- related: [domain_doctor_diagnoses_ritual_erosion_2026_10_10](domain_doctor_diagnoses_ritual_erosion_2026_10_10.md)
- related: [domain_review_is_skill_with_anchor_lint_agent_2026_10_12](../../workflow/decisions/domain_review_is_skill_with_anchor_lint_agent_2026_10_12.md)
- related: [domain_retro_default_roles_only_plugin_shipped_agents_2026_10_12](../../plugin/decisions/domain_retro_default_roles_only_plugin_shipped_agents_2026_10_12.md)
- related: [pattern_findings_about_outside_files_go_to_their_topic_area_2026_10_13](pattern_findings_about_outside_files_go_to_their_topic_area_2026_10_13.md)
- related: [domain_area_path_is_the_address_of_knowledge_2026_10_10](domain_area_path_is_the_address_of_knowledge_2026_10_10.md)
- related: [domain_archivist_who_what_how_2026_10_10](domain_archivist_who_what_how_2026_10_10.md)
- related: [domain_doctor_lists_external_skills_apart_2026_10_23](domain_doctor_lists_external_skills_apart_2026_10_23.md)
