type: learning
topic: plugin
perspective: orchestrator
created: 1791834833.045599
cue: The librarian answers empty or permission denied on its navigation reference and I wonder if the installed plugin is broken
---

Observed: In a normal interactive session with the installed plugin, the librarian (haiku) read reference/navigating_records.md under the plugin root without error and answered from the records. The permission denial seen in every setup eval run is specific to `claude -p --plugin-dir <dir outside cwd>`, not to the installed plugin; no --add-dir or permission entry is needed.
Cause: The eval runs read the plugin root from outside the cwd under a non-interactive permission mode; the installed plugin is not subject to that.
Evidence: check after the setup chunk, 2026-10-12; answers the closed todo todo_check_librarian_nav_reference_permission_in_installed_plugin_2026_10_12; context in [learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12](learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12.md).

## Edges

- related: [learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12](learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12.md)
