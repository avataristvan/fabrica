id: todo_doctor_wiring_deferred_from_4c_2026_10_11
type: todo
area: plugin
perspective: agent
created: 1791745728.742956
edges: [{"target_id": "domain_hook_in_line_canonical_form_is_namespaced_2026_10_12", "edge_type": "related"}]
cue: I am changing the doctor Wiring check or the expected-hook table in doctor.py
---

TODO (deferred from a /simplify review of the doctor): hooks registered only in project settings show as missing in doctor Wiring (it reads ~/.claude/settings.json only, plus the enabledPlugins check for the plugin); read project settings too.
Closed from the original three: the hook-in line stays a plain substring match on purpose (domain_hook_in_line_canonical_form_is_namespaced_2026_10_12), and install.py no longer holds an ENFORCING_HOOKS table, so there is nothing left to share.
