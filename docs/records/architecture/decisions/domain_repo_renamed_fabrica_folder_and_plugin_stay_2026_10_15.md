id: domain_repo_renamed_fabrica_folder_and_plugin_stay_2026_10_15
type: domain
area: architecture
perspective: user
created: 1792061046.833732
edges: [{"target_id": "domain_fabrica_name_collision_checked_2026_10_15", "edge_type": "related"}, {"target_id": "domain_framework_named_fabrica_2026_10_10", "edge_type": "related"}, {"target_id": "domain_area_path_is_the_address_of_knowledge_2026_10_10", "edge_type": "confirms"}, {"target_id": "learning_area_move_invalidates_relative_edges_and_editable_install_2026_10_23", "edge_type": "related"}, {"target_id": "domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31", "edge_type": "related"}]
cue: You want to rename the local folder ai-mem to fabrica, or wonder why the repo name differs from folder and plugin name.
---

Decision: The GitHub repo is renamed from avataristvan/ai-mem to avataristvan/fabrica (2026-10-15, done with gh repo rename; origin is git@github.com:avataristvan/fabrica.git). The local folder ai-mem (then directly in the workspace root), the plugin name and the marketplace name ai-mem@ai-mem stay unchanged. Addendum 2026-10-23: the folder has since moved into the ai-architecture area (`..`); plugin and marketplace names are unchanged.
Why: The area path is the address of knowledge. 12 record files in other workspace areas point into this area through relative cross-area edges `../ai-mem:<id>`, so renaming the folder would leave them dangling. Keeping the plugin name avoids a breaking rename for installed users. README clone and checkout paths say fabrica; CHANGELOG and docs/how-to/migrate-to-records.md keep `cd ai-mem` because they describe existing checkouts.
Scope: repo name, README, folder and plugin naming. Evidence: commit a365d9b; grep of `ai-mem:` edges in other areas' docs/records (12 files).

Addendum 2026-10-31, in effect (done in 3c64e27, pushed): the "installed users" reason no longer holds, because unmigrated installations get their way forward from tag v1-last-upgrade-path, named in the README (domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31). The rename of folder and plugin to fabrica is planned (todo_rename_folder_and_plugin_to_fabrica_2026_10_31). The area-path reason (cross-area edges) still has to be handled when renaming.

pseudonymised for publication, 2026-10-31
