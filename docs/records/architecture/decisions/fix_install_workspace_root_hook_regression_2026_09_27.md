type: domain
topic: architecture
created: 1790525010.686958
---

Decision: install.py's register_claude() now recovers an already-installed AI_MEM_WORKSPACE_ROOT prefix (via new `_existing_workspace_root()`) when a re-run's interactive prompt is left blank, instead of silently overwriting the SessionStart/PostToolUse hook commands with no prefix.
Why: A routine reinstall must not regress the hook while the MCP entry looks fine -- update_mcp() already preserved the MCP env block on a blank prompt, the hook-command builder lacked the equivalent protection (observation and root cause: [learning_workspace_root_hook_prefix_lost_on_reinstall_2026_09_27](../learnings/learning_workspace_root_hook_prefix_lost_on_reinstall_2026_09_27.md)).
Scope: install.py -- new `_existing_workspace_root(settings_path, module)` parses the currently-installed hook command for an `AI_MEM_WORKSPACE_ROOT=` prefix; `register_claude()` falls back to it when this run's `workspace_root` is empty, before building `env_prefix`. Tests: tests/test_install.py (3 new: recovered from installed command, empty when absent, empty when settings.json missing).

## Edges

- related: [arch_workspace_root_collection_naming](arch_workspace_root_collection_naming.md)
- derived_from: [learning_workspace_root_hook_prefix_lost_on_reinstall_2026_09_27](../learnings/learning_workspace_root_hook_prefix_lost_on_reinstall_2026_09_27.md)
- derived_from: [learning_hooks_do_not_inherit_mcp_env_2026_07_03](../learnings/learning_hooks_do_not_inherit_mcp_env_2026_07_03.md)
