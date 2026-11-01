id: fix_install_hook_registration_2026_07_31
type: learning
topic: architecture
created: 1785517791.69763
edges: [{"target_id": "arch_workspace_root_collection_naming", "edge_type": "related"}, {"target_id": "fix_workspace_focus_false_negative", "edge_type": "related"}]
---

Observed: has_claude_md gate inconsistent across hooks.
Cause: Comparison of ctx.collection against WORKSPACE_COLLECTION/GLOBAL_COLLECTION instead of has_claude_md.
Evidence: Commit 33e0162 (formerly cited as 44f5f17); tests/test_hook.py, test_posttool_hook.py, test_userprompt_hook.py.

## has_claude_md gate consistency (Bug fix 2026-07-31, commit 33e0162, pushed to origin/main)
Fixed the has_claude_md/WORKSPACE_COLLECTION gate bug consistently across ai_mem/hook.py (two remaining gates at what were lines ~235/~245, sibling to an already-fixed gate at ~191), ai_mem/pretool_hook.py, ai_mem/posttool_hook.py, and ai_mem/userprompt_hook.py -- all now gate repo-scoped lookups on `ctx.has_claude_md` instead of comparing `ctx.collection` against WORKSPACE_COLLECTION/GLOBAL_COLLECTION, since detect_repo_context() can return collection==WORKSPACE_COLLECTION while has_claude_md==True (CLAUDE.md at the workspace root itself, or its dir falling outside AI_MEM_WORKSPACE_ROOT with no derivable git scope name). PreToolUse/pretool_hook registration (previously only documented in a comment, never implemented) is now wired up in register_claude().

In the same commit two install.py bugs in _upsert_hook_command were fixed: learning_upsert_hook_command_matcher_overwrite_2026_07_31 and learning_upsert_hook_command_identity_vs_value_equality_2026_07_31.
