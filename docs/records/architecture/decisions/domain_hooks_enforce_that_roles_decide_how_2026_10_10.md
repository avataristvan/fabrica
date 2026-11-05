type: domain
topic: architecture
perspective: user
created: 1791630404.488933
---

Decision: Hooks enforce THAT a ritual happens. Roles decide HOW. Planned hooks: SubagentStop checks that a [retro] block carries records_consulted and record_candidates. `mem lint` runs when records changed. At session end, a reminder to run /reflect when work was done. These hooks never inject record content. They only check or remind.
Why: ai-mem's main operational risk is convention fragility: orchestrator-only writes, [retro] blocks and mem_dream are kept by convention, not code ([anti_pattern_convention_fragility_ai_mem_2026_10_04](../../general/learnings/anti_pattern_convention_fragility_ai_mem_2026_10_04.md) in collection `workspace`, from [dev_stack_assessment_2026_05](../../../../../../docs/sources/dev_stack_assessment_2026_05.md)). The plugin direction (archivist, handoffs, /reflect, handoff protocol) adds more convention. Judgment cannot be code-enforced, but call points can. This is not the retired push hooks: those injected content regardless of the situation, these enforce a ritual. Organisations keep the ADR ritual alive the same way, with PR templates and CI checks rather than good intentions.
Scope: plugin hooks/, the [retro] contract, `mem lint`; see docs/reference/hooks.md for the shipped hooks. Measure whether the hooks raise the rate of non-'none' records_consulted and record_candidates.

## Edges

- related: [domain_archivist_who_what_how_2026_10_10](domain_archivist_who_what_how_2026_10_10.md)
- related: [domain_reflect_yields_handoff_and_record_candidates_2026_10_10](domain_reflect_yields_handoff_and_record_candidates_2026_10_10.md)
- derived_from: [learning_organizational_not_personal_memory_2026_10_10](../learnings/learning_organizational_not_personal_memory_2026_10_10.md)
- related: [pattern_retro_learned_nothing_is_valid_2026_10_11](../../plugin/decisions/pattern_retro_learned_nothing_is_valid_2026_10_11.md)
- related: [pattern_hook_stdin_is_untrusted_2026_10_11](../../plugin/decisions/pattern_hook_stdin_is_untrusted_2026_10_11.md)
- related: [pattern_lint_hook_reports_codes_only_2026_10_11](../../plugin/decisions/pattern_lint_hook_reports_codes_only_2026_10_11.md)
- related: [learning_subagentstop_fires_for_nested_subagents_2026_10_11](../../plugin/learnings/learning_subagentstop_fires_for_nested_subagents_2026_10_11.md)
- related: [pattern_uninstall_matches_hooks_by_module_marker_2026_10_11](../../plugin/decisions/pattern_uninstall_matches_hooks_by_module_marker_2026_10_11.md)
- related: [pattern_duties_belong_in_enforcing_mechanisms_not_learnings_2026_10_18](pattern_duties_belong_in_enforcing_mechanisms_not_learnings_2026_10_18.md)
- related: [domain_coder_tests_run_by_subagentstop_hook_2026_10_19](../../../../../../docs/records/architecture/decisions/domain_coder_tests_run_by_subagentstop_hook_2026_10_19.md)
