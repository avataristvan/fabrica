type: learning
topic: plugin
perspective: agent
created: 1793485172.98626
cue: You are re-installing or renaming the plugin on the development machine and think of pointing the marketplace at the working repo.
---

Observed: The installed plugin must keep loading from a clean clone outside the repo, not from the repo folder itself, even when the marketplace is re-pointed; the stale clone gets its origin set to the local repo and is pulled. An earlier plan in the session proposed pointing the marketplace directly at the repo; the librarian's recall of [pattern_install_plugin_from_clean_clone_2026_10_12](../decisions/pattern_install_plugin_from_clean_clone_2026_10_12.md) caught this at the rename's chunk start.
Cause: A loaded plugin blocks edits to its own folder (seen in the seniority eval), so pointing the marketplace at the working repo would block editing it.
Evidence: [pattern_install_plugin_from_clean_clone_2026_10_12](../decisions/pattern_install_plugin_from_clean_clone_2026_10_12.md), [anti_pattern_eval_loads_repo_under_test_as_plugin_blocks_edits_2026_10_18](../../evaluation/decisions/anti_pattern_eval_loads_repo_under_test_as_plugin_blocks_edits_2026_10_18.md).

## Edges

- related: [domain_plugin_renamed_fabrica_package_and_cli_keep_names_2026_10_31](../../architecture/decisions/domain_plugin_renamed_fabrica_package_and_cli_keep_names_2026_10_31.md)
- confirms: [pattern_install_plugin_from_clean_clone_2026_10_12](../decisions/pattern_install_plugin_from_clean_clone_2026_10_12.md)
- related: [anti_pattern_eval_loads_repo_under_test_as_plugin_blocks_edits_2026_10_18](../../evaluation/decisions/anti_pattern_eval_loads_repo_under_test_as_plugin_blocks_edits_2026_10_18.md)
