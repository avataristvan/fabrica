id: arch_decision_userprompt_push_removed_2026_09_13
type: domain
area: architecture
created: 1789252235.413231
edges: [{"target_id": "learning_autoinject_disable_never_took_effect_2026_09_13", "edge_type": "derived_from"}, {"target_id": "arch_redesign_sketch_pull_based_2026_07_31", "edge_type": "related"}]
cue: Someone proposes that ai-mem inject context again on every prompt (UserPromptSubmit)
---

# UserPromptSubmit push removed (2026-09-13)

## Decision
UserPromptSubmit (userprompt_hook.py) removed globally, same pattern as arch_decision_pretool_push_removed_2026_09_12: `install.py` no longer registers the hook, `_remove_hook_command` self-heals existing installations on re-run (removal of `up_hooks`/`userprompt_cmd`, replaced by the same `if "UserPromptSubmit" in hooks: _remove_hook_command(...)` block as for PreToolUse). `uninstall.py` needed NO change -- `_hook_commands()` and the event loop already contained UserPromptSubmit generically, independent of whether install.py currently registers it.

## Why UserPromptSubmit and not SessionStart
UserPromptSubmit fires on EVERY single message with up to 4 parallel semantic queries; SessionStart stays active (once per session, cheap, current_focus + [available]/[available: global]). Trigger and audit finding: learning_autoinject_disable_never_took_effect_2026_09_13.

## Deployment
Deployed via `install.register_claude(workspace_root='<workspace root>')` -- a direct Python call, not the interactive `python3 install.py` flow (which asks interactively for workspace root/targets and is not headless-capable). Verified: the `hooks` block of `~/.claude/settings.json` now contains only SessionStart + PostToolUse. 365/365 tests still green.

## Cleaned up along the way: stale permissions
this repo's `.claude/settings.local.json` contained two categories of dead entries, both removed: (1) `Bash(... -m ai_mem.pretool_hook)` -- permission for the hook retired on 2026-09-12. (2) Two `Bash(cp /tmp/.../scratchpad/*.bak ~/.claude/...)` entries that pointed to a dead scratchpad path of an earlier session (52651925-...). A grep over all other `settings.local.json` files in the workspace found no further hits.

See also: arch_decision_pretool_push_removed_2026_09_12, pattern_generic_core_selective_agent_activation.

Evidence: docs/sources/automation_session_stats.md

pseudonymised for publication, 2026-10-31
