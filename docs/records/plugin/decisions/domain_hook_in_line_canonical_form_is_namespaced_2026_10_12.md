id: domain_hook_in_line_canonical_form_is_namespaced_2026_10_12
type: domain
topic: plugin
perspective: the-coder
created: 1791833919.258636
edges: [{"target_id": "domain_setup_seeds_nothing_first_records_come_from_work_2026_10_12", "edge_type": "related"}, {"target_id": "todo_doctor_wiring_deferred_from_4c_2026_10_11", "edge_type": "related"}, {"target_id": "domain_plugin_renamed_fabrica_package_and_cli_keep_names_2026_10_31", "edge_type": "related"}]
cue: I am writing or checking the handoff-protocol hook-in line in a team file
---

Decision: The canonical hook-in line is "At this boundary follow the Fabrica handoff protocol (skill `fabrica:handoff-protocol`)." (namespaced). Earlier forms ("the ai-mem handoff protocol", skill `ai-mem:handoff-protocol`, or un-prefixed) still pass `mem doctor` (substring match on `handoff-protocol`); setup proposes only the current form.
Why: Plugin skills are namespaced; the doctor check is a plain substring match, so old lines stay valid without a migration. Since the rename to fabrica (2026-11-01) the line was changed in the repo's skills, agents and docs, the user's global skills, agents and commands, and scripts/eval_setup.
Scope: CLAUDE.md, skills/README.md, skills/setup/SKILL.md; wiring a new team or editing the canonical line.
