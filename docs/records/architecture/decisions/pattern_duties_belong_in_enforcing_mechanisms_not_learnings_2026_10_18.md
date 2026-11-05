type: pattern
topic: architecture
perspective: user
created: 1792360316.267205
cue: I am about to record an "always do X after Y" duty as a learning.
---

Rule: A duty ("always do X after Y") belongs in an enforcing mechanism (hook or skill), not in a learning record. Tests in particular should run as a deterministic hook before the reviewer starts in the dev team, with falling coverage as a warning sign, instead of depending on the agent's habit.
When: Recording a lesson that says what must always be done after some change.
Why: Seniority case D6 (reword UPGRADING.md; senior reaction = rerun or call for the upgrade acceptance) scored 0 in every arm. The duty lives as [learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12](../../plugin/learnings/learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12.md) next to a root doc that looks like plain docs, so "docs-only, nothing to run" is a defensible reading. The knowledge was in the wrong medium, not missing. Evidence: [eval_seniority_main_run_result_2026_10_18](../../evaluation/learnings/eval_seniority_main_run_result_2026_10_18.md). The learning's medium is questioned, not its content.

## Edges

- derived_from: [eval_seniority_main_run_result_2026_10_18](../../evaluation/learnings/eval_seniority_main_run_result_2026_10_18.md)
- related: [learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12](../../plugin/learnings/learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12.md)
- related: [domain_hooks_enforce_that_roles_decide_how_2026_10_10](domain_hooks_enforce_that_roles_decide_how_2026_10_10.md)
- related: [domain_coder_tests_run_by_subagentstop_hook_2026_10_19](../../../../../../docs/records/architecture/decisions/domain_coder_tests_run_by_subagentstop_hook_2026_10_19.md)
- related: [learning_call_prompt_does_not_beat_agent_template_2026_10_24](../learnings/learning_call_prompt_does_not_beat_agent_template_2026_10_24.md)
