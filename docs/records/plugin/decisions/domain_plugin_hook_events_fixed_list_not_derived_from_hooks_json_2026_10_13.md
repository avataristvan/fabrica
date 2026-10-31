id: domain_plugin_hook_events_fixed_list_not_derived_from_hooks_json_2026_10_13
type: domain
area: plugin
perspective: agent
created: 1791876534.034085
edges: [{"target_id": "pattern_uninstall_matches_hooks_by_module_marker_2026_10_11", "edge_type": "related"}, {"target_id": "domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31", "edge_type": "related"}]
cue: I want to deduplicate PLUGIN_HOOK_EVENTS in install/uninstall against hooks/hooks.json
---

Decision: `PLUGIN_HOOK_EVENTS` (install.py / uninstall.py) deliberately stays a fixed list and is not derived from `hooks/hooks.json`.
Why: It records where OLDER versions of ai-mem registered hooks in the user's settings, so that `--plugin-switch` and uninstall can find and remove them. `hooks/hooks.json` describes only what the current plugin registers; deriving the list from it would forget every event an older version used and leave those hooks behind.
Scope: PLUGIN_HOOK_EVENTS in install.py and uninstall.py. Complements pattern_uninstall_matches_hooks_by_module_marker_2026_10_11 (hooks are matched by module marker, events come from this list).
