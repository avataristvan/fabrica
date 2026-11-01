id: learning_workspace_root_hook_prefix_lost_on_reinstall_2026_09_27
type: learning
topic: architecture
created: 1790678554.072722
---

Observed: A parallel session in another project reported that the SessionStart hook for a nested git repo resolved a legacy collection `repo.<Project>` instead of the workspace-root-based `repo.<Group>.<Project>` that its CLAUDE.md actually uses. On the maintainer's machine: `~/.claude.json` mcpServers.ai-mem.env had AI_MEM_WORKSPACE_ROOT=<workspace root> correctly, but the SessionStart/PostToolUse hook commands in `~/.claude/settings.json` had no prefix at all -- the hooks silently ran on the git-based fallback naming for EVERY project, not just that one.
Cause: `prompt_workspace_root()` asks again on every install.py run without the `--workspace-root` flag. `update_mcp()` already preserved the existing env block of the MCP entry on empty input, the hook command builder had no corresponding protection -- a routine reinstall (e.g. for an unrelated fix) silently regressed the hook while the MCP server looked intact. The *design* was correct (detect_repo_context() checks AI_MEM_WORKSPACE_ROOT before the git fallback; install.py passes it into the hook commands, see key_invariants), it just was not applied.
Evidence: Investigation 2026-09-27; the installed hook commands repaired manually; tests/test_install.py (3 new tests). Related: learning_hooks_do_not_inherit_mcp_env_2026_07_03.
