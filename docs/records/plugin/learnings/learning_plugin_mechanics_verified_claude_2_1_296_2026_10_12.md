id: learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12
type: learning
area: plugin
perspective: the-coder
created: 1791821370.176491
edges: [{"target_id": "domain_drop_mcp_server_for_cli_plugin_2026_10_10", "edge_type": "related"}, {"target_id": "learning_skill_model_frontmatter_honored_eval_under_real_model_2026_10_12", "edge_type": "related"}, {"target_id": "learning_librarian_reads_nav_reference_in_installed_plugin_2026_10_12", "edge_type": "related"}, {"target_id": "learning_plugin_from_local_marketplace_loads_in_place_2026_10_12", "edge_type": "related"}, {"target_id": "learning_bash_sandbox_masks_protected_paths_in_cwd_2026_10_12", "edge_type": "related"}, {"target_id": "domain_mem_delete_names_dangling_edges_2026_10_13", "edge_type": "related"}]
cue: I am writing or wiring plugin agents, skills, hooks or options and need to know what a plugin can reference where
---

Observed: Claude Code plugin mechanics, verified on claude 2.1.296 while packaging the plugin: (1) `<plugin>:<agent>` works as subagent_type. (2) Plugin skills are namespaced (`/ai-mem:reflect`), but a bare `/reflect` works as an alias when the name is unique. (3) The plugin's `bin/` is on a subagent's Bash PATH. (4) `${CLAUDE_PLUGIN_ROOT}` expands in agent and skill bodies and in the hook env, NOT in the Bash tool. (5) `CLAUDE_PLUGIN_OPTION_<KEY>` reaches hooks only once a value is set; no default is exported, so every option needs a file/default fallback. (6) `${user_config.KEY}` is not substituted in agent bodies.
Cause: Plugin variable expansion is done per surface (bodies, hook env), not by the shell.
Evidence: hooks/hooks.json, agents/ and skills/ of the plugin; user check 2026-10-12 (bare /reflect resolved).
