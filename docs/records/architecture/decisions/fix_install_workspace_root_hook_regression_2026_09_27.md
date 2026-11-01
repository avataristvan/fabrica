id: fix_install_workspace_root_hook_regression_2026_09_27
type: domain
topic: architecture
created: 1790525010.686958
edges: [{"target_id": "arch_workspace_root_collection_naming", "edge_type": "related"}, {"target_id": "learning_workspace_root_hook_prefix_lost_on_reinstall_2026_09_27", "edge_type": "derived_from"}, {"target_id": "learning_hooks_do_not_inherit_mcp_env_2026_07_03", "edge_type": "derived_from"}]
---

Decision: install.py's register_claude() now recovers an already-installed AI_MEM_WORKSPACE_ROOT prefix (via new `_existing_workspace_root()`) when a re-run's interactive prompt is left blank, instead of silently overwriting the SessionStart/PostToolUse hook commands with no prefix.
Why: A routine reinstall must not regress the hook while the MCP entry looks fine -- update_mcp() already preserved the MCP env block on a blank prompt, the hook-command builder lacked the equivalent protection (observation and root cause: learning_workspace_root_hook_prefix_lost_on_reinstall_2026_09_27).
Scope: install.py -- new `_existing_workspace_root(settings_path, module)` parses the currently-installed hook command for an `AI_MEM_WORKSPACE_ROOT=` prefix; `register_claude()` falls back to it when this run's `workspace_root` is empty, before building `env_prefix`. Tests: tests/test_install.py (3 new: recovered from installed command, empty when absent, empty when settings.json missing).
