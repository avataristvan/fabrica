type: domain
topic: plugin
perspective: user
created: 1791839505.102506
cue: I am changing which agents retro_check demands a [retro] block from, or the-coder is no longer checked after a plugin update
---

Decision: The default retro roles of the SubagentStop hook retro_check are only `ai-mem:anchor-lint`, the agent the plugin ships itself. Your own teams (e.g. `the-coder`) are added through the plugin option `retro_roles` (or `$AI_MEM_PATH/retro_roles.json`). User decided on 2026-10-12 (option A).
Why: An external agent such as `pr-review-toolkit:code-reviewer` does not know the protocol and is never edited ([domain_agents_learn_environment_never_edit_external_2026_10_11](../../architecture/decisions/domain_agents_learn_environment_never_edit_external_2026_10_11.md)); the hook blocked it once per stop and still got nothing (mem doctor: 9 stops, fields missing 100%). `the-coder` is this user's own agent name, which other plugin users may not have. The plugin enforces only what it ships; everything else is configuration.
Scope: `ai_mem/hooks/retro_check.py` DEFAULT_ROLES, `.claude-plugin/plugin.json` userConfig.retro_roles.default, `docs/reference/hooks.md`, `docs/how-to/wire-skills-and-agents.md`. Evidence: the retro_check tests. Closes todo_default_retro_roles_hardcoded_decide_after_6b_2026_10_12.

## Edges

- derived_from: [domain_agents_learn_environment_never_edit_external_2026_10_11](../../architecture/decisions/domain_agents_learn_environment_never_edit_external_2026_10_11.md)
- related: [domain_plugin_renamed_fabrica_package_and_cli_keep_names_2026_10_31](../../architecture/decisions/domain_plugin_renamed_fabrica_package_and_cli_keep_names_2026_10_31.md)
