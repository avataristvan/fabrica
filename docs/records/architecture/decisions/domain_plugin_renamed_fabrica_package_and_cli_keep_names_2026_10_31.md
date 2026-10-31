id: domain_plugin_renamed_fabrica_package_and_cli_keep_names_2026_10_31
type: domain
area: architecture
perspective: user
created: 1793485172.510591
edges: [{"target_id": "todo_rename_folder_and_plugin_to_fabrica_2026_10_31", "edge_type": "related"}, {"target_id": "domain_repo_renamed_fabrica_folder_and_plugin_stay_2026_10_15", "edge_type": "related"}, {"target_id": "domain_retro_default_roles_only_plugin_shipped_agents_2026_10_12", "edge_type": "related"}, {"target_id": "domain_hook_in_line_canonical_form_is_namespaced_2026_10_12", "edge_type": "related"}]
cue: You wonder why the plugin is called fabrica while the code says ai_mem and mem, or want to rename the Python package or CLI.
---

Decision: The plugin and marketplace are renamed to fabrica (agents fabrica:<agent>, skills /fabrica:<skill>, install fabrica@fabrica). The Python package ai_mem and the CLI mem keep their names.
Why: Fabrica is the public name of the repo and the method; package and CLI are internals, and renaming them would only churn imports, the editable install and every `mem` call without a visible gain.
Scope: the plugin identity. "ai-mem" stays as the name of the memory part in prose. Evidence: commit e2872a1 (pushed 2026-10-31). The repo part of todo_rename_folder_and_plugin_to_fabrica_2026_10_31 is done; folder move, cross-area edges, outside references and the plugin reinstall remain. This replaces the plugin part of domain_repo_renamed_fabrica_folder_and_plugin_stay_2026_10_15, and makes `fabrica:anchor-lint` the default retro role and `fabrica:` the canonical hook-in prefix.
