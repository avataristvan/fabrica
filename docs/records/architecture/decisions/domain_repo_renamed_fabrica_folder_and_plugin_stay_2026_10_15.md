id: domain_repo_renamed_fabrica_folder_and_plugin_stay_2026_10_15
type: domain
area: architecture
perspective: user
created: 1792061046.833732
edges: [{"target_id": "domain_fabrica_name_collision_checked_2026_10_15", "edge_type": "related"}, {"target_id": "domain_framework_named_fabrica_2026_10_10", "edge_type": "related"}, {"target_id": "domain_area_path_is_the_address_of_knowledge_2026_10_10", "edge_type": "confirms"}]
cue: You want to rename the local folder ai-mem to fabrica, or wonder why the repo name differs from folder and plugin name.
---

Decision: The GitHub repo is renamed from avataristvan/ai-mem to avataristvan/fabrica (2026-10-15, done with gh repo rename; origin is git@github.com:avataristvan/fabrica.git). The local folder ~/workspace/ai-mem, the plugin name and the marketplace name ai-mem@ai-mem stay unchanged.
Why: The area path is the address of knowledge. 12 record files in other workspace areas point into this area through relative cross-area edges `../ai-mem:<id>`, so renaming the folder would leave them dangling. Keeping the plugin name avoids a breaking rename for installed users. README clone and checkout paths say fabrica; CHANGELOG and docs/how-to/migrate-to-records.md keep `cd ai-mem` because they describe existing checkouts.
Scope: repo name, README, folder and plugin naming. Evidence: commit a365d9b; grep of `ai-mem:` edges in other areas' docs/records (12 files).
