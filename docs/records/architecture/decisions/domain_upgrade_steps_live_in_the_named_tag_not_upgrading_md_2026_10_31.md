type: domain
topic: architecture
perspective: user
created: 1793470086.577955
cue: I am looking for step-by-step upgrade instructions or about to edit UPGRADING.md and its acceptance run.
---

Decision: The step-by-step upgrade instructions live in the tag that the README names (v1-last-upgrade-path), not in UPGRADING.md. UPGRADING.md is removed from main (done in 3c64e27, pushed).
Why: Once main loses the upgrade path ([domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31](domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31.md)), instructions on main would describe code that is not there; the tag carries path and instructions together.
Scope: In effect since 3c64e27. Narrows [domain_current_docs_may_carry_one_short_history_section_2026_10_12](domain_current_docs_may_carry_one_short_history_section_2026_10_12.md) (its UPGRADING.md sentences only; the history-section rule stands). Historical since the same commit, evidence at the tag: [learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12](../../plugin/learnings/learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12.md), [domain_acceptance_checksum_skips_hook_written_paths_2026_10_13](../../plugin/decisions/domain_acceptance_checksum_skips_hook_written_paths_2026_10_13.md), [learning_migrate_apply_exit1_has_two_meanings_2026_10_11](../../workflow/learnings/learning_migrate_apply_exit1_has_two_meanings_2026_10_11.md), [learning_chunk0_upgrade_acceptance_passed_2026_10_15](../../plugin/learnings/learning_chunk0_upgrade_acceptance_passed_2026_10_15.md), [learning_guard_on_old_backend_artefact_silenced_sessionstart_2026_10_12](../../plugin/learnings/learning_guard_on_old_backend_artefact_silenced_sessionstart_2026_10_12.md) (its general lesson stands). Closed with the removal: [domain_plugin_hook_events_fixed_list_not_derived_from_hooks_json_2026_10_13](../../plugin/decisions/domain_plugin_hook_events_fixed_list_not_derived_from_hooks_json_2026_10_13.md) (install.py and uninstall.py gone) and todo_upgrading_md_rerun_duty_into_enforcing_mechanism_2026_10_18 (UPGRADING.md gone; the todo was deleted).
Frozen evidence: scripts/eval_seniority/run.py, scripts/eval_librarian/* and docs/plan_seniority_measurement.md (task D6) still name UPGRADING.md and install.py. They stay unchanged as evidence, but a rerun against main would mislead; a rerun needs the tag v1-last-upgrade-path.

## Edges

- derived_from: [domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31](domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31.md)
- related: [domain_current_docs_may_carry_one_short_history_section_2026_10_12](domain_current_docs_may_carry_one_short_history_section_2026_10_12.md)
- related: [learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12](../../plugin/learnings/learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12.md)
- related: [domain_acceptance_checksum_skips_hook_written_paths_2026_10_13](../../plugin/decisions/domain_acceptance_checksum_skips_hook_written_paths_2026_10_13.md)
- related: [learning_migrate_apply_exit1_has_two_meanings_2026_10_11](../../workflow/learnings/learning_migrate_apply_exit1_has_two_meanings_2026_10_11.md)
- related: [learning_chunk0_upgrade_acceptance_passed_2026_10_15](../../plugin/learnings/learning_chunk0_upgrade_acceptance_passed_2026_10_15.md)
- related: [learning_guard_on_old_backend_artefact_silenced_sessionstart_2026_10_12](../../plugin/learnings/learning_guard_on_old_backend_artefact_silenced_sessionstart_2026_10_12.md)
- related: [domain_plugin_hook_events_fixed_list_not_derived_from_hooks_json_2026_10_13](../../plugin/decisions/domain_plugin_hook_events_fixed_list_not_derived_from_hooks_json_2026_10_13.md)
