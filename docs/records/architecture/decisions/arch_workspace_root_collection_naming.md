type: domain
topic: architecture
created: 1783090344.485493
valid_until: 1793471383.827847
---

Decision: When AI_MEM_WORKSPACE_ROOT is set, detect_repo_context() names collections from the CLAUDE.md path relative to the workspace root instead of from the git remote (feature of 2026-07-03, commit eeb3e9d). install.py register_claude() additionally prefixes the hook commands (three at the time) itself with AI_MEM_WORKSPACE_ROOT=<path>, and the hook dedup on reinstall matches by module name (_upsert_hook_command, substring "-m <module>") instead of by exact command string.

Why: Hook subprocesses do not inherit the env block set on the MCP server entry in ~/.claude.json ([learning_hooks_do_not_inherit_mcp_env_2026_07_03](../learnings/learning_hooks_do_not_inherit_mcp_env_2026_07_03.md)); without a prefix in the hook command, the hooks would never see the variable. Because the prefix changes the command string, a dedup by exact string equality no longer works on reinstall.

Scope: detect_repo_context() (collection names), install.py register_claude() and _upsert_hook_command. Edge-case fix for directories outside the root: [fix_workspace_collection_catchall_2026_07_31](fix_workspace_collection_catchall_2026_07_31.md).

## Edges

- derived_from: [learning_hooks_do_not_inherit_mcp_env_2026_07_03](../learnings/learning_hooks_do_not_inherit_mcp_env_2026_07_03.md)
- superseded_by: [domain_area_path_is_the_address_of_knowledge_2026_10_10](domain_area_path_is_the_address_of_knowledge_2026_10_10.md)
