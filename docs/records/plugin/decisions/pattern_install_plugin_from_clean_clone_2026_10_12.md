id: pattern_install_plugin_from_clean_clone_2026_10_12
type: pattern
area: plugin
perspective: user
created: 1791821370.407105
edges: [{"target_id": "learning_plugin_from_local_marketplace_loads_in_place_2026_10_12", "edge_type": "related"}, {"target_id": "../briefing-interviewer:domain_install_plugin_from_area_folder_for_now_2026_10_21", "edge_type": "related"}, {"target_id": "learning_plugin_keeps_loading_from_clean_clone_when_marketplace_repointed_2026_10_31", "edge_type": "related"}]
cue: I am installing or updating a plugin that I develop locally in a checkout with git-excluded private files
---

Rule: Install a locally developed plugin from a clean clone, not from the dev checkout. ai-mem is installed from a clone outside the workspace; update with `git -C <clone> pull` and restart Claude Code.
When: Installing or updating any plugin developed locally.
Why: Git-excluded private files of the dev checkout (here the main checkout's `.mcp.json` for IntelliJ) would land at the plugin root. A clone outside the workspace also means its docs/records/ is no extra area.
