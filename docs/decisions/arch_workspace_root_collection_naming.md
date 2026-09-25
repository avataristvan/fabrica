id: arch_workspace_root_collection_naming
type: pattern
created: 1783090344.485493
---

AI_MEM_WORKSPACE_ROOT feature (2026-07-03, commit 5e855b1): detect_repo_context() names collections from the CLAUDE.md path relative to a workspace root instead of git remote, when AI_MEM_WORKSPACE_ROOT is set. Gotcha found and fixed during implementation: hook subprocesses (hook.py/userprompt_hook.py/posttool_hook.py) do NOT inherit the env block set on the MCP server's own ~/.claude.json entry — same failure mode as pattern_blindtest_methodik documents for AI_MEM_PATH. Fix: install.py's register_claude() also prefixes the three hook commands themselves with AI_MEM_WORKSPACE_ROOT=<path>, and hook dedup-on-reinstall now matches by module name (_upsert_hook_command, "-m <module>" substring) instead of exact command string, since the env prefix changes the string on re-install.