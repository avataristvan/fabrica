type: learning
topic: plugin
perspective: orchestrator
created: 1791834841.912628
cue: After pulling the plugin clone I wonder if a restart, version bump or plugin update is needed, or what installed_plugins.json means
---

Observed: A plugin from a marketplace added from a local path with a relative source ("./"; here a directory marketplace holding the plugin clone) loads IN PLACE from that folder. ~/.claude/plugins/cache/ai-mem/ai-mem/0.1.0 and installPath/gitCommitSha in installed_plugins.json (still the SHA of the first install) are not what runs. Edits or pulls take effect at the next session start or /reload-plugins; no version bump and no `claude plugin update` is needed. Hooks are reportedly not reliably reloaded by /reload-plugins (community issue), so restart after a chunk that changes hooks or agents.
Cause: Claude Code distinguishes in-place plugins (local directory source) from copied ones (cache).
Evidence: code.claude.com/docs/en/plugins/loading.md "In-place and copied plugins" (checked via claude-code-guide, 2026-10-12); the update step of [pattern_install_plugin_from_clean_clone_2026_10_12](../decisions/pattern_install_plugin_from_clean_clone_2026_10_12.md); [learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12](learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12.md).

## Edges

- related: [learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12](learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12.md)
- related: [pattern_install_plugin_from_clean_clone_2026_10_12](../decisions/pattern_install_plugin_from_clean_clone_2026_10_12.md)
- related: [learning_plugin_cache_copy_is_dead_loads_in_place_2026_10_21](../../../../../briefing-interviewer/docs/records/plugin/learnings/learning_plugin_cache_copy_is_dead_loads_in_place_2026_10_21.md)
