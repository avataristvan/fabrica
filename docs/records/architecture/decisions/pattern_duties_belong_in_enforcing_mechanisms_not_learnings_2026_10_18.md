id: pattern_duties_belong_in_enforcing_mechanisms_not_learnings_2026_10_18
type: pattern
topic: architecture
perspective: user
created: 1792360316.267205
edges: [{"target_id": "eval_seniority_main_run_result_2026_10_18", "edge_type": "derived_from"}, {"target_id": "learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12", "edge_type": "related"}, {"target_id": "domain_hooks_enforce_that_roles_decide_how_2026_10_10", "edge_type": "related"}, {"target_id": "../..:domain_coder_tests_run_by_subagentstop_hook_2026_10_19", "edge_type": "related"}, {"target_id": "learning_call_prompt_does_not_beat_agent_template_2026_10_24", "edge_type": "related"}]
cue: I am about to record an "always do X after Y" duty as a learning.
---

Rule: A duty ("always do X after Y") belongs in an enforcing mechanism (hook or skill), not in a learning record. Tests in particular should run as a deterministic hook before the reviewer starts in the dev team, with falling coverage as a warning sign, instead of depending on the agent's habit.
When: Recording a lesson that says what must always be done after some change.
Why: Seniority case D6 (reword UPGRADING.md; senior reaction = rerun or call for the upgrade acceptance) scored 0 in every arm. The duty lives as learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12 next to a root doc that looks like plain docs, so "docs-only, nothing to run" is a defensible reading. The knowledge was in the wrong medium, not missing. Evidence: eval_seniority_main_run_result_2026_10_18. The learning's medium is questioned, not its content.
