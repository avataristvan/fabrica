id: learning_guard_on_old_backend_artefact_silenced_sessionstart_2026_10_12
type: learning
topic: plugin
perspective: the-coder
created: 1791821370.909383
edges: [{"target_id": "domain_drop_mcp_server_for_cli_plugin_2026_10_10", "edge_type": "related"}, {"target_id": "domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31", "edge_type": "related"}]
cue: I am removing or switching a storage backend and some code still checks for files of the old one
---

Observed: A guard on an artefact of the old backend (`DB_PATH.exists()` in hook.py) silenced SessionStart on plugin-only machines.
Cause: Guards keyed to old-backend files silently disable features once the backend is switched and those files never exist.
Evidence: ai_mem/hook.py (the guard no longer keys on the old store). Related decision: domain_drop_mcp_server_for_cli_plugin_2026_10_10.

Historical since 3c64e27 (2026-10-31): the upgrade guard itself is removed from main; the code is at tag v1-last-upgrade-path. The general lesson about guards keyed to old-backend files stands.
