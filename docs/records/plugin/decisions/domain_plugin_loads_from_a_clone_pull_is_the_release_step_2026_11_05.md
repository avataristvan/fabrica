type: domain
topic: plugin
perspective: user
created: 1793905718.738205
cue: You are shipping a plugin change, or wonder why another session still acts the old way, or want to symlink the clone.
---

Decision: Sessions load the fabrica plugin from the clone ~/.local/share/fabrica-plugin (a git clone of the checkout), not from the checkout, and the clone stays a clone instead of a symlink. A change reaches other sessions only after commit, pull of the clone and a session restart; for developing fabrica itself use `claude --plugin-dir <checkout>`.
Why: The pull is the release step, so other projects never run a half-done state. A running session keeps the hooks, skills and agents it started with (the librarian still answered with ids after the format change).
Scope: Shipping plugin changes; diagnosing "another session still does the old thing".

## Edges

- confirms: [learning_installed_plugin_lags_repo_until_pull_and_reload_2026_11_02](../learnings/learning_installed_plugin_lags_repo_until_pull_and_reload_2026_11_02.md)
- related: [learning_record_format_change_needs_rollout_plan_per_area_2026_11_05](../learnings/learning_record_format_change_needs_rollout_plan_per_area_2026_11_05.md)
- related: [pattern_install_plugin_from_clean_clone_2026_10_12](pattern_install_plugin_from_clean_clone_2026_10_12.md)
