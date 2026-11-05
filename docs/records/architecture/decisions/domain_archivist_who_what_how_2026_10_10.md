type: domain
topic: architecture
perspective: user
created: 1791629321.361651
---

Decision: The archivist is the default writer of records, not the only door. Hand-written records stay allowed and readable. Adopting them is an archivist task: normalise them to the record format, regenerate INDEX.md, set edges. Lessons are NOT promoted into agent definitions. Those stay lean, and only the Navigator edits them, by hand. A lesson that had to be learned a third time (third-time rule) signals failed retrieval, not a missing promotion. The archivist sharpens the record's `cue:` (the situation in which it helps) and checks whether a pull point is missing. Consolidation shifts accordingly: it writes good cues, which prepares future recognition.
Why: Separating who (roles), what (records, agent definitions) and how (the tools a role uses) keeps consolidation from being a step someone has to remember to run. Promoting lessons into an agent definition is push by another name: the definition loads into every run whether the situation fits or not. It grows context and noise, like a retired auto-inject. An agent should search its own memory at its boundary instead ([domain_why_travels_with_chunk_spec_2026_10_10](domain_why_travels_with_chunk_spec_2026_10_10.md)). The cue is the closest functional analogue of human recognition ('I have been in this situation before'). So the fix for a lesson that is not recalled is a better index, not a bigger prompt. Hand-written records already exist in three areas ([learning_handwritten_records_drift_from_format_2026_10_10](../learnings/learning_handwritten_records_drift_from_format_2026_10_10.md)). The third-time rule comes from Chelsea Troy's practice 4 ([pattern_anti_corruption_layer_moment_2026_10_10](../../../../../briefing-interviewer/docs/records/practices/decisions/pattern_anti_corruption_layer_moment_2026_10_10.md) in the interview-notes project).
Scope: roles of Fabrica (librarian reads, archivist writes). The mechanism part (ai-mem's `mem` and `mem-dream` as the archivist's tools, `mem lint` normalising drift) is its own record ([domain_archivist_mechanism_mem_and_mem_dream_2026_10_11](domain_archivist_mechanism_mem_and_mem_dream_2026_10_11.md)). Revised twice on 2026-10-10: 'only writer' became 'default writer', and the promotion of lessons into agent definitions was dropped at the Navigator's objection.

pseudonymised for publication, 2026-10-11

## Edges

- derived_from: [domain_drop_mcp_server_for_cli_plugin_2026_10_10](domain_drop_mcp_server_for_cli_plugin_2026_10_10.md)
- related: [domain_user_records_as_role_perspective_2026_10_04](domain_user_records_as_role_perspective_2026_10_04.md)
- derived_from: [learning_handwritten_records_drift_from_format_2026_10_10](../learnings/learning_handwritten_records_drift_from_format_2026_10_10.md)
- related: [domain_agents_learn_environment_never_edit_external_2026_10_11](domain_agents_learn_environment_never_edit_external_2026_10_11.md)
- related: [domain_archivist_acceptance_closed_fail_use_carries_2026_10_13](../../evaluation/decisions/domain_archivist_acceptance_closed_fail_use_carries_2026_10_13.md)
- related: [domain_archivist_integration_visible_to_navigator_2026_10_15](domain_archivist_integration_visible_to_navigator_2026_10_15.md)
