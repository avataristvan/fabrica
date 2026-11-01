id: learning_hooks_do_not_inherit_mcp_env_2026_07_03
type: learning
topic: architecture
created: 1790678543.79727
---

Observed: Hook subprocesses (hook.py / userprompt_hook.py / posttool_hook.py) do NOT inherit the `env` block set on the MCP server entry in ~/.claude.json (noticed during the implementation of AI_MEM_WORKSPACE_ROOT, 2026-07-03).
Cause: The env block of an MCP server entry applies only to the MCP server subprocess; hooks inherit the system environment from Claude Code -- the same class of error that pattern_blindtest_methodik documents for AI_MEM_PATH.
Evidence: Commit eeb3e9d (AI_MEM_WORKSPACE_ROOT feature, in which the error was found and fixed; formerly cited as 5e855b1, hash invalidated by a history rewrite); pattern_blindtest_methodik (same cause for AI_MEM_PATH).
