id: domain_doctor_and_reflect_reminder_accept_old_ai_mem_names_2026_10_31
type: domain
area: plugin
perspective: agent
created: 1793485172.745218
edges: [{"target_id": "domain_plugin_renamed_fabrica_package_and_cli_keep_names_2026_10_31", "edge_type": "related"}]
cue: You are cleaning up the "ai-mem@" or "ai-mem:reflect" literals in doctor.py or reflect_reminder.py.
---

Decision: After the rename to fabrica, mem doctor (plugin enabled check) and the reflect reminder still accept the old ai-mem names next to fabrica.
Why: An installation that has not reinstalled yet would otherwise be reported as unwired or nagged after a /ai-mem:reflect.
Scope: compatibility only; new text uses fabrica. Evidence: e2872a1, ai_mem/doctor.py, ai_mem/hooks/reflect_reminder.py.
