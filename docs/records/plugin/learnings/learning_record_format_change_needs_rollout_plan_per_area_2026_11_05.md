type: learning
topic: plugin
perspective: agent
created: 1793885901.11564
cue: You are shipping a record-format or lint change, or another session suddenly cannot edit its records.
---

Observed: Sessions load the plugin from the clone ~/.local/share/fabrica-plugin, not from the working checkout; a repo change reaches other sessions once it is committed, the clone is pulled and the session reloads (see the earlier learning). After that, an area still in the old record format gets its old records blocked by the lint_after_write hook (legacy-refs/bare-id findings) until `mem lint --fix` runs there.
Cause: The hook checks against the new lint rules while the area's files are still old. A format change therefore needs a rollout plan per area, not just a commit. Extends the earlier learning on the lagging plugin.
Evidence: ~/.local/share/fabrica-plugin (git clone of this checkout); ai_mem/hooks/lint_after_write.py; coordinator check 2026-11-05 (the ~/.claude/plugins/cache/fabrica/fabrica/0.1.0 copy is stale and not used by loaded skills).

## Edges

- related: [domain_records_have_no_id_links_by_file_name_2026_11_05](../../records/decisions/domain_records_have_no_id_links_by_file_name_2026_11_05.md)
- confirms: [learning_installed_plugin_lags_repo_until_pull_and_reload_2026_11_02](learning_installed_plugin_lags_repo_until_pull_and_reload_2026_11_02.md)
- related: [domain_plugin_loads_from_a_clone_pull_is_the_release_step_2026_11_05](../decisions/domain_plugin_loads_from_a_clone_pull_is_the_release_step_2026_11_05.md)
