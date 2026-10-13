id: pattern_uninstall_matches_hooks_by_module_marker_2026_10_11
type: pattern
area: plugin
perspective: the-coder
created: 1791738300.96758
edges: [{"target_id": "../fabrica:domain_hooks_enforce_that_roles_decide_how_2026_10_10", "edge_type": "related"}, {"target_id": "pattern_uninstall_recognises_commands_by_distinctive_shipped_line_2026_10_12", "edge_type": "related"}, {"target_id": "domain_plugin_hook_events_fixed_list_not_derived_from_hooks_json_2026_10_13", "edge_type": "related"}]
cue: I am adding or removing a registered hook, or touching how uninstall.py finds installed hooks
---

Rule: uninstall.py matches ai-mem hooks by the module marker (-m ai_mem.hooks.), not by the exact command. A test asserts that install's hook list and uninstall's event list agree; update both when a hook is added or removed.
When: Adding or removing a registered hook.
Why: The interpreter path inside the hook command differs across machines and installs, so exact-command matching leaves hooks behind.
Evidence: uninstall.py, tests/test_uninstall.py.
