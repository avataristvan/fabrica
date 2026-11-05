type: pattern
topic: general
created: 1790440444.53689
---

install.py is interactive and to be run by the user only (who briefly ends the session for it): register_claude() asks for input via prompt_workspace_root() among others, and an agent call hangs on that. Do not call it, or the functions of its interactive pipeline, from an agent; propose the command and let the user run it.

Context remote session control (no restart possible, productive day-to-day workflow): hook changes take effect immediately, changes to a long-running server layer accumulate until the next restart (see [learning_mcp_servers_keep_old_code_and_cached_schema_2026_09_29](../../workflow/learnings/learning_mcp_servers_keep_old_code_and_cached_schema_2026_09_29.md)).

## Edges

- related: [learning_mcp_servers_keep_old_code_and_cached_schema_2026_09_29](../../workflow/learnings/learning_mcp_servers_keep_old_code_and_cached_schema_2026_09_29.md)
