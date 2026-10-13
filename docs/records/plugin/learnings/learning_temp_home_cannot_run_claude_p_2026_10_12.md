id: learning_temp_home_cannot_run_claude_p_2026_10_12
type: learning
area: plugin
perspective: the-coder
created: 1791821371.472324
edges: [{"target_id": "learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12", "edge_type": "related"}, {"target_id": "learning_setting_sources_drops_user_claude_md_for_claude_p_2026_10_12", "edge_type": "related"}, {"target_id": "learning_temp_home_record_held_again_in_6b_2026_10_12", "edge_type": "related"}]
cue: I am writing an end-to-end test of a plugin or agent through the claude CLI and want an isolated HOME
---

Observed: Temp-HOME tests cannot run `claude -p` (copying credentials into the temp HOME was denied). The plugin exit run used the real HOME with `--setting-sources project,local --plugin-dir` instead.
Cause: claude needs the user's credentials, which an agent may not copy.
Evidence: the plugin packaging exit run. Touches the CLAUDE.md rule "run install.py/uninstall.py against a temp HOME in tests": that rule holds for install/uninstall, not for claude -p runs.
