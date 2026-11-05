type: pattern
topic: evaluation
created: 1780077541.217354
---

# Blind-test methodology for ai-mem evaluation

Counterpart (what does NOT work: setting AI_MEM_PATH only via the MCP `env` block): [antipattern_ai_mem_path_via_mcp_env_misses_hooks](antipattern_ai_mem_path_via_mcp_env_misses_hooks.md).

## What works

**Option A: Prefix hook commands (recommended)**
Temporarily change all hook commands in `~/.claude/settings.json`:
```
AI_MEM_PATH=/tmp/ai-mem-blind python3 -m ai_mem.hook 2>/dev/null || true
```
This makes hooks AND MCP server run without the real DB. Afterwards reset + restart Claude Code.

**Not allowed: renaming or moving the DB directory** (the ai-mem store directory). The store directory is taboo (never delete the ChromaDB store): migrations and cleanups stay additive, a blind test must not touch the real DB. Formerly listed here as 'Option B', removed.

## Requirements for valid blind tests
- Hook commands AND MCP server must both point to an empty/non-existent DB
- Restart Claude Code completely after the change (not just a new session)
- Ask the test question only AFTER the restart

Status 2026-10-04 (checked in code): On the file backend an empty AI_MEM_PATH isolates nothing -- collections still resolve through cwd detection (git worktrees map to the main checkout), and an agent can Read/Grep docs/records directly. A blind arm needs the records out of reach: a fresh clone in another directory without docs/records, or a temporary copy of the repository without it.

## Edges

- derived_from: [learning_hooks_do_not_inherit_mcp_env_2026_07_03](../../architecture/learnings/learning_hooks_do_not_inherit_mcp_env_2026_07_03.md)
- related: [pattern_rubric_levels_defined_with_boundary_examples_2026_10_18](pattern_rubric_levels_defined_with_boundary_examples_2026_10_18.md)
