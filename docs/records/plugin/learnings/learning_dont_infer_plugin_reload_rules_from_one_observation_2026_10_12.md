id: learning_dont_infer_plugin_reload_rules_from_one_observation_2026_10_12
type: learning
topic: plugin
perspective: agent
created: 1791834833.457978
edges: [{"target_id": "learning_plugin_from_local_marketplace_loads_in_place_2026_10_12", "edge_type": "related"}]
cue: I am explaining why a plugin change is or is not visible in a running session, based on what I just saw
---

Observed: After the pull, the new plugin skill ai-mem:setup appeared in the session's skill list without a deliberate restart. The orchestrator generalised this to "skills hot-reload, hooks don't" and had to retract it.
Cause: One observation was taken as a rule. The docs describe no file watcher, only reload at session start or /reload-plugins; why the skill appeared is unexplained.
Evidence: learning_plugin_from_local_marketplace_loads_in_place_2026_10_12 (docs-based mechanics). Instead of inferring, check installed_plugins.json, known_marketplaces.json and the loading docs.
