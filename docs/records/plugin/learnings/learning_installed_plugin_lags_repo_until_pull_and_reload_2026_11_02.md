type: learning
topic: plugin
perspective: agent
created: 1793657748.532556
cue: A fabrica hook or skill behaves like the version before my change (false lint finding, old /reflect text).
---

Observed: The installed plugin lags the repo. The PostToolUse lint hook falsely reported "BACKLOG.md: unparsable" (old reserved names) and /reflect loaded its old text.
Cause: The marketplace reads the clone ~/.local/share/fabrica-plugin, which must be pulled, and the session needs /reload-plugins.
Evidence: ~/.claude/plugins/known_marketplaces.json (fabrica source directory). After changing a reserved name, hook or skill: commit, git -C ~/.local/share/fabrica-plugin pull, /reload-plugins.

## Edges

- related: [learning_record_format_change_needs_rollout_plan_per_area_2026_11_05](learning_record_format_change_needs_rollout_plan_per_area_2026_11_05.md)
- related: [domain_plugin_loads_from_a_clone_pull_is_the_release_step_2026_11_05](../decisions/domain_plugin_loads_from_a_clone_pull_is_the_release_step_2026_11_05.md)
