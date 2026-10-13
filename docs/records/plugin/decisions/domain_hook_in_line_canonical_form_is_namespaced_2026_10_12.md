id: domain_hook_in_line_canonical_form_is_namespaced_2026_10_12
type: domain
area: plugin
perspective: the-coder
created: 1791833919.258636
edges: [{"target_id": "domain_setup_seeds_nothing_first_records_come_from_work_2026_10_12", "edge_type": "related"}, {"target_id": "todo_doctor_wiring_deferred_from_4c_2026_10_11", "edge_type": "related"}]
cue: I am writing or checking the handoff-protocol hook-in line in a team file
---

Decision: The canonical hook-in line is "At this boundary follow the ai-mem handoff protocol (skill `ai-mem:handoff-protocol`)." (namespaced). The older un-prefixed form still passes `mem doctor` (substring match); setup proposes only the `ai-mem:` prefix form.
Why: Plugin skills are namespaced; the doctor check is a plain substring match, so old lines stay valid without a migration.
Scope: CLAUDE.md, skills/README.md, skills/setup/SKILL.md.
