id: todo_tell_external_installation_plugin_is_now_fabrica_2026_10_31
type: todo
area: architecture
perspective: user
created: 1793485173.213565
edges: [{"target_id": "domain_plugin_renamed_fabrica_package_and_cli_keep_names_2026_10_31", "edge_type": "derived_from"}, {"target_id": "todo_verify_external_installation_migration_and_plugin_switch_2026_10_15", "edge_type": "related"}]
cue: You are about to rely on the external installation after the rename, or it reports the ai-mem@ai-mem plugin as missing.
---

TODO: Tell the external installation that the plugin is now fabrica@fabrica. After its next pull the old ai-mem@ai-mem entry likely no longer resolves and needs one reinstall (untested).
