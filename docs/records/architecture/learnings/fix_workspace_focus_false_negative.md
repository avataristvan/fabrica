id: fix_workspace_focus_false_negative
type: learning
topic: architecture
created: 1785254188.230579
---

Observed: hook.py wrongly reported 'No focus entry found' although an active current_focus existed in the workspace root.
Cause: The repo_focus lookup compared ctx.collection with WORKSPACE_COLLECTION instead of using has_claude_md.
Evidence: Fix 2026-07-28 plus 3 tests in tests/test_hook.py.

Bug fix (2026-07-28): hook.py's repo_focus lookup at SessionStart used `ctx.collection != WORKSPACE_COLLECTION` to decide whether to query current_focus. This conflates two distinct cases repo_context.py already distinguishes via has_claude_md: (1) genuinely unscoped dir with no CLAUDE.md anywhere (collection falls back to 'workspace', has_claude_md=False) — correctly suppressed, and (2) CLAUDE.md literally at the workspace root (collection is also 'workspace', but has_claude_md=True — a real scope with its own current_focus). Case 2 was wrongly suppressed, causing a false 'No focus entry found' warning even when a real, actively-used current_focus entry existed in the workspace collection. Fix: gate the lookup on `ctx.has_claude_md` instead of the WORKSPACE_COLLECTION comparison; scope_name is None in the workspace-root case so the display label falls back to `ctx.scope_name or ctx.collection` to avoid printing '[None focus]'. Left the high_confidence_entries/expired_entries WORKSPACE_COLLECTION special-casing (lines ~226, 236) untouched — those are a separate, intentional noise-reduction choice not implicated by this bug. Added 3 tests to tests/test_hook.py covering: shown when has_claude_md=True with entry present, accurate warning when has_claude_md=True with entry absent, still suppressed when has_claude_md=False even if a 'workspace' entry exists.
