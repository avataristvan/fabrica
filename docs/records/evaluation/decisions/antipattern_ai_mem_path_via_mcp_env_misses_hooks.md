id: antipattern_ai_mem_path_via_mcp_env_misses_hooks
type: anti-pattern
area: evaluation
created: 1790700222.841447
edges: [{"target_id": "learning_hooks_do_not_inherit_mcp_env_2026_07_03", "edge_type": "related"}, {"target_id": "pattern_blindtest_methodik", "edge_type": "related"}]
---

Tried: Setting `env: {AI_MEM_PATH: /tmp/blind}` in the MCP server entry of `~/.claude.json` to run a blind test without the real DB.
Failed because: The `env` parameter applies only to the MCP server subprocess. Hooks (`ai_mem.hook`, `ai_mem.userprompt_hook`, `ai_mem.posttool_hook`) inherit the system environment from Claude Code -- they read the real DB path (learning_hooks_do_not_inherit_mcp_env_2026_07_03). In addition it was observed that Claude Code reuses the MCP server process after a session restart, so env changes only took effect after a complete restart of the app -- in which client this was observed is not recorded; learning_mcp_servers_keep_old_code_and_cached_schema_2026_09_29 saw a new server process per session in the CLI (process reuse is therefore client-dependent or unverified).
Instead: Prefix the hook commands themselves with AI_MEM_PATH and restart completely -- see pattern_blindtest_methodik.
