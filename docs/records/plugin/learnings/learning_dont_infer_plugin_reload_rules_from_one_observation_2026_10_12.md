type: learning
topic: plugin
perspective: agent
created: 1791834833.457978
cue: I am explaining why a plugin change is or is not visible in a running session, based on what I just saw
---

Observed: After the pull, the new plugin skill ai-mem:setup appeared in the session's skill list without a deliberate restart. The orchestrator generalised this to "skills hot-reload, hooks don't" and had to retract it.
Cause: One observation was taken as a rule. The docs describe no file watcher, only reload at session start or /reload-plugins; why the skill appeared is unexplained.
Evidence: [learning_plugin_from_local_marketplace_loads_in_place_2026_10_12](learning_plugin_from_local_marketplace_loads_in_place_2026_10_12.md) (docs-based mechanics). Instead of inferring, check installed_plugins.json, known_marketplaces.json and the loading docs.

## Edges

- related: [learning_plugin_from_local_marketplace_loads_in_place_2026_10_12](learning_plugin_from_local_marketplace_loads_in_place_2026_10_12.md)
